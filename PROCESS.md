# 프로젝트 진행 기록

> 인스타 핫플 저장 앱의 사용자 인터뷰 질문지를, 실제 인터뷰 전에 합성 페르소나로 미리 검증해보는 사이드 프로젝트의 진행 과정 기록.

날짜: 2026-05-13

---

## 0. 시작 배경

NVIDIA가 2026년 4월 한국인 합성 페르소나 700만 명 데이터셋(`nvidia/Nemotron-Personas-Korea`)을 공개했고, 지피터스의 윤누리님이 이를 활용해 자신의 사이드 프로젝트("로나") 가설을 검증하는 글을 썼다.

핵심 교훈 4가지가 마음에 와닿았다.

1. 헤드라인 숫자(0.3%)에 속지 말 것 — 거절 이유까지 카테고리화해야 진실이 보임
2. 직관과 정반대 결과는 가설 framing을 다시 짜라는 신호
3. AI 페르소나 시뮬레이션은 "가설 검증"보다 "질문지/제품 QA"에 강함
4. 시뮬과 실제 인터뷰는 함께 써야 의미가 있음

이 중 **3번**이 결정적이었다. 실제 인터뷰를 곧 진행할 예정인데, 인터뷰 질문지가 의도대로 답을 끌어내는지 사전에 점검할 도구가 필요했다. 합성 페르소나 시뮬레이션이 그 역할에 정확히 맞았다.

---

## 1. 무엇을 검증하는가

### 서비스 컨셉

인스타에서 가고 싶은 장소(맛집·카페·팝업 등)를 발견하면, 게시물 링크 복사 → 우리 앱 붙여넣기 한 번으로 지도 위에 자동으로 핀이 꽂히는 앱. 카테고리 분류, 친구 공유, 리마인드까지.

- **타겟**: 20~30대, 인스타 사용 익숙, 수도권·광역시 거주
- **페인포인트**: 가고 싶은 장소가 인스타 저장함/카톡/메모/지도앱에 산발적으로 흩어져서 정작 필요할 때 못 찾음
- **Must 기능 3가지**: 인스타 링크 자동 저장 + 지도 조회 / 카테고리 분류 / 친구 공유

### 검증하고 싶었던 가설

1. 저장한 장소를 실제 방문하는 비율 (페인포인트의 강도)
2. 못 가게 되는 가장 큰 원인
3. "지도 위에 모이는" 가치의 매력도
4. 친구 공유 기능이 정말 필수인가
5. 인스타 저장함을 떠날 만큼의 동기는 무엇인가

---

## 2. 데이터셋 선택과 다운로드

**`nvidia/Nemotron-Personas-Korea`** (Hugging Face, CC BY 4.0)

| 항목 | 값 |
|---|---|
| 총 페르소나 수 | 700만 |
| 파일 구조 | 9개 parquet |
| 라이선스 | CC BY 4.0 (상업적 이용 가능) |
| 시드 데이터 출처 | KOSIS, 대법원, 국민건강보험공단, 농촌경제연구원, NAVER Cloud |
| 페르소나 컬럼 | persona, professional/sports/arts/travel/culinary/family persona |
| 인구통계 컬럼 | sex, age, marital_status, education_level, occupation, district, province 등 26개 |

700만 전부 받을 필요는 없다 판단해서 **9개 중 1개(110만 명, 220MB)**만 받았다. 윤누리님도 같은 선택을 했고, 표본 크기가 너무 작아서 문제될 일은 없다.

```python
# scripts/00_download_dataset.py
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id="nvidia/Nemotron-Personas-Korea",
    filename="data/train-00000-of-00009.parquet",
    repo_type="dataset",
    ...
)
```

---

## 3. 환경 구성

```
Nemotron-Personas-Korea-Practice/
├── .env                  # GEMINI_API_KEY (gitignore)
├── .env.example          # placeholder만 (git 추적됨)
├── .gitignore
├── requirements.txt      # pandas, pyarrow, google-generativeai, dotenv, tqdm, huggingface-hub
├── README.md
├── PROCESS.md            # 이 파일
├── data/
│   ├── personas_sample.parquet     # 110만 명 raw (gitignore)
│   └── target_personas.json        # 필터링된 50명
├── scripts/
│   ├── 00_download_dataset.py
│   ├── 01_filter_personas.py
│   ├── 02_run_interview.py
│   └── 03_analyze_results.py
├── config/
│   ├── service_concept.md          # 서비스 컨셉 정리
│   ├── filter_config.json          # 페르소나 필터 조건
│   └── interview_questions.json    # 인터뷰 질문지
└── results/
    ├── interview_responses.csv     # 시뮬 결과 (행: 페르소나×질문×턴)
    ├── interview_responses.json
    └── analysis_report.md
```

각 스크립트의 역할:

| 단계 | 스크립트 | 입력 | 출력 |
|---|---|---|---|
| 0 | 데이터셋 다운로드 | (HF) | `data/personas_sample.parquet` |
| 1 | 페르소나 필터링 | `config/filter_config.json` + parquet | `data/target_personas.json` |
| 2 | Gemini 인터뷰 시뮬 | personas + questions JSON | `results/interview_responses.csv/json` |
| 3 | 응답 분석 + 진단 | responses JSON | `results/analysis_report.md` |

