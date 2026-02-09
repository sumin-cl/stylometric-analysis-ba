import pandas as pd
from preprocessing_test import clean_reddit_text

def process_new_corpus_b(input_json, output_csv):
    print("--- Lade Arctic Shift Daten ---")
    # Arctic Shift kommt oft als JSONL (JSON Lines)
    df = pd.read_json(input_json, lines=True)
    
    # 1. Spalten-Mapping & Datumskonvertierung
    df['date'] = pd.to_datetime(df['created_utc'], unit='s')
    df['year'] = df['date'].dt.year
    df = df.rename(columns={'selftext': 'post'})
    
    # 2. Relevante Jahre filtern (2023, 2024)
    df = df[df['year'].isin([2023, 2024])]
    print(f"Posts in Zieljahren: {len(df)}")

    # 3. Cleaning
    print("Cleaning läuft...")
    df['text'] = df['post'].apply(clean_reddit_text)
    
    # 4. Längen-Filter (>= 30 Wörter)
    df['token_count'] = df['text'].apply(lambda x: len(x.split()))
    df = df[df['token_count'] >= 30].copy()

    df_final = df[['id', 'date', 'text']]
    
    # 6. Speichern
    df_final[['id', 'date', 'text']].to_csv(output_csv, index=False)
    print(f"Erfolg: {len(df_final)} Posts in {output_csv} gespeichert.")

if __name__ == "__main__":
    process_new_corpus_b('r_machinelearning_posts.jsonl', 'corpus_b_2023_2024.csv')