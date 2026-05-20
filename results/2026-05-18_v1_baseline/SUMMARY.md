# v1 Baseline — 2026-05-18

> 첫 시뮬레이션. 인스타 핫플 저장 앱 컨셉 + 8개 질문 11턴을 50명 합성 페르소나에게 던져 기준선 확보.

## 메타

| 항목 | 값 |
|---|---|
| 실행일 | 2026-05-18 |
| 페르소나 | 50명 (20~39세 · 수도권/광역시 · seed=42) |
| 질문 | 8개 (Q7만 멀티턴 4턴, 총 11턴) |
| 모델 | `gemini-2.5-flash-lite` |
| 총 호출 | 550건 |
| ERROR | 0건 |
| 소요 | 19분 35초 |
| Notion | [인터뷰 페르소나](https://www.notion.so/36455d5bd13f805a9ef0cd9d0721fc2f) |

## 검증하려던 가설

| # | 가설 | 결과 |
|---|---|---|
| 1 | 인스타 저장 장소를 실제 방문하는 비율은 낮을 것 | ✅ 확인 — Q2 다수가 "시간 안 맞아서/잊어서" 미방문 |
| 2 | 못 가는 가장 큰 원인은 "재발견 비용" | ✅ 확인 — Q3에서 "저장하고 까먹음", "스크롤 너무 길어 못 찾음" 다수 |
| 3 | "지도 위에 모인다"는 가치가 매력적 | ✅ Q5 Positive 56% — "검색 안 해도 됨"이 가장 강한 어필 |
| 4 | 친구 공유는 필수 기능 | ⚠️ Q6에서 자주 언급되지만 "카톡으로 충분"도 다수 — 필수지만 차별화는 약함 |
| 5 | 인스타 저장함을 떠날 만큼의 동기 | ❌ 약함 — Q7-t2에서 다수가 "지금 X로 충분" |

## 핵심 인사이트

### 🔥 가장 큰 발견: 경쟁자는 다른 앱이 아니라 **현재의 무료 워크플로우**

가격 거절 사유 다수가 "**지금도 인스타 피드/네이버 지도/메모장으로 충분**". 차별화 메시지가 "지도 뷰"만으로는 약함. **"왜 굳이 새 앱을 깔아야 하는지"의 답**이 가치 제안에 반드시 들어가야 함.

### ⚠️ 손볼 질문: Q2

중립 응답 78% (39/50). 페르소나들이 "있긴 있는데… 없긴 없는데…" 식 애매한 답이 많음 → 보기 없이 자유응답한 게 문제.

## 다음 회차로 가져갈 액션

- [ ] **Q2 V2**: "있다/없다" 명시 + 있다면 횟수, 없다면 가장 큰 이유 동시 추출
- [ ] **가격 시나리오 비교** 시뮬: 2,900 / 4,900 / 9,900 — 거절 톤이 급변하는 지점
- [ ] **Q5 응답 군집화**: "지도 뷰"가 매력적이라는 응답이 어떤 페르소나 군에서 강한지 (직업·연령·성별)
- [ ] **타겟 분할 시뮬**: 남/여 · 20대/30대 · 서울/지방 분리 실행 → 어느 군이 더 강한 페인 호소하는지

## 📂 파일 바로 보기

### 입력 (이 회차에 사용한 설정 스냅샷)

| 파일 | 내용 | 미리보기 | 다운로드 |
|---|---|---|---|
| `service_concept.md` | 검증한 서비스 컨셉 1-page | [GitHub](./service_concept.md) | [Raw](https://raw.githubusercontent.com/hooni0918/Nemotron-Personas-Korea-Practice-/main/results/2026-05-18_v1_baseline/service_concept.md) |
| `interview_questions.json` | 던진 질문 8개 (Q7 멀티턴 4턴) | [GitHub](./interview_questions.json) | [Raw](https://raw.githubusercontent.com/hooni0918/Nemotron-Personas-Korea-Practice-/main/results/2026-05-18_v1_baseline/interview_questions.json) |
| `filter_config.json` | 페르소나 필터 조건 (20~39세·수도권·seed=42) | [GitHub](./filter_config.json) | [Raw](https://raw.githubusercontent.com/hooni0918/Nemotron-Personas-Korea-Practice-/main/results/2026-05-18_v1_baseline/filter_config.json) |

### 출력 (시뮬레이션 결과)

| 파일 | 크기 | 내용 | 미리보기 | 다운로드 |
|---|---|---|---|---|
| `interview_responses.csv` | 452KB · 550행 | 페르소나×질문×턴 raw (스프레드시트 분석용) | [GitHub 표뷰](./interview_responses.csv) | [Raw](https://raw.githubusercontent.com/hooni0918/Nemotron-Personas-Korea-Practice-/main/results/2026-05-18_v1_baseline/interview_responses.csv) |
| `interview_responses.json` | 482KB | 페르소나별 전체 대화 (멀티턴 흐름 검수용) | [GitHub](./interview_responses.json) | [Raw](https://raw.githubusercontent.com/hooni0918/Nemotron-Personas-Korea-Practice-/main/results/2026-05-18_v1_baseline/interview_responses.json) |
| `analysis_report.md` | 22KB | 사람 읽기용 진단 리포트 (질문별 응답·감성·진단·샘플 5건) | [GitHub](./analysis_report.md) | [Raw](https://raw.githubusercontent.com/hooni0918/Nemotron-Personas-Korea-Practice-/main/results/2026-05-18_v1_baseline/analysis_report.md) |
| `analysis_report.json` | 24KB | 분석 raw (감성 분포·평균 길이·진단 플래그) | [GitHub](./analysis_report.json) | [Raw](https://raw.githubusercontent.com/hooni0918/Nemotron-Personas-Korea-Practice-/main/results/2026-05-18_v1_baseline/analysis_report.json) |

> **빠른 길**: 가장 자주 볼 두 개 — [analysis_report.md](./analysis_report.md) (사람용 진단) · [interview_responses.csv](./interview_responses.csv) (GitHub이 CSV를 표로 자동 렌더링)
