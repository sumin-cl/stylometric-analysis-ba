# src/01_preprocessing/01_preprocess.py
"""
Bereinigt die Rohkorpora und speichert sie in 01_processed/full/.

Input:  data/final/00_extraction/corpus_*_raw_subset.csv
Output: data/final/01_processed/full/corpus_*_cleaned.csv

Verwendung:
    python src/01_preprocessing/01_preprocess.py        # Reddit A + B
    python src/01_preprocessing/01_preprocess.py llm    # LLM Korpus C
"""
import pandas as pd
from utils.cleanup import clean_reddit_text
from utils.paths import FINAL, EXTRACTED, PROCESSED_FULL
from pathlib import Path
import sys

def pipeline(input_name, output_name=None):
    """
    Vollständige Vorverarbeitungs-Pipeline für eine Korpusdatei.
    Erwartet standardmäßig Dateien aus data/final/00_extraction/.
    Bereinigt Texte, berechnet Token-Anzahlen und entfernt Posts mit weniger als 30 Tokens.
    Speichert das bereinigte Korpus unter data/final/<output_name>.csv.
    """
    input_path = EXTRACTED / input_name
    print(f"Verarbeite {input_path}...")

    if output_name is None:
        stem = Path(input_name).stem.replace("_raw_subset", "")
        output_name = f"{stem}_cleaned"

    df = pd.read_csv(input_path)

    df['text'] = df['post'].apply(clean_reddit_text)
    df['tokens'] = df['text'].apply(lambda x: len(x.split()))
    df = df[df['tokens'] >= 30].copy()
    
    FINAL.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_FULL / f"{output_name}.csv"
    df[['id', 'date', 'text']].to_csv(output_path, index=False)
    print(f"Gespeichert: {output_path} ({len(df)} Zeilen)")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "reddit"
    if mode == "llm":
        print("=== Preprocessing LLM-Korpus (corpus_c) ===")
        pipeline('corpus_c_raw.csv', 'corpus_c_cleaned')
    else:
        print("=== Preprocessing Reddit-Korpora (A + B) ===")
        pipeline('corpus_a_raw_subset.csv')
        pipeline('corpus_b_raw_subset.csv')