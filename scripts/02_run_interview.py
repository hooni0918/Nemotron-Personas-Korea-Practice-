"""
필터링된 페르소나 각각에게 Gemini API로 인터뷰 질문을 던지고 응답을 수집.

- single_turn: 1회 응답
- multi_turn: 이전 응답을 컨텍스트에 쌓아가며 연속 대화

출력:
- results/interview_responses.csv  (페르소나×질문×턴 단위 행)
- results/interview_responses.json (페르소나별 전체 대화)
"""
import argparse
import csv
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm

ROOT = Path(__file__).parent.parent
DEFAULT_PERSONAS_PATH = ROOT / "data" / "target_personas.json"
QUESTIONS_PATH = ROOT / "config" / "interview_questions.json"
RESULTS_CSV = ROOT / "results" / "interview_responses.csv"
RESULTS_JSON = ROOT / "results" / "interview_responses.json"

# gemini-2.5-flash-lite: 현역 모델 중 최저가($0.10/$0.40 per 1M tokens).
# 페르소나 인터뷰 품질엔 충분하고 비용·한도 측면에서 가성비 최고.
MODEL_SINGLE_TURN = "gemini-2.5-flash-lite"
MODEL_MULTI_TURN = "gemini-2.5-flash-lite"

MAX_WORKERS = 5          # 동시 호출 수 (RPM 한도 고려)
MAX_RETRIES = 4          # 429(quota) 만났을 때 재시도 횟수
RETRY_BACKOFF = 20       # 첫 재시도 대기 시간(초). 매 재시도마다 2배씩 늘어남


def build_system_prompt(persona: dict, service_context: str) -> str:
    """페르소나 필드를 1인칭 롤플레잉 시스템 프롬프트로 합친다.

    두 가지 페르소나 스키마를 모두 지원한다:
    - Nemotron 스타일: persona / professional_persona / family_persona + 인구통계 컬럼들
    - 커스텀 스타일(v2 이후): summary / behaviors / pain_points / needs / trigger + name·motto
    페르소나에 어떤 키가 있느냐에 따라 자연스럽게 분기된다.
    """
    # 공통 인구통계 (있는 것만)
    demo_lines = []
    if persona.get("name"):
        demo_lines.append(f"- 이름: {persona['name']}")
    if persona.get("sex"):
        demo_lines.append(f"- 성별: {persona['sex']}")
    if persona.get("age") is not None:
        demo_lines.append(f"- 나이: {persona['age']}")
    if persona.get("district"):
        demo_lines.append(f"- 거주지: {persona['district']}")
    if persona.get("occupation"):
        demo_lines.append(f"- 직업: {persona['occupation']}")
    if persona.get("education_level"):
        demo_lines.append(f"- 학력: {persona['education_level']}")
    if persona.get("marital_status"):
        demo_lines.append(f"- 혼인 상태: {persona['marital_status']}")
    demographics = "\n".join(demo_lines)

    # 인물 묘사 — 커스텀 스키마가 있으면 그쪽을, 없으면 Nemotron 컬럼을 사용
    if persona.get("summary") or persona.get("behaviors") or persona.get("pain_points"):
        sections = []
        if persona.get("type_label"):
            sections.append(f"[타입] {persona['type_label']} ({persona.get('type_summary', '')})".strip())
        if persona.get("motto"):
            sections.append(f"[한 줄 멘트] \"{persona['motto']}\"")
        if persona.get("summary"):
            sections.append(f"[요약]\n{persona['summary']}")
        if persona.get("behaviors"):
            bullets = "\n".join(f"- {b}" for b in persona["behaviors"])
            sections.append(f"[주요 행동]\n{bullets}")
        if persona.get("pain_points"):
            bullets = "\n".join(f"- {p}" for p in persona["pain_points"])
            sections.append(f"[페인포인트]\n{bullets}")
        if persona.get("needs"):
            bullets = "\n".join(f"- {n}" for n in persona["needs"])
            sections.append(f"[서비스 니즈]\n{bullets}")
        if persona.get("trigger"):
            sections.append(f"[사용 트리거] {persona['trigger']}")
        persona_text = "\n\n".join(sections)
    else:
        parts = []
        for key in ("persona", "professional_persona", "family_persona"):
            if persona.get(key):
                parts.append(persona[key])
        persona_text = "\n\n".join(parts)

    return f"""당신은 아래에 묘사된 인물입니다. 1인칭으로, 그 인물의 성격과 처지에 맞게 솔직하게 답하세요.
가식적으로 "좋다", "괜찮다"라고 둘러대지 말고, 실제로 그 인물이 느낄 만한 솔직한 감정과 망설임을 그대로 표현하세요.
모르거나 관심 없는 주제라면 "잘 모르겠다", "별로 관심 없다"라고 솔직히 답해도 됩니다.

[인물 정보]
{demographics}

[인물 묘사]
{persona_text}

[서비스 맥락]
지금 어떤 인터뷰어가 출시 예정인 서비스에 대해 당신의 의견을 듣고 싶어합니다. 서비스는 다음과 같습니다:

{service_context}

답변은 2~4문장 정도로 간결하게, 그 인물답게 말하세요."""


