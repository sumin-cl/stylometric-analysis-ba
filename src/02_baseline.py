# src/02_baseline.py
import pandas as pd
import matplotlib.pyplot as plt

def analyze_baseline(path_a, path_b):
    print("--- BASELINE ANALYSE ---")
    
    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    
    df_a['corpus'] = 'A (2019-21)'
    df_b['corpus'] = 'B (2023-25)'
    
    df_a['tokens'] = df_a['text'].astype(str).apply(lambda x: len(x.split()))
    df_b['tokens'] = df_b['text'].astype(str).apply(lambda x: len(x.split()))

    post_count_a = len(df_a)
    post_count_b = len(df_b)
    
    mean_a = df_a['tokens'].mean()
    mean_b = df_b['tokens'].mean()

    median_a = df_a['tokens'].median()
    median_b = df_b['tokens'].median()
    
    print(f"\nKORPUS A (Pre-LLM):")
    print(f"Anzahl Posts: {post_count_a}")
    print(f"Durchschnittliche Länge: {mean_a:.2f} Wörter")
    print(f"Median Länge: {median_a:.2f} Wörter")
    
    print(f"\nKORPUS B (Post-LLM):")
    print(f"Anzahl Posts: {post_count_b}")
    print(f"Durchschnittliche Länge: {mean_b:.2f} Wörter")
    print(f"Median Länge: {median_b:.2f} Wörter")
    
    min_count = min(post_count_a, post_count_b)
    print(f"\n>>> EMPFEHLUNG FÜR DOWNSAMPLING: Reduziere beide auf {min_count} Posts.")

    meta = {
    "sample_size": min_count,
    "mode": "baseline_statistics",
    "source_files": ["data/final/corpus_a_clean.csv", "data/final/corpus_b_clean.csv"]
    }
    res = {
        "mean_a": mean_a,
        "mean_b": mean_b,
        "diff_count_a_b_raw": mean_b - mean_a,
        "post_count_a": post_count_a,
        "post_count_b": post_count_b,
        "median_a": median_a,
        "median_b": median_b,
    }
    from nlp_utils import save_as_json
    save_as_json("baseline_stats.json", meta, res)

if __name__ == "__main__":
    analyze_baseline('data/final/corpus_a_clean.csv', 'data/final/corpus_b_clean.csv')