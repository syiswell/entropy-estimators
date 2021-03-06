import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
IMAGES_DIR = RESULTS_DIR / "images"
TIMINGS_DIR = RESULTS_DIR / "timings"

DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
TIMINGS_DIR.mkdir(exist_ok=True)

BATCH_SIZE = int(os.environ.get('BATCH_SIZE', 256))
