from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from signal_room.data_generation import write_demo_data


if __name__ == "__main__":
    path = write_demo_data(Path("data"))
    print(f"Wrote {path}")
