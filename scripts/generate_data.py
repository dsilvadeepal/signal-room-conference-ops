from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from signal_room.data_generation import write_demo_data


if __name__ == "__main__":
    paths = write_demo_data(Path("data"))
    print("Wrote " + " and ".join(str(path) for path in paths))
