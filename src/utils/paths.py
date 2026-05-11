# src/utils/paths.py
from pathlib import Path

ROOT  = Path(__file__).resolve().parents[2]
DATA  = ROOT / "data"
RAW   = DATA / "raw"
FINAL = DATA / "final"

# ── 00 Extraction ─────────────────────────────────────────────────────────────
EXTRACTED = FINAL / "00_extraction"

# ── 01 Processed ──────────────────────────────────────────────────────────────
PROCESSED          = FINAL / "01_processed"
PROCESSED_FULL     = PROCESSED / "full"       # corpus_*_cleaned.csv
PROCESSED_FILTERED = PROCESSED / "filtered"   # corpus_*_filtered.csv
PROCESSED_SAMPLES  = PROCESSED / "samples"    # sample{N}_{pre/post}_n500.csv

# ── 02 EDA ────────────────────────────────────────────────────────────────────
EDA = FINAL / "02_eda"

# ── 02 Generation ─────────────────────────────────────────────────────────────
GENERATED         = FINAL / "02_generation"
GENERATED_PROMPTS = GENERATED / "prompts"
GENERATED_TOPICS  = GENERATED / "topics"
GENERATED_CORPUS  = GENERATED / "synthetic_corpus"
GENERATED_REPORTS = GENERATED / "reports"

# ── 03 Tagged ─────────────────────────────────────────────────────────────────
TAGGED          = FINAL / "03_tagged"
TAGGED_FULL     = TAGGED / "full"       # corpus_*_tagged.csv  (Vollkorpus, optional)
TAGGED_FILTERED = TAGGED / "filtered"   # corpus_*_filtered_tagged.csv
TAGGED_SAMPLES  = TAGGED / "samples"    # sample{N}_{pre/post}_n500_tagged.csv

# ── 04 Parsed ─────────────────────────────────────────────────────────────────
PARSED          = FINAL / "04_parsed"
PARSED_FULL     = PARSED / "full"       # corpus_*_cleaned_parsed_depths.json  (Vollkorpus, optional)
PARSED_FILTERED = PARSED / "filtered"   # corpus_*_filtered_parsed_depths.json
PARSED_SAMPLES  = PARSED / "samples"    # sample{N}_{pre/post}_n500_parsed_depths.json

# ── Results ───────────────────────────────────────────────────────────────────
RESULTS         = FINAL / "results"
RESULTS_MTLD    = RESULTS / "mtld"
RESULTS_SHANNON = RESULTS / "shannon"
RESULTS_FWR     = RESULTS / "fwr"
RESULTS_PTD     = RESULTS / "ptd"
RESULTS_SIGNIF  = RESULTS / "significance"

# Per-Layer Subordner: full / filtered / samples / llm
RESULTS_MTLD_FULL     = RESULTS_MTLD / "full"
RESULTS_MTLD_FILTERED = RESULTS_MTLD / "filtered"
RESULTS_MTLD_SAMPLES  = RESULTS_MTLD / "samples"
RESULTS_MTLD_LLM      = RESULTS_MTLD / "llm"

RESULTS_SHANNON_FULL     = RESULTS_SHANNON / "full"
RESULTS_SHANNON_FILTERED = RESULTS_SHANNON / "filtered"
RESULTS_SHANNON_SAMPLES  = RESULTS_SHANNON / "samples"
RESULTS_SHANNON_LLM      = RESULTS_SHANNON / "llm"

RESULTS_FWR_FULL     = RESULTS_FWR / "full"
RESULTS_FWR_FILTERED = RESULTS_FWR / "filtered"
RESULTS_FWR_SAMPLES  = RESULTS_FWR / "samples"
RESULTS_FWR_LLM      = RESULTS_FWR / "llm"

RESULTS_PTD_FULL     = RESULTS_PTD / "full"
RESULTS_PTD_FILTERED = RESULTS_PTD / "filtered"
RESULTS_PTD_SAMPLES  = RESULTS_PTD / "samples"
RESULTS_PTD_LLM      = RESULTS_PTD / "llm"

# ── Auto-create all directories ───────────────────────────────────────────────
for p in [
    EXTRACTED,
    PROCESSED_FULL, PROCESSED_FILTERED, PROCESSED_SAMPLES,
    EDA,
    GENERATED_PROMPTS, GENERATED_TOPICS, GENERATED_CORPUS, GENERATED_REPORTS,
    TAGGED_FULL, TAGGED_FILTERED, TAGGED_SAMPLES,
    PARSED_FULL, PARSED_FILTERED, PARSED_SAMPLES,
    RESULTS_MTLD_FULL, RESULTS_MTLD_FILTERED, RESULTS_MTLD_SAMPLES, RESULTS_MTLD_LLM,
    RESULTS_SHANNON_FULL, RESULTS_SHANNON_FILTERED, RESULTS_SHANNON_SAMPLES, RESULTS_SHANNON_LLM,
    RESULTS_FWR_FULL, RESULTS_FWR_FILTERED, RESULTS_FWR_SAMPLES, RESULTS_FWR_LLM,
    RESULTS_PTD_FULL, RESULTS_PTD_FILTERED, RESULTS_PTD_SAMPLES, RESULTS_PTD_LLM,
    RESULTS_SIGNIF,
]:
    p.mkdir(parents=True, exist_ok=True)