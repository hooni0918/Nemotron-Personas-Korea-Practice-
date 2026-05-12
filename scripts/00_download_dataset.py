"""
Nemotron-Personas-Korea parquet 파일 1개 다운로드.
700만 명 전체가 9개 파일로 나뉘어 있는데, 그중 1개(약 220MB, 110만 명)만 받는다.
"""
from pathlib import Path
from huggingface_hub import hf_hub_download

REPO_ID = "nvidia/Nemotron-Personas-Korea"
FILENAME = "data/train-00000-of-00009.parquet"
DATA_DIR = Path(__file__).parent.parent / "data"


def main():
    DATA_DIR.mkdir(exist_ok=True)
    target_path = DATA_DIR / "personas_sample.parquet"

    if target_path.exists():
        size_mb = target_path.stat().st_size / 1024 / 1024
        print(f"이미 다운로드되어 있음: {target_path} ({size_mb:.1f}MB)")
        return

    print(f"다운로드 중: {REPO_ID} / {FILENAME}")
    downloaded = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILENAME,
        repo_type="dataset",
        local_dir=DATA_DIR,
        local_dir_use_symlinks=False,
    )

    # huggingface_hub가 받은 파일을 우리 이름으로 옮긴다
    src = Path(downloaded)
    src.rename(target_path)

    # 빈 폴더 정리 (data/data/ 같은 구조가 생길 수 있음)
    nested = DATA_DIR / "data"
    if nested.exists() and not any(nested.iterdir()):
        nested.rmdir()

    size_mb = target_path.stat().st_size / 1024 / 1024
    print(f"완료: {target_path} ({size_mb:.1f}MB)")


if __name__ == "__main__":
    main()
