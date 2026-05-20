"""
Nemotron 페르소나를 PDF의 3 타겟 유형에 매칭해 자동 추출.

`01_filter_personas.py`는 단일 필터 조건으로 1개 그룹을 뽑는 반면,
이 스크립트는 `config/v3_match_config.json`의 label별 키워드로
여러 그룹을 동시에 라벨링·샘플링해서 한 파일에 담는다.

매칭 로직:
1. 인구통계 1차 필터 (연령·지역)
2. 각 라벨의 occupation_keywords로 매칭 → 매칭되면 라벨 할당
3. A/B 라벨에 잡히지 않은 나머지는 C_general 풀에 들어감
4. 라벨별로 sample_size만큼 random sample (seed 고정)

출력: data/place_scrap_personas_v3.json
각 페르소나에 추가 필드:
- match_label: A_marketer / B_engineer / C_general
- match_label_title: 사람용 라벨 제목
- match_reason: 매칭된 키워드 또는 'general_pool'
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "personas_sample.parquet"
CONFIG_PATH = ROOT / "config" / "v3_match_config.json"
OUTPUT_PATH = ROOT / "data" / "place_scrap_personas_v3.json"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def apply_demographic_filter(df: pd.DataFrame, demo: dict) -> pd.DataFrame:
    df = df[df["age"].between(demo["age_min"], demo["age_max"])]
    if demo.get("provinces"):
        df = df[df["province"].isin(demo["provinces"])]
    return df


def label_personas(df: pd.DataFrame, labels: list) -> pd.DataFrame:
    """각 페르소나에 label과 reason을 할당. A/B에 안 잡히면 C_general."""
    df = df.copy()
    df["match_label"] = None
    df["match_label_title"] = None
    df["match_reason"] = None

    occ = df["occupation"].fillna("").astype(str)

    for spec in labels:
        if spec["id"] == "C_general":
            continue
        keywords = spec.get("occupation_keywords", [])
        exclude = spec.get("exclude_occupation_keywords", [])
        if not keywords:
            continue

        include_pat = "|".join(re.escape(k) for k in keywords)
        matched_idx = occ.str.contains(include_pat, regex=True, na=False)
        if exclude:
            exclude_pat = "|".join(re.escape(k) for k in exclude)
            matched_idx &= ~occ.str.contains(exclude_pat, regex=True, na=False)

        # 아직 라벨이 없는 행만 채움 (앞 라벨 우선)
        free = df["match_label"].isna()
        target_idx = matched_idx & free
        df.loc[target_idx, "match_label"] = spec["id"]
        df.loc[target_idx, "match_label_title"] = spec["title"]

        def reason_for(o):
            for k in keywords:
                if k in o:
                    return f"occupation matched: {k}"
            return "occupation matched"
        df.loc[target_idx, "match_reason"] = occ[target_idx].apply(reason_for)

    # 나머지 = C_general 풀
    c_spec = next((s for s in labels if s["id"] == "C_general"), None)
    if c_spec:
        unlabeled = df["match_label"].isna()
        df.loc[unlabeled, "match_label"] = c_spec["id"]
        df.loc[unlabeled, "match_label_title"] = c_spec["title"]
        df.loc[unlabeled, "match_reason"] = "general_pool"

    return df


def sample_by_label(df: pd.DataFrame, labels: list, seed: int) -> pd.DataFrame:
    """라벨별로 sample_size만큼 추출."""
    parts = []
    for spec in labels:
        label_df = df[df["match_label"] == spec["id"]]
        n = min(spec["sample_size"], len(label_df))
        if n < spec["sample_size"]:
            print(f"  ⚠️  {spec['id']}: 목표 {spec['sample_size']}명 중 {n}명만 확보")
        parts.append(label_df.sample(n=n, random_state=seed))
    return pd.concat(parts).reset_index(drop=True)


def to_records(df: pd.DataFrame) -> list:
    """JSON 직렬화 가능한 dict 리스트로 변환."""
    return json.loads(df.to_json(orient="records", force_ascii=False))


def main():
    cfg = load_config()
    print(f"매칭 설정: {CONFIG_PATH.name}")
    print(f"  총 목표: {cfg['total_target']}명")
    for spec in cfg["labels"]:
        print(f"  - {spec['id']}: {spec['sample_size']}명 ({spec['title']})")
    print()

    print(f"parquet 로드: {DATA_PATH.name}")
    df = pd.read_parquet(DATA_PATH)
    print(f"  전체: {len(df):,}명")

    df = apply_demographic_filter(df, cfg["demographics"])
    print(f"  인구통계 필터 후: {len(df):,}명")
    print()

    print("라벨링...")
    df = label_personas(df, cfg["labels"])
    by_label = df["match_label"].value_counts()
    for label_id, count in by_label.items():
        print(f"  {label_id}: {count:,}명 풀")
    print()

    print(f"샘플링 (seed={cfg['random_seed']})...")
    sampled = sample_by_label(df, cfg["labels"], cfg["random_seed"])
    print(f"  최종: {len(sampled)}명")
    print()

    records = to_records(sampled)
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"저장 완료: {OUTPUT_PATH}")
    print()
    print("라벨별 분포:")
    for label_id, count in pd.Series([r["match_label"] for r in records]).value_counts().items():
        title = next((s["title"] for s in cfg["labels"] if s["id"] == label_id), "")
        print(f"  {label_id} ({title}): {count}명")


if __name__ == "__main__":
    main()
