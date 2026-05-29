# Stylometric Changes in Online Texts (Bachelor Thesis)

## Overview
Source code for my Bachelor's thesis in Computational Linguistics at LMU Munich. The project tests the "homogenization hypothesis" by comparing stylometric features across a pre-LLM human corpus (r/MachineLearning, 2019–2021), a post-LLM human corpus (2023–2025), and a synthetic corpus generated with GPT-4o.

## Metrics
- **Shannon Entropy** (word and POS level), with a vocabulary-aligned variant
- **MTLD** (Measure of Textual Lexical Diversity), chunk-level
- **Function Word Ratio (FWR)**, tagged and untagged
- **Parse Tree Depth (PTD)** via spaCy dependency parsing

## Project Structure

```
src/
├── 00_extraction/     # Kaggle (A), Arctic Shift (B), GPT-4o output (C)
├── 01_preprocessing/  # cleaning, 100–400 token filter, sampling, POS tagging, parse caching
├── 02_eda/            # baseline statistics, length distribution
├── 02_generation/     # topic extraction, prompt building, synthetic corpus generation
├── 03_analysis/       # MTLD, Shannon, FWR, PTD, Mann–Whitney U
├── 04_visualization/  # significance report, plots, correlation matrices
└── utils/             # shared paths, NLP utilities
data/final/            # generated outputs (raw source dumps not included; see Data)
```

## Tech Stack
- Python 3.11+
- spaCy 3.8.11 with `en_core_web_sm` 3.8.0
- `lexical-diversity` (MTLD), pandas, numpy, scipy
- matplotlib, seaborn, plotly
- `openai` for synthetic corpus generation (set `OPENAI_API_KEY`)

All versions are pinned in `requirements.txt`.

## Data
The two raw source corpora are not included. To reproduce corpora A and B, place the source files in `data/raw/`:
- `reddit_database.csv` — Kaggle r/MachineLearning dataset (2019–2021)
- `r_machinelearning_posts.jsonl` — Arctic Shift dump (2023–2025)

The repository ships the derived artefacts only (analysis results under `data/final/results/` and exploratory output under `data/final/02_eda/`); the cleaned and tagged corpora are omitted as they contain verbatim post text.

## Setup

```
python -m venv venv
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Running
On Windows, run `start.bat` for an interactive menu (Reddit pipeline, synthetic pipeline, analysis). Otherwise set `PYTHONPATH=src` and run `python src/run_pipeline.py`, or call an individual stage script directly.

## License
Academic use only.