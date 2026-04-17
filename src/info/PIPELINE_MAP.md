# PIPELINE_MAP.md

Dieses Dokument beschreibt **welches Skript welche Datei erzeugt**,  
**wo die Datei liegt**,  
**wie sie heißt**,  
**und wofür sie später benötigt wird**.

Es basiert ausschließlich auf dem aktuellen Ordnerbaum + dem geplanten Topic‑Extractor.

---

## 0. Überblick

Die Pipeline besteht aus:

1. **Extraction** – Rohdaten aus externen Quellen holen  
2. **Preprocessing** – Cleaning, Parsing, POS‑Tagging  
3. **EDA** – Baseline‑Statistiken  
4. **Analysis** – linguistische Metriken  
5. **Visualization** – Plots und Signifikanz  
6. **Synthetic (geplant)** – Topic‑Extraction für spätere LLM‑Generierung

---

## 1. Extraction (`00_extraction/`)

### `00_extract_a_kaggle.py`
- **Input:** Kaggle‑Dataset  
- **Output:** `corpus_a_raw.csv`  
- **Purpose:** Rohdaten extrahieren

### `00_extract_b_arctic.py`
- **Input:** Arctic‑Dataset  
- **Output:** `corpus_b_raw.csv`  
- **Purpose:** Rohdaten extrahieren

---

## 2. Preprocessing (`01_preprocessing/`)

### `01_parse_and_cache.py`
- **Input:** `corpus_*_raw.csv`  
- **Output:** interne Cache‑Dateien  
- **Purpose:** Parsing, Vorverarbeitung

### `01_preprocess.py`
- **Input:** Cache‑Daten  
- **Output:**  
  - `corpus_a_clean.csv`  
  - `corpus_b_clean.csv`  
- **Purpose:** Cleaning, Normalisierung

### `01b_pos_tagger.py`
- **Input:** `corpus_*_clean.csv`  
- **Output:**  
  - `corpus_a_tagged.csv`  
  - `corpus_b_tagged.csv`  
- **Purpose:** POS‑Tagging für spätere Analysen

---

## 3. EDA (`02_eda/`)

### `02_baseline.py`
- **Input:** `corpus_*_clean.csv`  
- **Output:** `baseline_stats.json`  
- **Purpose:** Baseline‑Statistiken

---

## 4. Analysis (`03_analysis/`)

Alle Skripte in diesem Ordner:

- **Input:** `corpus_*_clean.csv` oder `corpus_*_tagged.csv`  
- **Output:** diverse JSON‑Ergebnisse in `data/final/results/`  
- **Purpose:** linguistische Analysen (FWR, MTLD, Syntax, Shannon, Mann‑Whitney usw.)

---

## 5. Visualization (`04_visualization/`)

### `04_visualization.py`
- **Input:** Analyse‑JSONs  
- **Output:** Plots  
- **Purpose:** Visualisierung der Ergebnisse

### `04_sign_all.py`
- **Input:** Analyse‑Ergebnisse  
- **Output:** Signifikanz‑Zusammenfassungen  
- **Purpose:** statistische Signifikanztests

---

## 6. Synthetic Pipeline (geplant)

### `01c_topic_extraction.py`
- **Input:**  
  - `sample*_pre_n500.csv`  
  - `sample*_post_n500.csv`  
  *(kommen aus deinem Downsampling‑Script außerhalb dieses Baums)*

- **Output:**  
  - `sample*_pre_topics.csv`  
  - `sample*_post_topics.csv`

- **Format:** CSV  
  - `nouns` (JSON‑encoded list)  
  - `adjectives` (JSON‑encoded list)  
  - `tokens` (kombiniert)

- **Purpose:**  
  Extrahiert Nomen/Adjektive als Grundlage für spätere Prompt‑Generierung.

---

- **`data/raw/`**  
  Originalquellen (Reddit, JSONL, CSV)

- **`data/final/02_processed/`**  
  Clean‑Korpora

- **`data/final/03_tagged/`**  
  POS‑getaggte Korpora

- **`data/final/results/`**  
  Analyse‑Outputs (JSON)

- **`data/final/04_entropy_lists/`**  
  Zwischendateien für Entropie‑Berechnungen

---

## 8. Utils (`utils/`)

### `nlp_utils.py`
- NLP‑Hilfsfunktionen

### `paths.py`
- zentrale Pfaddefinitionen

### `cleanup.py`
- Cleaning‑Utilities

---

## 9. Root

### `run_pipeline.py`
- orchestriert Analyse‑/Visualisierungs‑Schritte  
- **(synthetische Pipeline ist hier noch nicht integriert)**

