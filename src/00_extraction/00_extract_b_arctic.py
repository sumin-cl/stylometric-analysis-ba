# src/00_extraction/00_extract_b_arctic.py
import pandas as pd
from utils.paths import RAW, EXTRACTED

def extract():
    """
    Extrahiert r/MachineLearning-Posts aus dem Arctic-Shift-JSONL-Datensatz.
    Filtert auf die Jahre 2023-2025.
    Speichert das Ergebnis als unbereinigtes Subset.
    """
    raw_jsonl = RAW / "r_machinelearning_posts.jsonl"
    df = pd.read_json(raw_jsonl, lines=True)
    
    df['date'] = pd.to_datetime(df['created_utc'], unit='s')
    df = df[df['date'].dt.year.isin([2023, 2024, 2025])]
    
    df = df.rename(columns={'selftext': 'post'})
    df = df[['id', 'date', 'post']]
    
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    output_path = EXTRACTED / "corpus_b_raw_subset.csv"
    df.to_csv(output_path, index=False)

    print(f"B extrahiert: {len(df)} Zeilen → {output_path}")

if __name__ == "__main__":
    extract()