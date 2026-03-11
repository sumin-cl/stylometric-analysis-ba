# src/03_analysis/03_fwr_ratio.py
import pandas as pd
import numpy as np
from utils.nlp_utils import calculate_fwr_per_doc, save_as_json
from utils.paths import FINAL, PROCESSED

def run_fwr_analysis(input_a="corpus_a_cleaned.csv", input_b="corpus_b_cleaned.csv"):
    """
    Berechnet die mittlere Function-Word-Ratio (FWR) pro Dokument für beide Korpora
    auf Basis von spaCy-POS-Tags. Funktion nimmt bereinigten Texte als Eingabe entgegen.
    FWR = Anzahl Funktionswörter / Anzahl Inhaltswörter pro Post.
    Speichert Mittelwerte, Differenz und Standardabweichungen in fwr_results.json.
    """
    print("--- Start FWR-Analyse (Verbosity Check) ---")
    
    path_a = PROCESSED / input_a
    path_b = PROCESSED / input_b

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    
    min_len = min(len(df_a), len(df_b))
    print(f"Sampling auf {min_len} Posts...")
    df_a = df_a.sample(n=min_len, random_state=42)
    df_b = df_b.sample(n=min_len, random_state=42)

    fwr_a = calculate_fwr_per_doc(df_a['text'])
    fwr_b = calculate_fwr_per_doc(df_b['text'])

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

    meta = {
        "sample_size": min_len,
        "mode": "fwr",
        "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mean_fwr_a": float(mean_a),
        "mean_fwr_b": float(mean_b),
        "diff_fwr": float(diff),
        # For MWU
        "std_fwr_a": float(np.std(fwr_a)),
        "std_fwr_b": float(np.std(fwr_b))
    }
    save_as_json("fwr_results.json", meta, res)

if __name__ == "__main__":
    run_fwr_analysis()