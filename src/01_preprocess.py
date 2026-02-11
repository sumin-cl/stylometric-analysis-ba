import pandas as pd
from cleanup import clean_reddit_text
import os

def load_data(path):
    if path.endswith('.jsonl'): return pd.read_json(path, lines=True)
    return pd.read_csv(path)

def pipeline(input_path, output_name, is_corpus_b=False):
    print(f"Verarbeite {input_path}...")
    df = load_data(input_path)
    
    if is_corpus_b and 'selftext' in df.columns:
        df = df.rename(columns={'selftext': 'post', 'created_utc': 'date'})
        df['date'] = pd.to_datetime(df['date'], unit='s') if df['date'].dtype != '<M8[ns]' else df['date']
        df = df[df['date'].dt.year.isin([2023, 2024, 2025])]

    df['text'] = df['post'].apply(clean_reddit_text)
    df['tokens'] = df['text'].apply(lambda x: len(x.split()))
    df = df[df['tokens'] >= 30].copy()
    
    os.makedirs("data/final", exist_ok=True)
    df[['id', 'date', 'text']].to_csv(f"data/final/{output_name}.csv", index=False)
    print(f"Gespeichert: data/final/{output_name}.csv ({len(df)} Zeilen)")

if __name__ == "__main__":
    pipeline('corpus_a_filtered.csv', 'corpus_a_clean')
    pipeline('corpus_b_filtered.csv', 'corpus_b_clean', is_corpus_b=True)