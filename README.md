# Nemotron-Personas-Korea Practice

NVIDIA의 한국인 합성 페르소나 700만 명 데이터셋(`nvidia/Nemotron-Personas-Korea`)을 활용해, **실제 사용자 인터뷰 전에 질문지를 합성 페르소나로 미리 시뮬레이션·QA**하는 사이드 프로젝트.

> 📖 시행착오·세부 의사결정은 [PROCESS.md](./PROCESS.md) 참고.

---

## 1. 무엇을 / 왜 하는가

### 핵심 문제의식

> 실제 사용자 인터뷰는 비용이 크고 한 번뿐이다. 질문이 **leading**이거나 **모호**하면 인터뷰가 끝난 뒤에야 알게 된다. 끝나기 전에 미리 검증할 수 있다면?

### 해결 가설

LLM 페르소나 시뮬레이션은 **"가설 검증"에는 약하지만 "질문지 QA"에는 강하다.** 100~400명의 합성 페르소나에게 미리 질문을 던져보면 어떤 질문이 답을 못 끌어내는지, 어떤 질문이 정답을 유도하는지 사전에 파악할 수 있다.

### 검증 대상 (예시 도메인)

이 레포의 예시는 **인스타에서 발견한 장소를 지도에 자동 저장·공유하는 앱**의 인터뷰 질문지를 검증한다. 도메인은 [`config/service_concept.md`](./config/service_concept.md) · [`config/interview_questions.json`](./config/interview_questions.json) 만 갈아끼우면 즉시 다른 서비스에도 적용 가능.

---

## 2. 전체 파이프라인

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  00 다운로드 │ → │  01 필터링   │ → │ 02 인터뷰    │ → │ 03 분석/진단 │
│  HF 데이터셋 │   │  타겟 N명    │   │  Gemini 호출 │   │  leading 탐지│
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
       │                  │                  │                   │
   parquet            target JSON       responses CSV+JSON   report MD+JSON
   (110만 raw)        (50~400명)        (페르소나×질문×턴)   (질문별 진단)
```

| # | 스크립트 | 입력 | 출력 | 라인 |
|---|---|---|---|---|
| 00 | `scripts/00_download_dataset.py` | HF `nvidia/Nemotron-Personas-Korea` | `data/personas_sample.parquet` (~220MB) | 45 |
| 01 | `scripts/01_filter_personas.py` | parquet + `config/filter_config.json` | `data/target_personas.json` | 112 |
| 02 | `scripts/02_run_interview.py` | target JSON + `config/interview_questions.json` + `.env` | `results/interview_responses.{csv,json}` | 225 |
| 03 | `scripts/03_analyze_results.py` | responses JSON | `results/analysis_report.{md,json}` | 150 |

---

## 3. 빠른 시작

### 사전 요구

- Python 3.11+
- Hugging Face 계정 (퍼블릭 데이터셋이라 토큰 불요)
- [Google AI Studio API Key](https://aistudio.google.com/apikey) — Gemini

### 셋업

```bash
# 1) 가상환경
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2) API 키
cp .env.example .env
# .env 열어서 GEMINI_API_KEY=<your_key> 채우기
```

### 실행 (4단계)

```bash
python scripts/00_download_dataset.py   # 1회만. 220MB parquet 다운로드
python scripts/01_filter_personas.py    # 50명(기본) 추출 → target_personas.json
python scripts/02_run_interview.py      # Gemini 호출. 50명×11턴 ≈ 1~3분 (Tier 1)
python scripts/03_analyze_results.py    # 응답 분석 + 진단 리포트 생성
```

### 결과 확인

```bash
open results/analysis_report.md         # 사람용 요약 (질문별 응답/진단)
open results/interview_responses.csv    # 전체 응답 raw (스프레드시트 분석용)
```

---

## 4. 디렉토리 구조

```
.
├── .env                       # GEMINI_API_KEY (gitignore)
├── .env.example               # placeholder
├── requirements.txt           # pandas, pyarrow, google-generativeai, dotenv, tqdm, huggingface-hub
├── README.md                  # 이 파일
├── PROCESS.md                 # 시행착오·교훈 기록
├── config/
│   ├── service_concept.md     # 검증 대상 서비스 1-page 정의 (편집 가능)
│   ├── filter_config.json     # 타겟 페르소나 조건
│   └── interview_questions.json   # 질문지 (single/multi turn)
├── data/
│   ├── personas_sample.parquet     # 110만 명 raw (gitignore)
│   └── target_personas.json        # 필터링 결과 N명
├── scripts/
│   ├── 00_download_dataset.py
│   ├── 01_filter_personas.py
│   ├── 02_run_interview.py
│   └── 03_analyze_results.py
└── results/
    ├── interview_responses.csv     # 페르소나×질문×턴 행 (분석 용도)
    ├── interview_responses.json    # 페르소나별 전체 대화 (검수 용도)
    ├── analysis_report.json        # 진단 raw
    └── analysis_report.md          # 진단 요약 (사람용)
