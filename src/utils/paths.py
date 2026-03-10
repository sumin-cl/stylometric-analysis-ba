# src/utils/paths.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
RAW = DATA / "raw"
FINAL = DATA / "final"

PROCESSED = FINAL / "02_processed"
TAGGED = FINAL / "03_tagged"
RESULTS = FINAL / "results"
