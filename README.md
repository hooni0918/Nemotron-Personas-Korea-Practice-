# 장소 스크랩 서비스 — 인터뷰 시뮬레이션

> **실제 사용자 인터뷰를 하기 전에**, AI가 만든 120명의 가상 한국인에게 우리 질문지를 미리 던져보고 **무엇이 잘 통하고 무엇은 손봐야 하는지**를 알아내는 도구입니다.

---

## 🎯 한눈에 보는 결론 (2026-05-20 기준, v3)

**우리가 만들려는 서비스**: 인스타에서 발견한 맛집·카페를 한 번에 지도에 저장하고, 친구별로 모아 함께 가는 앱.

**세 차례 시뮬레이션으로 알아낸 것**:

| | 결론 | 신뢰도 |
|---|---|---|
| ✅ | **링크 한 번으로 자동 저장된다는 핵심 가치**는 거의 모든 사람에게 통한다 | **120명 중 105명(87.5%)이 "매우 편할 것"** 응답 |
| ✅ | **"저장은 해놓고 어디 뒀는지 잊어버린다"** 는 페인은 직군·연령 무관 보편 | 64%가 "자주 헷갈린다" |
| ✅ | **"다시 찾기가 너무 번거롭다"** 페인도 보편 | 75%가 "매우 자주/자주" 겪음 |
| ⚠️ | **친구와 함께 쓰는 그룹 기능**은 마케팅·콘텐츠 직군에서 가장 반응이 강함 | A_marketer 40% vs 일반 20% |
| ⚠️ | **"내 평소 방식보다 이 앱이 낫다"** 는 확신은 약함 | 다수가 "일부 상황에서만 쓸 듯" |
| ⚠️ | **현재 경쟁자는 다른 앱이 아니라 인스타 저장함·메모장·스크린샷** | v1에서 가격 거절 사유로 일관 호소 |

### 이게 무슨 뜻이냐면

- **만들어도 된다는 신호**: 핵심 가치(자동 저장)가 거의 만장일치 긍정.
- **누구부터 잡아야 하나**: 그룹 기능에 반응 큰 **마케팅·콘텐츠 직군**부터 베타 모집.
- **무엇을 더 검증해야 하나**: "기존 방식 대비 진짜 더 좋은가"는 시뮬로는 부족 → **실제 사용자 인터뷰에서 풀어야 할 1순위 질문**.

---

## 📂 회차별 결과 보기

| 회차 | 누구한테 물었나 | 무엇이 달랐나 | 핵심 발견 |
|---|---|---|---|
| **[v3 (최신)](./results/2026-05-20_v3_nemotron-matched/SUMMARY.md)** | Nemotron 풀에서 자동 추출한 120명 | 일반 사용자 베이스라인 확인 | MVP1 87.5% 만장일치. 그룹 기능은 마케팅 직군이 가장 강함 |
| [v2](./results/2026-05-20_v2_place-scrap-personas/SUMMARY.md) | 직접 설계한 3 타겟 페르소나 × 5회 | 타겟별 반응 차이 확인 | 페르소나 의도대로 행동·페인 깔끔히 분화 |
| [v1](./results/2026-05-18_v1_baseline/SUMMARY.md) | Nemotron 랜덤 50명 | 첫 베이스라인 | 경쟁자는 다른 앱이 아니라 **현재의 무료 워크플로우** |

→ 회차마다 무엇을 바꿔서 무엇이 달라졌는지: [results/README.md](./results/README.md)

---

## 🧭 어떻게 동작하나 (비개발자용)

```
1단계: 한국인 100만 명 데이터 다운로드
       (NVIDIA가 공개한 합성 데이터 — 실제 사람 아님)
        ↓
2단계: 우리 타겟(20~39세 도시 거주 + 마케팅·IT 직군 등)으로 추리기
        ↓
3단계: AI에게 "당신은 이 사람입니다" 가르치고 우리 질문지 던지기
       (120명 × 19개 질문 = 2,280번 대화)
        ↓
4단계: 응답을 모아 "어떤 질문이 잘 통했고 어떤 건 모호했는지" 자동 분석
```