def _call_with_retry(callable_, *args, **kwargs):
    """레이트 리밋(429)에 부딪히면 backoff하며 재시도. 다른 에러는 즉시 raise."""
    wait = RETRY_BACKOFF
    last_exc = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return callable_(*args, **kwargs)
        except Exception as e:
            last_exc = e
            msg = str(e).lower()
            if "429" in str(e) or "quota" in msg or "resourceexhausted" in msg.replace(" ", ""):
                if attempt < MAX_RETRIES:
                    time.sleep(wait)
                    wait *= 2
                    continue
            raise
    raise last_exc  # 도달 안 함


def interview_single_persona(persona: dict, questions: list, service_context: str) -> dict:
    """한 페르소나에 대해 모든 질문 실행."""
    system_prompt = build_system_prompt(persona, service_context)

    result = {
        "uuid": persona.get("uuid"),
        "age": persona.get("age"),
        "sex": persona.get("sex"),
        "occupation": persona.get("occupation"),
        "district": persona.get("district"),
        "responses": [],
    }

    for q in questions:
        q_id = q["id"]
        q_type = q.get("type", "single_turn")

        try:
            if q_type == "single_turn":
                model = genai.GenerativeModel(
                    MODEL_SINGLE_TURN,
                    system_instruction=system_prompt,
                )
                resp = _call_with_retry(model.generate_content, q["text"])
                result["responses"].append({
                    "question_id": q_id,
                    "type": "single_turn",
                    "turn": 1,
                    "question": q["text"],
                    "answer": resp.text.strip() if resp.text else "",
                })

            elif q_type == "multi_turn":
                model = genai.GenerativeModel(
                    MODEL_MULTI_TURN,
                    system_instruction=system_prompt,
                )
                chat = model.start_chat(history=[])
                for turn_idx, turn_text in enumerate(q["turns"], start=1):
                    resp = _call_with_retry(chat.send_message, turn_text)
                    result["responses"].append({
                        "question_id": q_id,
                        "type": "multi_turn",
                        "turn": turn_idx,
                        "question": turn_text,
                        "answer": resp.text.strip() if resp.text else "",
                    })

        except Exception as e:
            # 재시도 후에도 실패하면 그 질문만 ERROR로 기록하고 다음으로
            result["responses"].append({
                "question_id": q_id,
                "type": q_type,
                "turn": 0,
                "question": "[ERROR]",
                "answer": f"ERROR: {type(e).__name__}: {e}",
            })

    return result


def save_results(all_results: list):
    RESULTS_CSV.parent.mkdir(exist_ok=True)

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    with open(RESULTS_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "uuid", "age", "sex", "occupation", "district",
            "question_id", "type", "turn", "question", "answer",
        ])
        for r in all_results:
            for resp in r["responses"]:
                writer.writerow([
                    r["uuid"], r["age"], r["sex"], r["occupation"], r["district"],
                    resp["question_id"], resp["type"], resp["turn"],
                    resp["question"], resp["answer"],
                ])

    print(f"\n저장 완료:")
    print(f"  - {RESULTS_CSV}")
    print(f"  - {RESULTS_JSON}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--personas",
        default=str(DEFAULT_PERSONAS_PATH),
        help="페르소나 JSON 파일 경로 (기본: data/target_personas.json)",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="페르소나당 반복 실행 횟수 (소수 페르소나 시뮬에서 응답 다양성 확보용)",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            ".env 파일에 GEMINI_API_KEY가 없습니다.\n"
            "Google AI Studio (https://aistudio.google.com)에서 키를 발급받아 설정하세요."
        )
    genai.configure(api_key=api_key)

    with open(args.personas, encoding="utf-8") as f:
        base_personas = json.load(f)
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        q_config = json.load(f)

    # 반복 실행: 페르소나 N명을 R회씩 → 각 인스턴스에 -r{i} suffix 붙여 별도 응답으로 기록
    personas = []
    for p in base_personas:
        for r in range(args.repeats):
            instance = dict(p)
            if args.repeats > 1:
                instance["uuid"] = f"{p.get('uuid', 'persona')}-r{r+1}"
            personas.append(instance)

    questions = q_config["questions"]
    service_context = q_config.get("service_context", "")

    print(f"페르소나 파일: {args.personas}")
    print(f"페르소나: {len(base_personas)}명 × {args.repeats}회 = {len(personas)} 인터뷰")
    print(f"질문: {len(questions)}개 ({sum(len(q.get('turns', [q.get('text')])) for q in questions)}턴)")
    print(f"모델: single={MODEL_SINGLE_TURN}, multi={MODEL_MULTI_TURN}")
    print(f"동시 호출: {MAX_WORKERS}\n")

    all_results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(interview_single_persona, p, questions, service_context): p
            for p in personas
        }
        for fut in tqdm(as_completed(futures), total=len(futures), desc="인터뷰 진행"):
            all_results.append(fut.result())

    save_results(all_results)

    # 간단한 에러 통계
    error_count = sum(
        1 for r in all_results for resp in r["responses"]
        if resp["answer"].startswith("ERROR")
    )
    if error_count:
        print(f"\n⚠️  에러 발생: {error_count}건")


if __name__ == "__main__":
    main()
