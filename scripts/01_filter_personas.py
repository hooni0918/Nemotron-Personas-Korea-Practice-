"""
config/filter_config.json 의 조건으로 페르소나를 필터링해 JSON으로 저장.

출력: data/target_personas.json (필터링된 페르소나 리스트)
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "personas_sample.parquet"
CONFIG_PATH = ROOT / "config" / "filter_config.json"
OUTPUT_PATH = ROOT / "data" / "target_personas.json"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def apply_filters(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    if cfg.get("age_min") is not None:
        df = df[df["age"] >= cfg["age_min"]]
    if cfg.get("age_max") is not None:
        df = df[df["age"] <= cfg["age_max"]]

    if cfg.get("sex"):
        df = df[df["sex"] == cfg["sex"]]

    if cfg.get("education_levels"):
        df = df[df["education_level"].isin(cfg["education_levels"])]

    if cfg.get("occupation_keywords"):
        pattern = "|".join(cfg["occupation_keywords"])
        df = df[df["occupation"].str.contains(pattern, na=False)]

    if cfg.get("provinces"):
        df = df[df["province"].isin(cfg["provinces"])]

    if cfg.get("marital_status"):
        df = df[df["marital_status"].isin(cfg["marital_status"])]

    # 광역시·특별시 = 수도권/대도시. 실제 데이터에 별도 컬럼이 없으면 province로 추정.
    if cfg.get("metro_only"):
        metros = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기"]
        df = df[df["province"].isin(metros)]

    return df


def main():
    cfg = load_config()
    print(f"필터 조건: {json.dumps(cfg, ensure_ascii=False, indent=2)}\n")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"데이터 파일이 없습니다: {DATA_PATH}\n"
            f"먼저 'python scripts/00_download_dataset.py' 를 실행하세요."
        )

    print(f"parquet 로딩 중: {DATA_PATH}")
    df = pd.read_parquet(DATA_PATH)
    print(f"전체 페르소나: {len(df):,}명\n")

    filtered = apply_filters(df, cfg)
    print(f"필터 적용 후: {len(filtered):,}명")

    sample_size = cfg.get("sample_size", 50)
    if len(filtered) < sample_size:
        print(f"⚠️  필터 결과({len(filtered)}명)가 sample_size({sample_size})보다 작습니다. 전체 사용.")
        sample = filtered
    else:
        sample = filtered.sample(n=sample_size, random_state=cfg.get("random_seed", 42))

    print(f"최종 샘플: {len(sample):,}명\n")

    # 시뮬레이션에서 쓸 컬럼만 추려 dict로 변환
    persona_cols = [
        "uuid",
        "persona",
        "professional_persona",
        "family_persona",
        "culinary_persona",
        "travel_persona",
        "sex",
        "age",
        "marital_status",
        "education_level",
        "bachelors_field",
        "occupation",
        "district",
        "province",
    ]
    available_cols = [c for c in persona_cols if c in sample.columns]
    personas = sample[available_cols].to_dict(orient="records")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(personas, f, ensure_ascii=False, indent=2)

    print(f"저장 완료: {OUTPUT_PATH}")

    # 분포 요약
    print("\n=== 샘플 분포 ===")
    print(f"성별: {sample['sex'].value_counts().to_dict()}")
    print(f"평균 연령: {sample['age'].mean():.1f}세")
    print(f"학력: {sample['education_level'].value_counts().to_dict()}")
    print(f"지역(상위 5개): {sample['province'].value_counts().head().to_dict()}")


if __name__ == "__main__":
    main()
