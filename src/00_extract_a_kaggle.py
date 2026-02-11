import pandas as pd

def extract():
    raw_csv = "data/raw/reddit_database.csv"
    df = pd.read_csv(raw_csv, low_memory=False)
    
    df = df[df['subreddit'] == 'MachineLearning'].copy()
    df['date'] = pd.to_datetime(df['created_timestamp'], unit='s')
    
    start_date = '2019-01-01'
    end_date = '2021-12-31'
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    df = df.loc[mask].copy()

    df = df[['id', 'date', 'post']]

    df = df.dropna(subset=['post'])
    
    df.to_csv("data/raw/corpus_a_filtered.csv", index=False)
    print(f"A extrahiert: {len(df)} Zeilen.")

if __name__ == "__main__":
    extract()