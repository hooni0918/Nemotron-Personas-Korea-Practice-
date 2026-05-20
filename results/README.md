# Interview Runs

회차별 인터뷰 시뮬레이션 결과 아카이브. **각 회차는 독립된 폴더**에 입력(`service_concept` · `interview_questions` · `filter_config`)과 출력(`responses` · `analysis`)을 함께 박제해, 나중에 무엇을 바꿔서 어떤 결과가 나왔는지 비교할 수 있게 했음.

## 회차 인덱스

| 회차 | 날짜 | 라벨 | 페르소나 | 질문×턴 | 핵심 발견 |
|---|---|---|---|---|---|
| [v1](./2026-05-18_v1_baseline/SUMMARY.md) | 2026-05-18 | baseline | 50명 | 8×11 | 경쟁자는 다른 앱이 아니라 **현재의 무료 워크플로우** (인스타+메모+네이버지도). Q2 모호 진단. |

## 회차별 파일 빠른 접근

### v1 baseline (2026-05-18)

- 📄 [**SUMMARY.md**](./2026-05-18_v1_baseline/SUMMARY.md) — 회차 요약 (가설·인사이트·다음 액션)
- **입력 스냅샷**
  - [service_concept.md](./2026-05-18_v1_baseline/service_concept.md) — 검증한 서비스 컨셉
  - [interview_questions.json](./2026-05-18_v1_baseline/interview_questions.json) — 던진 질문지
  - [filter_config.json](./2026-05-18_v1_baseline/filter_config.json) — 페르소나 필터 조건
- **출력**
  - [analysis_report.md](./2026-05-18_v1_baseline/analysis_report.md) — 사람용 진단 리포트 (가장 자주 볼 파일)
  - [interview_responses.csv](./2026-05-18_v1_baseline/interview_responses.csv) — 550행 raw 응답 (GitHub이 표로 렌더링)
  - [interview_responses.json](./2026-05-18_v1_baseline/interview_responses.json) — 페르소나별 대화 묶음
  - [analysis_report.json](./2026-05-18_v1_baseline/analysis_report.json) — 분석 raw

## 다음 회차 만드는 법

1. **폴더 생성**: `results/YYYY-MM-DD_v{n}_{label}/`
   - 라벨은 그 회차의 핵심 변경을 한 단어로 (`baseline`, `q2-fixed`, `price-3way` 등)
2. **입력 스냅샷 복사**:
   ```bash
   RUN=results/2026-05-20_v2_q2-fixed
   mkdir -p "$RUN"
   cp config/service_concept.md config/interview_questions.json config/filter_config.json "$RUN/"
   ```
3. **인터뷰 실행**:
   ```bash
   python scripts/02_run_interview.py
   python scripts/03_analyze_results.py
   mv results/interview_responses.{csv,json} results/analysis_report.{md,json} "$RUN/"
   ```
4. **SUMMARY.md 작성** — 아래 템플릿 사용
5. **이 README의 인덱스 표에 한 줄 추가**
6. 커밋 푸시

## SUMMARY.md 템플릿

```markdown
# v{n} {label} — YYYY-MM-DD

> 이번 회차에서 무엇을·왜 바꿨는지 한 줄.

## 메타
| 항목 | 값 |
|---|---|
| 실행일 | YYYY-MM-DD |
| 페르소나 | N명 (필터 조건 요약) |
| 질문 | N개 (M턴) |
| 모델 | ... |
| 총 호출 | N건 |
| ERROR | N건 |
| 소요 | M분 S초 |

## 이전 회차 대비 변경점
- [v{n-1}](../YYYY-MM-DD_v{n-1}_*/SUMMARY.md) 대비 무엇을 어떻게 바꿨고, 왜?

## 검증하려던 가설
| # | 가설 | 결과 |
|---|---|---|
| 1 | ... | ✅ / ⚠️ / ❌ |

## 핵심 인사이트
### 🔥 가장 큰 발견
...

### ⚠️ 손볼 질문 / 다음 가설

## 다음 회차로 가져갈 액션
- [ ] ...

## 박제된 입력 / 출력
(이 폴더 안의 파일 목록)
```

## 결과 비교 팁

회차 간 비교를 빠르게 보려면:

```bash
# Q1 응답 길이가 회차별로 어떻게 변했는지
for f in results/*/analysis_report.json; do
  echo "$f"
  jq '.questions[] | select(.question_id=="Q1") | {n, avg_length}' "$f"
done
```
