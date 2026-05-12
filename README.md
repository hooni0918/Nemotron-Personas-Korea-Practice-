# Nemotron-Personas-Korea Practice

NVIDIA Nemotron-Personas-Korea(한국인 합성 페르소나 700만 명)로 인터뷰 질문지를 시뮬레이션 테스트하는 사이드 프로젝트.

## 무엇을 하는가

실제 사용자 인터뷰 전에, 작성한 인터뷰 질문이 의도대로 답을 끌어내는지 합성 페르소나 100~400명에게 먼저 던져본다. 어떤 질문이 leading인지, 어떤 질문이 모호한지, 어떤 가설은 multi-turn으로 깊이 파야 하는지를 미리 확인한다.

## 진행 흐름

```
[Phase 1] 환경 구축
   ↓
[Phase 2] 서비스 컨셉 + 질문지 초안 작성  ← 대화로 정리
   ↓
[Phase 3] 시뮬레이션 실행
   ↓
[Phase 4] 결과 분석 → 질문지 V2 → 실제 인터뷰
```

## 사용 방법

### 1. 환경 준비

```bash
# 가상환경
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# API 키 (Google AI Studio: https://aistudio.google.com)
cp .env.example .env
# .env 파일을 열어 GEMINI_API_KEY 값을 채운다
```

### 2. 데이터셋 다운로드 (한 번만)

```bash
python scripts/00_download_dataset.py
```

110만 명 분량 parquet 1개 파일(~220MB)이 `data/personas_sample.parquet`에 저장된다.

### 3. 서비스 컨셉 & 질문지 작성

- `config/service_concept.md` — 서비스 한 줄 설명 + 타겟 가정
- `config/interview_questions.json` — 인터뷰 질문 (싱글턴/멀티턴)

예시 파일이 들어 있으니 참고해서 수정.

### 4. 페르소나 필터링

```bash
python scripts/01_filter_personas.py
```

`config/filter_config.json`의 조건으로 페르소나를 추출해 `data/target_personas.json`에 저장.

### 5. 인터뷰 시뮬레이션

```bash
python scripts/02_run_interview.py
```

페르소나마다 질문을 던지고 응답을 `results/interview_responses.csv`에 저장.

### 6. 결과 분석

```bash
python scripts/03_analyze_results.py
```

질문별 응답 패턴, 카테고리 분포 등을 `results/analysis_report.json`에 저장.

## 주의사항

- **합성 페르소나는 "예의로 OK"라고 답하는 경향이 있다.** 100% 동의 결과는 무시하고, 의미 있는 거절/조건이 나오는 질문에만 집중.
- **경제 데이터(소득, 자산)는 없다.** 가격 질문은 시뮬에서 정확히 검증되지 않으니 실제 인터뷰로 보완.
- **시뮬 결과는 답이 아니라 지도다.** 어디를 더 깊이 파야 할지 알려주는 도구로만 사용.

## 데이터 출처

- [nvidia/Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (CC BY 4.0)
