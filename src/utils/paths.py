# src/utils/paths.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
RAW = DATA / "raw"
FINAL = DATA / "final"

EXTRACTED = FINAL / "00_extraction"

PROCESSED = FINAL / "02_processed"
TAGGED = FINAL / "03_tagged"
RESULTS = FINAL / "results"
RESULTS_ENTROPY = RESULTS / "entropy"

RESULTS.mkdir(parents=True, exist_ok=True)
RESULTS_ENTROPY.mkdir(parents=True, exist_ok=True)