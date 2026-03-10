# src/00_extraction/00_extract_a_kaggle.py
import pandas as pd
from utils.paths import RAW, EXTRACTED

def extract():
    """
    Extrahiert r/MachineLearning-Posts aus dem Kaggle-Reddit-CSV-Datensatz.
    Filtert auf den Zeitraum 01.01.2019 bis 31.12.2021 und entfernt Posts ohne Text.
    Speichert das Ergebnis als unbereinigtes Subset.
    """
    raw_csv = RAW / "reddit_database.csv"
    df = pd.read_csv(raw_csv, low_memory=False)
    
    df = df[df['subreddit'] == 'MachineLearning'].copy()
    df['date'] = pd.to_datetime(df['created_timestamp'], unit='s')
    
    start_date = '2019-01-01'
    end_date = '2021-12-31'
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    df = df.loc[mask].copy()

    df = df[['id', 'date', 'post']]

    df = df.dropna(subset=['post'])
    
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    output_path = EXTRACTED / "corpus_a_raw_subset.csv"
    df.to_csv(output_path, index=False)

    print(f"A extrahiert: {len(df)} Zeilen → {output_path}")

if __name__ == "__main__":
    extract()