---

## 4. 페르소나 필터링 결과

```json
// config/filter_config.json
{
  "age_min": 20,
  "age_max": 39,
  "provinces": ["서울", "경기", "인천", "부산", "대구", "대전", "광주", "울산", "세종"],
  "sample_size": 50,
  "random_seed": 42
}
```

전체 1,111,111명에서 필터링 후 50명 추출. 분포:

- 성별: 남자 27 / 여자 23
- 평균 연령: 30.3세
- 학력: 전문대 21, 4년제 18, 고졸 7, 대학원 4
- 지역(상위 5): 경기 18, 서울 16, 인천 4, 광주 3, 부산 3

---

## 5. 인터뷰 질문지 설계

8개 질문, 총 11턴.

| Q | 유형 | 의도 |
|---|---|---|
| Q1 | 싱글턴 | 평소 인스타 장소 콘텐츠 처리 방식 |
| Q2 | 싱글턴 | 최근 한 달 내 실제 방문 사례 |
| Q3 | 싱글턴 | 저장하고도 안 가게 되는 이유 |
| Q4 | 싱글턴 | 서비스 사용 의향 (5점 척도) |
| Q5 | 싱글턴 | 매력적인 장점 |
| Q6 | 싱글턴 | 꼭 필요한 기능 |
| Q7 | **멀티턴 (4턴)** | 가격: 결제 → 조건 → 비교 앵커 → 망설임 |
| Q8 | 싱글턴 | 사례 회상 (친구 약속 불편 경험) |

선택지 질문이라도 페르소나가 "X를 선택, 이유는 Y"로 답하도록 모든 질문에 "이유를 짧게 말해주세요"를 넣었다.

시스템 프롬프트 핵심 구조:

```python
# scripts/02_run_interview.py - build_system_prompt
당신은 아래에 묘사된 인물입니다. 1인칭으로 그 인물답게 솔직하게 답하세요.
가식적으로 "좋다"라고 둘러대지 말고, 실제 그 인물이 느낄 망설임을 그대로.

[인구통계]
- 성별, 나이, 거주지, 직업, 학력, 혼인 상태

[인물 묘사]
{persona} + {professional_persona} + {family_persona}

[서비스 맥락]
{service_context}
```

페르소나 컬럼 3개(persona, professional_persona, family_persona)를 합쳐서 1인칭 롤플레잉 컨텍스트를 구성했다.

---

## 6. 시뮬 1차 시도 — 모델 deprecation

처음에 `gemini-2.0-flash-exp`로 설정해두고 돌렸다. 결과:

```
인터뷰 진행: 100%|██████| 50/50 [00:09<00:00, 5.35it/s]
⚠️  에러 발생: 400건
```

**9초 만에 끝났는데 400건 에러.** 정상이라면 분 단위로 걸려야 한다.

에러 메시지를 까보니:
```
ERROR: NotFound: 404 models/gemini-2.0-flash-exp is not found
```

실험 모델 버전이 종료됐다. 사용 가능한 모델 목록을 확인하니 `gemini-2.5-flash`, `gemini-2.0-flash` 등이 있었다. `gemini-2.5-flash`로 교체.

```python
# 변경 전
MODEL_SINGLE_TURN = "gemini-2.0-flash-exp"
# 변경 후
MODEL_SINGLE_TURN = "gemini-2.5-flash"
```

### 배운 점

LLM API는 모델 이름이 자주 바뀐다. 특히 `-exp` 접미사가 붙은 실험 모델은 어느 날 사라진다. 코드에 모델명을 하드코딩하지 말고 config로 빼는 게 좋다.

---

## 7. 시뮬 2차 시도 — Quota 초과

```
인터뷰 진행: 100%|██████| 50/50 [09:32<00:00, 11.46s/it]
⚠️  에러 발생: 385건
```

9분 32초. 모델은 진짜로 응답을 만들었다. 그러나 550회 중 **385회가 에러**, 성공은 165회.

에러 종류 단일:
```
ERROR: ResourceExhausted: 429 You exceeded your current quota
Quota exceeded for metric: generate_content_free_tier_requests
```

**원인**: `gemini-2.5-flash` 무료 한도 = 분당 10회 / 일일 250회. 우리는 동시 호출 8로 분당 ~60회를 쏘았고, 일일 한도 250도 금세 초과.

대응책으로 모델을 더 넉넉한 한도의 `gemini-2.0-flash`(분당 15 / 일일 1,500)로 다시 바꾸고, 동시 호출 8 → 5로 낮추고, 429 만나면 backoff 재시도하는 로직 추가:

```python
def _call_with_retry(callable_, *args, **kwargs):
    wait = 20
    for attempt in range(5):
        try:
            return callable_(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                time.sleep(wait)
                wait *= 2
                continue
            raise
```