데이터 출처: NVIDIA가 한국 통계청·대법원·건보공단 데이터를 기반으로 만든 [Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (CC BY 4.0).

---

## 💰 비용

세 차례 시뮬 전체 비용 합계 **약 $1 (1,400원) 미만**. Google Gemini API 결제카드 + 1,000원 사용량 제한 등록 상태.

| 회차 | 인터뷰 수 | 응답 수 | 대략 비용 |
|---|---|---|---|
| v1 | 50명 × 11턴 | 550 | ~$0.13 |
| v2 | 3명 × 5회 × 19문 | 285 | ~$0.07 |
| v3 | 120명 × 19문 | 2,280 | ~$0.55 |

---

## ⚠️ 합성 페르소나의 한계 (꼭 알아두기)

| 한계 | 영향 |
|---|---|
| 응답은 **AI가 만든 시뮬레이션**이지 실제 사용자 의견이 아님 | "지도"로 쓰고 "결론"으로 쓰지 말 것 |
| 데이터셋에 **소득·자산 정보 없음** | **가격 민감도 검증은 부정확** → 실제 인터뷰로 풀기 |
| AI는 예의로 "괜찮다"고 답하는 경향 | 100% 동의 답은 의심부터 |
| Nemotron 페르소나에 PDF "실행형"(저장 잘 함 → 방문 잘 함) 거의 없음 | 실제 사용자 모집 때 사전 행동 기반 스크리닝 필요 |

> **결론**: 이 시뮬레이션은 **"무엇을 더 깊이 파야 할지 알려주는 지도"**이지 답이 아닙니다. 진짜 인터뷰의 사전 QA용으로만 사용.

---

<details>
<summary><strong>👨‍💻 개발자용 — 코드 셋업과 실행 방법</strong></summary>

## 파이프라인

```
00 다운로드 → 01 필터링 (또는 01b 라벨 매칭) → 02 인터뷰 → 03 분석
parquet     target.json                       responses     report.md
```

| 단계 | 입력 | 출력 |
|---|---|---|
| `00_download_dataset.py` | HF | `data/personas_sample.parquet` (~220MB) |
| `01_filter_personas.py` | `filter_config.json` | `data/target_personas.json` |
| `01b_match_personas.py` *(v3 신규)* | `v3_match_config.json` | `data/place_scrap_personas_v3.json` (라벨 포함) |
| `02_run_interview.py` | personas + `interview_questions.json` | `results/interview_responses.{csv,json}` |
| `03_analyze_results.py` | responses | `results/analysis_report.{md,json}` |

## 사용법

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # GEMINI_API_KEY 채우기

python scripts/00_download_dataset.py            # 1회만
python scripts/01_filter_personas.py             # 또는 01b_match_personas.py
python scripts/02_run_interview.py --personas data/<file>.json --repeats N
python scripts/03_analyze_results.py
```

## 다른 서비스에 적용하려면

`config/` 안의 3개 파일만 갈아끼우면 됨:
- `service_concept.md` — 검증 대상 서비스 정의
- `filter_config.json` 또는 `v3_match_config.json` — 타겟 페르소나 조건
- `interview_questions.json` — 질문지

## 회차별 결과 아카이브 구조

각 회차의 입력(`service_concept` · `interview_questions` · `personas`)과 출력(`responses` · `analysis` · `SUMMARY`)은 `results/YYYY-MM-DD_v{n}_{label}/` 폴더에 함께 박제됨.

회차 인덱스 + 다음 회차 만드는 법 + SUMMARY 템플릿: [`results/README.md`](./results/README.md)

## 자동 진단 로직 (03_analyze_results.py)

| 진단 트리거 | 의미 |
|---|---|
| Positive 80%↑ | leading question 의심 |
| Neutral 70%↑ | 모호 또는 5점 척도 응답 (분석기 한계) |
| 응답 길이 < 30자 | 관심 부족 / 질문 빈약 |
| multi_turn 거절 후 조건 풍부 | 좋은 질문 |

## 자세한 시행착오 기록

- [PROCESS.md](./PROCESS.md) — v1 초반 모델 deprecation, quota 초과 등 실패 사례
</details>

---

- 📊 데이터: [nvidia/Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (CC BY 4.0)
- 🔗 레포: https://github.com/hooni0918/Nemotron-Personas-Korea-Practice-
