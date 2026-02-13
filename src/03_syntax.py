# src/03_syntax.py
import pandas as pd
from nlp_utils import analyze_syntax_complexity
import numpy as np

def run_syntax_analysis():
    print("--- SYNTACTIC COMPLEXITY (Parse Tree Depth) ---")
    
    # 1. Laden
    df_a = pd.read_csv("data/final/corpus_a_clean.csv")
    df_b = pd.read_csv("data/final/corpus_b_clean.csv")

    min_len = min(len(df_a), len(df_b))
    
    test_mode = False 
    
    if test_mode:
        print("ZUM TESTEN: Nur 500 Posts pro Korpus!")
        min_len = 500
        
    df_a = df_a.sample(n=min_len, random_state=42)
    df_b = df_b.sample(n=min_len, random_state=42)
    
    print(f"Verarbeite {min_len} Posts pro Korpus...")

    # 2. Analyse
    print("\nKorpus A (2019-21):")
    depths_a = analyze_syntax_complexity(df_a['text'])
    
    print("\nKorpus B (2023-25):")
    depths_b = analyze_syntax_complexity(df_b['text'])
    
    # 3. Statistik
    mean_a = np.mean(depths_a)
    mean_b = np.mean(depths_b)
    
    print("\n--- ERGEBNISSE ---")
    print(f"Durchschnittliche Baumtiefe A: {mean_a:.2f}")
    print(f"Durchschnittliche Baumtiefe B: {mean_b:.2f}")
    print(f"Differenz: {mean_b - mean_a:.2f}")
    
    if mean_b < mean_a:
        print(">> Hypothese gestützt: Die Satzstruktur wird flacher (weniger komplex).")
    else:
        print(">> Hypothese abgelehnt: Sätze werden tiefer verschachtelt.")

    return depths_a, depths_b

if __name__ == "__main__":
    depths_a, depths_b = run_syntax_analysis()