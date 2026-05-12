"""
필터링된 페르소나 각각에게 Gemini API로 인터뷰 질문을 던지고 응답을 수집.

- single_turn: 1회 응답
- multi_turn: 이전 응답을 컨텍스트에 쌓아가며 연속 대화

출력:
- results/interview_responses.csv  (페르소나×질문×턴 단위 행)
- results/interview_responses.json (페르소나별 전체 대화)
"""
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
PERSONAS_PATH = ROOT / "data" / "target_personas.json"
QUESTIONS_PATH = ROOT / "config" / "interview_questions.json"
RESULTS_CSV = ROOT / "results" / "interview_responses.csv"
RESULTS_JSON = ROOT / "results" / "interview_responses.json"

# gemini-2.0-flash: 무료 분당 15회, 일일 1,500회. 2.5-flash(분당 10·일일 250)보다 6배 넉넉.
# 응답 품질도 페르소나 인터뷰엔 충분.
MODEL_SINGLE_TURN = "gemini-2.0-flash"
MODEL_MULTI_TURN = "gemini-2.0-flash"

MAX_WORKERS = 5          # 동시 호출 수 (RPM 한도 고려)
MAX_RETRIES = 4          # 429(quota) 만났을 때 재시도 횟수
RETRY_BACKOFF = 20       # 첫 재시도 대기 시간(초). 매 재시도마다 2배씩 늘어남


def build_system_prompt(persona: dict, service_context: str) -> str:
    """페르소나 컬럼들을 합쳐 1인칭 롤플레잉 시스템 프롬프트를 만든다."""
    parts = []
    if persona.get("persona"):
        parts.append(persona["persona"])
    if persona.get("professional_persona"):
        parts.append(persona["professional_persona"])
    if persona.get("family_persona"):
        parts.append(persona["family_persona"])
    persona_text = "\n\n".join(parts)

    demographics = (
        f"- 성별: {persona.get('sex')}\n"
        f"- 나이: {persona.get('age')}\n"
        f"- 거주지: {persona.get('district')}\n"
        f"- 직업: {persona.get('occupation')}\n"
        f"- 학력: {persona.get('education_level')}\n"
        f"- 혼인 상태: {persona.get('marital_status')}"
    )

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
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            ".env 파일에 GEMINI_API_KEY가 없습니다.\n"
            "Google AI Studio (https://aistudio.google.com)에서 키를 발급받아 설정하세요."
        )
    genai.configure(api_key=api_key)

    with open(PERSONAS_PATH, encoding="utf-8") as f:
        personas = json.load(f)
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        q_config = json.load(f)

    questions = q_config["questions"]
    service_context = q_config.get("service_context", "")

    print(f"페르소나: {len(personas)}명")
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
