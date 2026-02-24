# Stylometric Changes in Online Texts (Bachelor Thesis)

## Overview
This repository contains the source code for my Bachelor's Thesis in Computational Linguistics at LMU Munich. The project investigates the "homogenization hypothesis" regarding Large Language Models (LLMs).

It provides a reproducible Python pipeline to analyze and compare stylometric features between pre-LLM (2019-2021) and post-LLM (2023-2025) text corpora, alongside synthetic reference data.

## Methodology
The Python pipeline (`src/`) implements a reproducible workflow to measure lexical and structural complexity using:

*   **Shannon Entropy:** Measuring information density and predictability.
*   **MTLD (Measure of Textual Lexical Diversity):** Assessing vocabulary richness robust to text length.
*   **Syntactic Complexity:** Analysis of POS n-grams and Parse Tree Depth via spaCy.

## Project Structure
*   `src/`: Contains the core logic for data preprocessing, metric calculation, and statistical analysis.
*   `data/`: (Not included in repo for privacy/size reasons) - Expects CSV inputs.

## Tech Stack
*   **Language:** Python 3.10+
*   **NLP:** spaCy, NLTK, lexical-diversity
*   **Data/Stats:** pandas, scipy, scikit-learn

## Status
**Active Development.** This project is part of an ongoing thesis (Submission: Summer 2026).
