# src/03_fwr_ratio.py
import pandas as pd
import numpy as np
from nlp_utils import calculate_fwr_per_doc

def run_fwr_analysis():
    print("--- Start FWR-Analyse (Verbosity Check) ---")
    
    # 1. Laden & Sampling
    df_a = pd.read_csv("data/final/corpus_a_clean.csv")
    df_b = pd.read_csv("data/final/corpus_b_clean.csv")
    
    min_len = min(len(df_a), len(df_b))
    print(f"Sampling auf {min_len} Posts...")
    df_a = df_a.sample(n=min_len, random_state=42)
    df_b = df_b.sample(n=min_len, random_state=42)

    # 2. Berechnung
    fwr_a = calculate_fwr_per_doc(df_a['text'])
    fwr_b = calculate_fwr_per_doc(df_b['text'])

    # 3. Statistik
    mean_a = np.mean(fwr_a)
    mean_b = np.mean(fwr_b)
    diff = mean_b - mean_a
    
    print("\n--- ERGEBNISSE ---")
    print(f"FWR A (2019-21): {mean_a:.4f}")
    print(f"FWR B (2023-25): {mean_b:.4f}")
    print(f"Differenz: {diff:.4f}")
    
    if diff > 0:
        print(">> Hypothese gestützt: Texte werden 'dünner' (mehr Funktionswörter pro Inhalt).")
    else:
        print(">> Hypothese abgelehnt: Texte werden dichter.")

if __name__ == "__main__":
    run_fwr_analysis()