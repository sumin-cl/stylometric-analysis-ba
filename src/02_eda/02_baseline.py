# src/02_eda/02_baseline.py
import pandas as pd
from utils.paths import FINAL, EDA, PROCESSED
from utils.nlp_utils import save_as_json

def analyze_baseline(input_a, input_b):
    """
    Berechnet und gibt deskriptive Statistiken beider Korpora aus
    (Anzahl Posts, mittlere und mediane Token-Länge).
    Empfiehlt eine Downsampling-Zielgröße und speichert die Ergebnisse in baseline_stats.json.
    """
    path_a = PROCESSED / input_a
    path_b = PROCESSED / input_b

    print("--- BASELINE ANALYSE ---")
    
    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    
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
    print(f"\n>>> Empfehlung für Downsampling: Reduziere beide auf {min_count} Posts.")

    meta = {
    "sample_size": min_count,
    "mode": "baseline_statistics",
    "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mean_a": mean_a,
        "mean_b": mean_b,
        "diff_mean_b_minus_a": mean_b - mean_a,
        "post_count_a": post_count_a,
        "post_count_b": post_count_b,
        "median_a": median_a,
        "median_b": median_b,
    }
    save_as_json("baseline_stats.json", meta, res, output_dir=str(EDA))

if __name__ == "__main__":
    analyze_baseline("corpus_a_cleaned.csv", "corpus_b_cleaned.csv")