```

---

## 5. 핵심 구현 노트

### 페르소나 데이터 (Nemotron-Personas-Korea)

| 항목 | 값 |
|---|---|
| 총 페르소나 | 700만 (9개 parquet 중 1개 = 110만만 사용) |
| 라이선스 | CC BY 4.0 (상업적 이용 가능) |
| 시드 출처 | KOSIS, 대법원, 국민건강보험공단, NAVER Cloud 등 |
| **인구통계 컬럼** | `sex`, `age`, `marital_status`, `education_level`, `occupation`, `district`, `province` 외 26개 |
| **페르소나 컬럼** | `persona`, `professional_persona`, `family_persona`, `culinary_persona`, `travel_persona`, `sports_persona`, `arts_persona` |

**⚠️ 데이터셋에 없는 것**: 소득·자산 등 경제 지표. → **가격 질문은 시뮬에서 정확히 검증 불가**, 실제 인터뷰로 보완 필요.

### `01_filter_personas.py` — 필터 조건

`config/filter_config.json` 한 파일이 모든 필터를 관장. null이면 해당 조건 무시.

```jsonc
{
  "age_min": 20, "age_max": 39,        // 연령 범위
  "sex": null,                          // "남자" / "여자" / null
  "education_levels": null,             // ["4년제 대학교", ...] 또는 null
  "occupation_keywords": null,          // ["엔지니어", ...] 직업명 부분일치
  "provinces": ["서울", "경기", ...],   // 시도 단위
  "marital_status": null,               // "미혼" / "배우자있음" / "이혼" / "사별"
  "metro_only": false,
  "sample_size": 50,                    // 추출할 N
  "random_seed": 42                     // 재현성
}
```

### `02_run_interview.py` — 인터뷰 시뮬레이션

핵심 설계:

| 항목 | 값 / 설계 의도 |
|---|---|
| 모델 | `gemini-2.5-flash-lite` (현역 최저가, $0.10/$0.40 per 1M tokens) |
| 동시 호출 | `MAX_WORKERS = 5` (RPM 한도 고려) |
| 재시도 | 429 발생 시 backoff (20→40→80→160초, 4회) 후 ERROR 기록 |
| 시스템 프롬프트 | 페르소나 3종(persona+professional+family) 결합 + 1인칭 롤플레잉 강제 |
| 답변 톤 통제 | *"가식적 '좋다'로 둘러대지 말고 솔직한 망설임을 표현"* 명시 |
| 답변 길이 | 2~4문장 권장 (페르소나가 길게 설교하지 못하게) |

**시스템 프롬프트 구조** (`build_system_prompt`):

```
당신은 아래에 묘사된 인물입니다. 1인칭으로 그 인물답게 솔직하게…

[인물 정보]
- 성별 / 나이 / 거주지 / 직업 / 학력 / 혼인 상태

[인물 묘사]
{persona}  +  {professional_persona}  +  {family_persona}

