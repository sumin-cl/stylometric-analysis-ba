import os
import pandas as pd

def extract():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'data', 'raw'))
    
    raw_csv = os.path.join(DATA_DIR, "reddit_database.csv")
    df = pd.read_csv(raw_csv, low_memory=False)
    
    df = df[df['subreddit'] == 'MachineLearning'].copy()
    df['date'] = pd.to_datetime(df['created_timestamp'], unit='s')
    
    start_date = '2019-01-01'
    end_date = '2021-12-31'
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    df = df.loc[mask].copy()

    df = df[['id', 'date', 'post']]

    df = df.dropna(subset=['post'])
    
    df.to_csv("corpus_a_filtered.csv", index=False)
    print(f"A extrahiert: {len(df)} Zeilen.")

if __name__ == "__main__":
    extract()