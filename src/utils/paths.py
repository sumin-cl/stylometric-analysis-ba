# src/utils/paths.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA  = ROOT / "data"
RAW   = DATA / "raw"
FINAL = DATA / "final"

EXTRACTED = FINAL / "00_extraction"
PROCESSED = FINAL / "01_processed" 
EDA       = FINAL / "02_eda"  
TAGGED    = FINAL / "03_tagged"     
PARSED    = FINAL / "04_parsed"     

RESULTS         = FINAL / "results"
RESULTS_ENTROPY = RESULTS / "entropy"

for p in [PROCESSED, EDA, TAGGED, PARSED, RESULTS, RESULTS_ENTROPY]:
    p.mkdir(parents=True, exist_ok=True)