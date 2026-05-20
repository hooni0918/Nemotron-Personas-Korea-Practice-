# Nemotron-Personas-Korea Practice

실제 사용자 인터뷰 전에, 작성한 질문지를 **NVIDIA 한국인 합성 페르소나**(`nvidia/Nemotron-Personas-Korea`, 700만 명)에 미리 던져보고 어떤 질문이 leading인지·모호한지 자동 진단하는 도구.

> 상세 시행착오는 [PROCESS.md](./PROCESS.md).

---

## 파이프라인

```
00 다운로드 → 01 필터링 → 02 인터뷰 → 03 분석
parquet     target.json   responses     report.md
```

| 단계 | 입력 | 출력 |
|---|---|---|
| `00_download_dataset.py` | HF | `data/personas_sample.parquet` (~220MB) |
| `01_filter_personas.py` | `filter_config.json` | `data/target_personas.json` |
| `02_run_interview.py` | personas + `interview_questions.json` | `results/interview_responses.{csv,json}` |
| `03_analyze_results.py` | responses | `results/analysis_report.{md,json}` |

## 회차별 결과 아카이브

각 회차의 입력(`service_concept` · `interview_questions` · `filter_config`)과 출력(`responses` · `analysis` · `SUMMARY`)은 `results/YYYY-MM-DD_v{n}_{label}/` 폴더에 함께 박제됨. 회차 인덱스: [`results/README.md`](./results/README.md)

### 최신 회차 빠른 접근 — v3 nemotron-matched (2026-05-20)

- 📄 [**SUMMARY.md**](./results/2026-05-20_v3_nemotron-matched/SUMMARY.md) — 120명 라벨별 응답 분포 + MVP1 검증
- 📊 [**analysis_report.md**](./results/2026-05-20_v3_nemotron-matched/analysis_report.md) — 자동 진단 리포트
- 📑 [**interview_responses.csv**](./results/2026-05-20_v3_nemotron-matched/interview_responses.csv) — 2,280행 raw
- 📋 [v3_match_config.json](./results/2026-05-20_v3_nemotron-matched/v3_match_config.json) · [place_scrap_personas_v3.json](./results/2026-05-20_v3_nemotron-matched/place_scrap_personas_v3.json) · [interview_questions.json](./results/2026-05-20_v3_nemotron-matched/interview_questions.json) — 이 회차 입력 스냅샷

이전 회차: [v2 place-scrap-personas](./results/2026-05-20_v2_place-scrap-personas/SUMMARY.md) · [v1 baseline](./results/2026-05-18_v1_baseline/SUMMARY.md)

---

## 사용법

```bash
# 셋업
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # GEMINI_API_KEY 채우기

# 실행
python scripts/00_download_dataset.py   # 1회만
python scripts/01_filter_personas.py
python scripts/02_run_interview.py
python scripts/03_analyze_results.py

open results/analysis_report.md
```

다른 서비스에 적용하려면 `config/` 3개 파일만 수정:
- `service_concept.md` — 검증 대상 서비스 정의
- `filter_config.json` — 타겟 페르소나 조건
- `interview_questions.json` — 질문지 (single/multi turn)

---

## 핵심 동작

- **시스템 프롬프트**: 페르소나 컬럼 3종(`persona` + `professional` + `family`)을 합쳐 1인칭 롤플레잉 강제
- **멀티턴**: `model.start_chat()`으로 이전 응답을 컨텍스트에 누적 → 가격 거절 사유 등 깊이 추출
- **자동 진단** (`03_analyze_results.py`):
  - Positive 80%↑ → **leading question**
  - Neutral 70%↑ → **모호**
  - 평균 길이 30자↓ → **관심 부족 / 질문 빈약**

---

## 비용 (gemini-2.5-flash-lite, $0.10/$0.40 per 1M tokens)

| 페르소나 × 턴 | 예상 비용 |
|---|---|
| 50 × 11 | ~$0.13 |
| 200 × 11 | ~$0.52 |
| 500 × 11 | ~$1.30 |

무료 티어(RPM 15)는 50명도 빡빡 → **결제 카드 등록 + 사용량 cap 설정 권장**.

---

## 한계

- 데이터셋에 **소득·자산 정보 없음** → 가격 민감도 검증 부정확. 실제 인터뷰로 보완.
- LLM은 예의로 "OK" 답하는 경향 → 100% 동의는 신뢰 X (`03`이 자동 필터).
- 시뮬 결과는 답이 아니라 **지도**. 어디를 더 깊이 파야 할지 알려주는 도구.

---

- 데이터: [nvidia/Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (CC BY 4.0)
- 레포: https://github.com/hooni0918/Nemotron-Personas-Korea-Practice-