[서비스 맥락]
{interview_questions.json 의 service_context}
```

**질문 유형** (`interview_questions.json`):

```jsonc
{
  "service_context": "...",
  "questions": [
    { "id": "Q1", "type": "single_turn", "text": "..." },          // 1회 응답
    { "id": "Q7", "type": "multi_turn",                             // 연쇄 대화
      "turns": [ "1턴 질문...", "2턴 follow-up...", "..." ] }
  ]
}
```

multi_turn은 `model.start_chat()`으로 이전 응답을 컨텍스트에 쌓아가며 진행 → **가격 거절 이유, 조건부 결제 의향** 같은 깊이 있는 추출에 사용.

### `03_analyze_results.py` — 자동 진단

질문별 응답을 모아 4가지 진단 패턴 자동 검출:

| 진단 트리거 | 의미 | 액션 |
|---|---|---|
| 응답 길이 평균 < 30자 | 페르소나가 관심 없거나 질문 빈약 | 질문 구체화 |
| 긍정 sentiment > 80% | **leading question 의심** | 단어/구조 다시 짜기 |
| neutral sentiment > 70% | 질문이 모호·추상적 | "예시 보기" 추가 |
| multi_turn에서 거절 후 조건 풍부 | **좋은 질문** | 인터뷰 가이드에 그대로 사용 |

sentiment는 한국어 키워드 매칭(`POSITIVE_PATTERNS` / `NEGATIVE_PATTERNS`)로 분류 — 정밀하진 않지만 거시 패턴 진단에는 충분.

---

## 6. 출력 포맷

### `results/interview_responses.csv`

스프레드시트·pandas 분석용. 페르소나×질문×턴 단위 1행:

| 열 | 설명 |
|---|---|
| `uuid` | 페르소나 고유 ID |
| `age`, `sex`, `occupation`, `district` | 인구통계 (분석 그룹핑용) |
| `question_id` | Q1~Q8 |
| `type` | `single_turn` / `multi_turn` |
| `turn` | 1부터 시작. ERROR 시 0 |
| `question` | 질문 원문 |
| `answer` | 페르소나 응답 (실패 시 `ERROR: ...`) |

### `results/interview_responses.json`

페르소나별 전체 대화 묶음. 멀티턴 흐름 검수 용도.

### `results/analysis_report.md`

질문별 응답 수, 평균 길이, 감성 분포, 자동 진단, 응답 샘플 5건.

---

## 7. 비용·한도

### 모델 가격 (Standard tier, 1M tokens 기준)

| 모델 | Input | Output | 비고 |
|---|---|---|---|
| **gemini-2.5-flash-lite** | $0.10 | $0.40 | **현재 사용** — 현역 최저가 |
| gemini-2.0-flash | $0.10 | $0.40 | 동급, deprecation 위험 |
| gemini-2.5-flash | $0.30 | $2.50 | 6배 비쌈 |

### 실제 비용 추산 (이 프로젝트 기준)

호출당 input ~1,400 / output ~250 토큰 가정.

| 페르소나 × 턴 | 호출 수 | 예상 비용 |
|---|---|---|
| 50 × 11 | 550 | **~$0.13** (≈ 180원) |
| 200 × 11 | 2,200 | ~$0.52 (≈ 720원) |
| 500 × 11 | 5,500 | ~$1.30 (≈ 1,800원) |

### Tier 한도 (요약)

| Tier | RPM | 사용 시점 |
|---|---|---|
| Free | ~15 | 10명 이하 소규모 검증만 권장 |
| Tier 1 (결제카드 등록) | 1,000+ | 50~500명 시뮬레이션 안정적 |

> 💡 결제 카드 등록 + Google Cloud 콘솔에서 사용량 cap(예: $1) 설정해두면 안전. 실제 비용은 cap의 1/10 미만이라 한도 도달 가능성 거의 0.

---

## 8. 알려진 한계

| 한계 | 영향 | 대응 |
|---|---|---|
| 데이터셋에 **소득/자산 정보 없음** | 가격 민감도 검증 부정확 | 가격은 실제 인터뷰로 확정 |
| LLM은 **예의로 "OK"** 답하는 경향 | 100% 동의 결과는 신뢰 X | leading 진단으로 자동 필터 |
| 페르소나 톤이 **다 비슷한 한국어** | 세대·지역 다양성 다소 약함 | 결과는 "지도"로만 사용 |
| 무료 티어 한도가 매우 빡빡 | 50명 시뮬도 무료로는 어려움 | 결제 등록 권장 |
| Gemini 모델 deprecation 빈번 | 코드 수정 필요 | 모델명을 상수로 분리 (`02_run_interview.py:30`) |

---

## 9. 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `404 models/... not found` | 모델 이름 오래됨 | `gemini-2.5-flash-lite` 등 최신으로 교체 |
| `429 ResourceExhausted` | 무료 한도 초과 | 결제 등록 또는 페르소나 수 축소 |
| 진행률이 0%에서 멈춤 | tqdm 출력 버퍼링 | `PYTHONUNBUFFERED=1` + `python -u` 옵션 |
| `.env.example`에 실수로 진짜 키 기입 | 헷갈림 | 즉시 키 revoke → `.env`로 옮기기 |
| ERROR 응답만 가득 | 모델 fallback 실패 | output 파일에서 ERROR 메시지 grep |

---

## 10. 다른 서비스에 재사용하려면

1. `config/service_concept.md` — 서비스 한 줄 설명 + 타겟 다시 작성
2. `config/filter_config.json` — 타겟 페르소나 조건 수정 (연령·지역·성별·직업)
3. `config/interview_questions.json` — 검증할 질문지 갈아끼우기
4. `02_run_interview.py` 코드 변경 **불필요**
5. `python scripts/01_filter_personas.py && python scripts/02_run_interview.py && python scripts/03_analyze_results.py`

---

## 11. 참고

- **데이터셋**: [nvidia/Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (CC BY 4.0)
- **원본 영감**: 지피터스 윤누리 — "엔비디아 700만 한국인 페르소나 AI 시뮬레이션 80분 돌리고 배운 4가지"
- **Gemini API**: [pricing](https://ai.google.dev/pricing) · [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- **레포**: https://github.com/hooni0918/Nemotron-Personas-Korea-Practice-

---

## 라이선스 / 면책

- 코드: 자유 사용
- 데이터셋: CC BY 4.0 (NVIDIA 출처 명시 필요)
- 합성 페르소나의 응답은 **시뮬레이션 결과**이며 실제 사용자 의견이 아님. 의사결정은 반드시 실제 사용자 인터뷰와 함께 진행.
