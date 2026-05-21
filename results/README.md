# 인터뷰 회차 모음

회차별 결과 폴더 모음. **각 회차의 입력(서비스 컨셉·질문지·페르소나)과 출력(응답·분석·요약)이 같이 박제**되어 있어, 어떤 변화가 어떤 결과를 낳았는지 한눈에 비교할 수 있습니다.

> 회차를 가로지르는 종합 인사이트는 [`INSIGHTS.md`](../INSIGHTS.md) 참고.

---

## 📅 회차 인덱스

| 회차 | 날짜 | 무엇이 달랐나 | 페르소나 | 응답 수 | 한 줄 결론 |
|---|---|---|---|---|---|
| **[v3](./2026-05-20_v3_nemotron-matched/SUMMARY.md)** | 2026-05-20 | Nemotron 풀에서 직업 매칭으로 120명 자동 추출 | 120명 (A40·B30·C50) × 1회 | 2,280 | **120명 중 105명(87.5%)이 "매우 편할" — MVP1 만장일치 검증** |
| [v2](./2026-05-20_v2_place-scrap-personas/SUMMARY.md) | 2026-05-20 | 사용자 직접 설계한 PDF 3 타겟 페르소나 + Q1-Q20 종합 질문지 | 3 타입 × 5회 = 15 | 285 | PDF 의도한 페르소나 행동·페인 차이가 LLM에서 깔끔히 분화 |
| [v1](./2026-05-18_v1_baseline/SUMMARY.md) | 2026-05-18 | 첫 베이스라인. Nemotron 랜덤 50명 + 8질문 | 50명 | 165 (유효) | 경쟁자는 다른 앱이 아니라 **현재의 무료 워크플로우** (인스타 저장함·메모·스크린샷) |

---

## 📂 각 회차 파일 빠르게 보기

비개발자가 먼저 봐야 할 파일은 **SUMMARY.md**. 그 안에서 자세한 데이터로 펼쳐 들어갑니다.

### v3 — Nemotron 매칭 120명 (2026-05-20)

- 🟢 [**SUMMARY.md — 한 줄 결론과 5가지 발견**](./2026-05-20_v3_nemotron-matched/SUMMARY.md)
- 📊 [`analysis_report.md`](./2026-05-20_v3_nemotron-matched/analysis_report.md) — 자동 진단 + 응답 샘플
- 📑 [`interview_responses.csv`](./2026-05-20_v3_nemotron-matched/interview_responses.csv) — 2,280행 응답 (GitHub이 표로 자동 렌더링)
- 📋 입력 스냅샷: [`v3_match_config.json`](./2026-05-20_v3_nemotron-matched/v3_match_config.json) · [`place_scrap_personas_v3.json`](./2026-05-20_v3_nemotron-matched/place_scrap_personas_v3.json) · [`interview_questions.json`](./2026-05-20_v3_nemotron-matched/interview_questions.json) · [`service_concept.md`](./2026-05-20_v3_nemotron-matched/service_concept.md)

### v2 — 사용자 설계 3 페르소나 (2026-05-20)

- 🟢 [**SUMMARY.md — 페르소나 타입별 분화 검증**](./2026-05-20_v2_place-scrap-personas/SUMMARY.md)
- 📊 [`analysis_report.md`](./2026-05-20_v2_place-scrap-personas/analysis_report.md)
- 📑 [`interview_responses.csv`](./2026-05-20_v2_place-scrap-personas/interview_responses.csv) — 285행
- 📋 입력: [`place_scrap_personas.json`](./2026-05-20_v2_place-scrap-personas/place_scrap_personas.json) · [`interview_questions.json`](./2026-05-20_v2_place-scrap-personas/interview_questions.json) · [`service_concept.md`](./2026-05-20_v2_place-scrap-personas/service_concept.md)

### v1 — 첫 베이스라인 (2026-05-18)

- 🟢 [**SUMMARY.md — 첫 시뮬 결과와 시행착오**](./2026-05-18_v1_baseline/SUMMARY.md)
- 📊 [`analysis_report.md`](./2026-05-18_v1_baseline/analysis_report.md)
- 📑 [`interview_responses.csv`](./2026-05-18_v1_baseline/interview_responses.csv) — 550행 (대부분 API 쿼터 에러)
- 📋 입력: [`interview_questions.json`](./2026-05-18_v1_baseline/interview_questions.json) · [`service_concept.md`](./2026-05-18_v1_baseline/service_concept.md) · [`filter_config.json`](./2026-05-18_v1_baseline/filter_config.json)

---

<details>
<summary><strong>👨‍💻 개발자용 — 새 회차 만드는 법</strong></summary>

### 1. 폴더 생성
```bash
RUN=results/$(date +%F)_v4_{label}
mkdir -p "$RUN"
```
라벨은 그 회차의 핵심 변경을 한 단어로 (`q2-fixed`, `price-3way`, `multi-turn-deep` 등).

### 2. 입력 스냅샷 복사
```bash
cp config/service_concept.md config/interview_questions.json \
   config/v3_match_config.json data/place_scrap_personas_v3.json "$RUN/"
```

### 3. 인터뷰 + 분석 실행
```bash
python scripts/02_run_interview.py --personas data/<file>.json --repeats N
python scripts/03_analyze_results.py
mv results/interview_responses.{csv,json} results/analysis_report.{md,json} "$RUN/"
```

### 4. SUMMARY.md 작성

가장 최신인 [v3 SUMMARY.md](./2026-05-20_v3_nemotron-matched/SUMMARY.md)의 구조를 그대로 따라가는 게 가장 빠릅니다:
- **한 줄 결론** 맨 위
- **누구한테 무엇을 물었나** (간단)
- **핵심 발견 N가지** (각 발견에 표 + 💡 시사점)
- **페르소나가 한 말** (직접 인용 2~3개)
- **다음에 해야 할 것** (비즈니스 액션 / 다음 회차 액션 분리)
- **결과 읽을 때 주의할 점**
- **기술 메타 데이터** (펼치기)
- **raw 데이터 보기** (파일 링크)

### 5. 인덱스 표·INSIGHTS·메인 README 갱신

- `results/README.md`의 회차 인덱스 표에 한 줄 추가
- `INSIGHTS.md`에 회차 가로지르는 패턴 업데이트
- 메인 `README.md`의 "최신 회차 빠른 접근" 블록 v3 → v4로 교체

### 6. 파일 단위로 잘게 커밋

```bash
git add results/<run>/v3_match_config.json && git commit -m "v4 archive: snapshot v3_match_config.json"
git add results/<run>/<personas>.json && git commit -m "v4 archive: snapshot personas"
# … 파일별로
```

### 7. 푸시 + PR

```bash
git push -u origin v4/<branch>
gh pr create --title "v4: <한 줄 요약>" --body "<SUMMARY 인용>"
```

### 회차 간 빠른 비교 jq

```bash
for f in results/*/analysis_report.json; do
  echo "$f"
  jq '.questions[] | select(.question_id=="Q1") | {n, avg_length}' "$f"
done
```

</details>
