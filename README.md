# Stylometric Changes in Online Texts (Bachelor Thesis)

## Overview
This repository contains the source code for my Bachelor's Thesis in Computational Linguistics at LMU Munich. The project investigates the "homogenization hypothesis" regarding Large Language Models (LLMs).

It provides a reproducible Python pipeline to analyze and compare stylometric features between pre-LLM (2019–2021) and post-LLM (2023–2025) text corpora sourced from r/MachineLearning.

## Methodology
The pipeline implements a reproducible workflow to measure lexical and structural complexity using:

- **Shannon Entropy:** Measuring information density and predictability at word and POS level.
- **MTLD (Measure of Textual Lexical Diversity):** Assessing vocabulary richness, robust to text length.
- **Function Word Ratio (FWR):** Measuring the ratio of function words to content words as a verbosity proxy.
- **Syntactic Complexity (PTD):** Parse Tree Depth analysis via spaCy dependency parsing.

A vocabulary-filtered variant of each metric controls for topic shift between the two time periods.

## Project Structure

```
src/
├── 00_extraction/       # Kaggle CSV + Arctic Shift JSONL extraction
├── 01_preprocessing/    # Text cleaning, POS tagging, parse caching
├── 02_eda/              # Baseline corpus statistics
├── 03_analysis/         # Entropy, MTLD, FWR, PTD, Mann-Whitney-U
├── 04_visualization/    # Significance tests, plots
└── utils/               # Shared paths, NLP utilities, cleanup

data/                    # Not included — see Data section below
├── raw/                 # Place source files here
└── final/
    ├── 00_extraction/
    ├── 01_processed/
    ├── 02_eda/
    ├── 03_tagged/
    ├── 04_parsed/
    └── results/
        └── entropy/
```

## Data
The raw data is not included in this repository due to size. To reproduce the analysis, place the following files in `data/raw/`:

- `reddit_database.csv` — Kaggle Reddit dataset (r/MachineLearning, 2019–2021)
- `r_machinelearning_posts.jsonl` — Arctic Shift dataset (r/MachineLearning, 2023–2025)

## Tech Stack

- **Language:** Python 3.11+
- **NLP:** spaCy (`en_core_web_sm`), lexical-diversity
- **Data / Stats:** pandas, numpy, scipy

## Running the Pipeline

### Prerequisites
- Python 3.11+
- Virtual environment: `python -m venv venv`
- Dependencies: `pip install -r requirements.txt`
- spaCy model: `python -m spacy download en_core_web_sm`
- Raw data placed in `data/raw/`

---

### Option 1 — Windows Batch (easiest)

Double-click `start.bat` in the project root. An interactive menu lets you run the full pipeline or any individual step.

---

### Option 2 — Command Line (Windows PowerShell)

```powershell
# Set PYTHONPATH once for the session
$env:PYTHONPATH="src"

# Run full pipeline
python src/run_pipeline.py

# Or run individual steps
python src/03_analysis/03_shannon.py
```

---

### Option 3 — Command Line (Linux / macOS)

```bash
# Set PYTHONPATH once for the session
export PYTHONPATH=src

# Run full pipeline
python src/run_pipeline.py

# Or run individual steps
python src/03_analysis/03_shannon.py
```

## Status
**Active Development.** Part of an ongoing thesis at LMU Munich (Submission: Summer 2026).

## License
Academic use only.
