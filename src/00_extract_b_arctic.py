import pandas as pd
import os

def extract():
    raw_jsonl = "data/raw/r_machinelearning_posts.jsonl"
    df = pd.read_json(raw_jsonl, lines=True)
    
    # Zeit-Extraktion & Filter
    df['date'] = pd.to_datetime(df['created_utc'], unit='s')
    df = df[df['date'].dt.year.isin([2023, 2024, 2025])]
    
    # Spalten-Mapping
    df = df.rename(columns={'selftext': 'post'})
    df = df[['id', 'date', 'post']]
    
    df.to_csv("data/raw/corpus_b_filtered.csv", index=False)
    print(f"B extrahiert: {len(df)} Zeilen.")

if __name__ == "__main__":
    extract()