테스트 한 명만 호출해보니:
```
Quota exceeded for metric: ..., limit: 0, model: gemini-2.0-flash
```

**limit: 0** ← 일일 한도를 다 쓴 게 아니라, 한도 자체가 0. `gemini-2.5-flash`로 165회 쓰면서 프로젝트 단위 무료 할당량이 소진된 듯하다. 같은 프로젝트의 다른 모델로도 spillover 차단된 상황.

### 배운 점

- **무료 티어는 본격 시뮬레이션에 부족하다.** 작은 검증(10~20명)이라면 가능하지만, 50명 이상은 일일 한도에 쉽게 걸린다.
- **모델별 한도가 프로젝트 단위로 합산**되는 듯하다. 모델을 바꿔도 우회되지 않는다.
- 본격 사용 시 **빌링 활성화** 필수. Tier 1 진입 시 50명×11턴 시뮬레이션의 실제 비용은 $0.10~0.30 수준이라 부담은 없다.

---

## 8. 보안 인시던트

진행 중에 `.env.example`에 실제 API 키를 적은 사건이 있었다.

- `.env.example`은 git 추적되는 파일 (예시 placeholder 용도)
- `.env`는 gitignore되어 git에 안 올라감

다행히 변경이 commit/push되기 전이라 GitHub에는 노출되지 않았다. 즉시 `.env`로 키를 옮기고 `.env.example`은 placeholder로 복원.

### 배운 점

키 같은 비밀 정보는 항상 `.env`에. `.env.example`은 단순히 "이런 변수 이름이 필요해" 알려주는 placeholder. 헷갈리기 쉬우니 README나 주석에 명확히 표시.

또한 채팅 도구·외부 LLM에 키를 붙여넣었다면 한 번 노출된 셈이니, 본격 사용 전에 revoke하고 새로 발급하는 게 안전하다.

---

## 9. 현재 상태

- **유효 응답 165건 보유** (50명 풀은 아님)
- 응답 샘플은 페르소나 캐릭터에 잘 맞춰 나옴
  - 예: Q1 — "카톡 '나에게 보내기'로 링크 보내놔요. 인스타 자체 저장은 다시 찾기 너무 번거롭더라고요…"
  - 예: Q2 — "딱히 방문한 곳은 없어요. 사진 보면서 '언젠가 여유 생기면' 정도…"

이 165건만 가지고도 분석은 의미가 있다. 어떤 질문에서 응답이 잘 나왔는지, 어떤 질문이 leading인지 파악해 V2 질문지를 만들 수 있다.

---

## 10. 다음 단계

### 단기 (지금~내일)

1. **165건 분석 돌리기** (`python scripts/03_analyze_results.py`)
2. 결과 보고 질문지 V2 작성
3. (선택) Google AI Studio에서 빌링 활성화 → Tier 1 진입
4. 24시간 후 quota 리셋되면 V2 질문지로 50명 본격 시뮬

### 중기 (이번 주)

5. 시뮬 결과가 안정적이면 sample_size 200~400으로 확대
6. 타겟 쪼개기 (남/여, 20대/30대, 서울/지방)
7. 가격 시나리오 비교 (2,900 / 4,900 / 9,900)

### 장기 (인터뷰 직전)

8. 시뮬에서 검증된 질문 + 시뮬이 답할 수 없는 질문(구체 경험, 비교 앵커)을 결합한 실제 인터뷰 가이드 확정
9. 실제 사용자 5~10명 인터뷰
10. 시뮬 결과와 실제 응답 패턴 비교 → 시뮬의 신뢰도 평가

---

## 부록: 코드 통계

| 파일 | 줄 수 | 역할 |
|---|---|---|
| `scripts/00_download_dataset.py` | 45 | HF 다운로드 |
| `scripts/01_filter_personas.py` | 112 | 조건 필터링 + 샘플링 |
| `scripts/02_run_interview.py` | 220 | Gemini 인터뷰 (재시도 포함) |
| `scripts/03_analyze_results.py` | 150 | 감성 분류 + 자동 진단 |

총 ~530줄. 외부 라이브러리는 pandas, pyarrow, google-generativeai, python-dotenv, tqdm, huggingface-hub 6개.

## 부록: Git 커밋 히스토리

```
87155c4  feat: 인스타 핫플 저장 앱 컨셉과 인터뷰 질문지 작성
c2a4bd8  feat: 응답 분석 및 질문지 진단 스크립트 추가
64ba462  feat: Gemini 기반 인터뷰 시뮬레이션 스크립트 추가
06c5e9b  feat: 페르소나 필터링 스크립트 추가
132284e  feat: Hugging Face 데이터셋 다운로드 스크립트 추가
80f5e54  chore: 프로젝트 초기 설정 추가
```

레포: https://github.com/hooni0918/Nemotron-Personas-Korea-Practice-

---

## 부록: 참고

- [NVIDIA Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
- [지피터스 윤누리, "엔비디아 700만 한국인 페르소나 AI 시뮬레이션 80분 돌리고 배운 4가지"](https://www.gpters.org/)
- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
