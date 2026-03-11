# src/01_preprocessing/01_preprocess.py
import pandas as pd
from utils.cleanup import clean_reddit_text
from utils.paths import FINAL, EXTRACTED, PROCESSED
from pathlib import Path

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
    output_path = PROCESSED / f"{output_name}.csv"
    df[['id', 'date', 'text']].to_csv(output_path, index=False)
    print(f"Gespeichert: {output_path} ({len(df)} Zeilen)")

if __name__ == "__main__":
    pipeline('corpus_a_raw_subset.csv')
    pipeline('corpus_b_raw_subset.csv')