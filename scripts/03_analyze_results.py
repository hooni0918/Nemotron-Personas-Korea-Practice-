"""
인터뷰 결과를 분석해 질문지의 약점을 진단한다.

핵심 진단 항목 (윤누리 블로그의 교훈을 그대로):
1. 응답 길이가 너무 짧으면 → 페르소나가 관심 없거나 질문이 빈약
2. 응답이 100% 동의/긍정으로 쏠리면 → leading question, obvious yes
3. 응답이 너무 다양해서 패턴이 없으면 → 질문이 모호
4. 멀티턴에서 거절 후 조건이 풍부하면 → 좋은 질문 (인터뷰 가이드 핵심)

출력:
- results/analysis_report.json : 질문별 통계
- results/analysis_report.md   : 사람이 읽을 수 있는 요약
"""
import json
import re
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESPONSES_PATH = ROOT / "results" / "interview_responses.json"
REPORT_JSON = ROOT / "results" / "analysis_report.json"
REPORT_MD = ROOT / "results" / "analysis_report.md"

POSITIVE_PATTERNS = [
    r"네\b", r"네,", r"좋아요", r"좋네요", r"괜찮", r"동의",
    r"그렇죠", r"맞아요", r"흥미", r"매력적", r"끌리", r"사겠",
    r"결제할", r"해볼", r"써볼",
]
NEGATIVE_PATTERNS = [
    r"아니", r"별로", r"글쎄", r"비싸", r"필요없", r"관심없",
    r"안 살", r"안 쓸", r"안 할", r"안 해", r"싫",
]


def classify_sentiment(text: str) -> str:
    pos = sum(1 for p in POSITIVE_PATTERNS if re.search(p, text))
    neg = sum(1 for p in NEGATIVE_PATTERNS if re.search(p, text))
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def analyze_question(question_id: str, responses: list) -> dict:
    """한 질문에 대한 모든 응답을 분석."""
    valid = [r for r in responses if not r["answer"].startswith("ERROR")]
    if not valid:
        return {"question_id": question_id, "n": 0, "warning": "응답 없음"}

    lengths = [len(r["answer"]) for r in valid]
    sentiments = [classify_sentiment(r["answer"]) for r in valid]
    sentiment_dist = Counter(sentiments)

    sample_answers = [r["answer"][:200] for r in valid[:5]]

    result = {
        "question_id": question_id,
        "n": len(valid),
        "avg_length": round(statistics.mean(lengths), 1),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "sentiment_distribution": dict(sentiment_dist),
        "sample_answers": sample_answers,
        "warnings": [],
    }

    # 자동 진단
    if result["avg_length"] < 30:
        result["warnings"].append("응답이 너무 짧음 → 질문이 빈약하거나 페르소나가 관심 없음")
    if sentiment_dist.get("positive", 0) / len(valid) > 0.9:
        result["warnings"].append(
            f"긍정 응답이 {sentiment_dist['positive']}/{len(valid)} → leading question 의심"
        )
    if sentiment_dist.get("neutral", 0) / len(valid) > 0.7:
        result["warnings"].append("중립 응답이 70% 이상 → 질문이 모호하거나 추상적")

    return result


def main():
    if not RESPONSES_PATH.exists():
        raise FileNotFoundError(
            f"결과 파일이 없습니다: {RESPONSES_PATH}\n"
            f"먼저 'python scripts/02_run_interview.py' 를 실행하세요."
        )

    with open(RESPONSES_PATH, encoding="utf-8") as f:
        all_results = json.load(f)

    print(f"분석 대상: 페르소나 {len(all_results)}명\n")

    # 질문×턴 단위로 응답 그룹화
    grouped: dict[str, list] = {}
    for r in all_results:
        for resp in r["responses"]:
            key = f"{resp['question_id']}-turn{resp['turn']}"
            grouped.setdefault(key, []).append(resp)

    report = {"questions": []}
    for key in sorted(grouped.keys()):
        analysis = analyze_question(key, grouped[key])
        report["questions"].append(analysis)

    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 사람이 읽기 좋은 마크다운
    md_lines = ["# 인터뷰 시뮬레이션 분석 리포트\n"]
    md_lines.append(f"- 페르소나: {len(all_results)}명")
    md_lines.append(f"- 질문×턴: {len(report['questions'])}개\n")

    for q in report["questions"]:
        md_lines.append(f"\n## {q['question_id']}")
        md_lines.append(f"- 응답 수: {q.get('n', 0)}")
        if q.get("warning"):
            md_lines.append(f"- ⚠️ {q['warning']}")
            continue
        md_lines.append(f"- 평균 응답 길이: {q['avg_length']}자")
        md_lines.append(f"- 감성 분포: {q['sentiment_distribution']}")
        if q["warnings"]:
            md_lines.append("- **진단**:")
            for w in q["warnings"]:
                md_lines.append(f"  - ⚠️ {w}")
        md_lines.append("- 응답 샘플:")
        for i, ans in enumerate(q["sample_answers"], 1):
            md_lines.append(f"  {i}. {ans}")

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"저장 완료:")
    print(f"  - {REPORT_JSON}")
    print(f"  - {REPORT_MD}")

    # 핵심 경고만 콘솔에 요약
    flagged = [q for q in report["questions"] if q.get("warnings")]
    if flagged:
        print(f"\n=== 진단 결과: 손볼 필요 있는 질문 {len(flagged)}개 ===")
        for q in flagged:
            print(f"\n[{q['question_id']}] (n={q['n']}, 평균 {q['avg_length']}자)")
            for w in q["warnings"]:
                print(f"  - {w}")
    else:
        print("\n모든 질문이 합리적인 응답 분포를 보입니다.")


if __name__ == "__main__":
    main()
