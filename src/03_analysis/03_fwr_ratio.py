# src/03_analysis/03_fwr_ratio.py
import pandas as pd
import numpy as np
from utils.nlp_utils import calculate_fwr_per_doc, save_as_json
from utils.paths import FINAL, PROCESSED_FULL, PROCESSED_FILTERED, PROCESSED_SAMPLES, \
                        RESULTS_FWR_FULL, RESULTS_FWR_FILTERED, RESULTS_FWR_SAMPLES, RESULTS_FWR_LLM

def run_fwr_analysis(input_a="corpus_a_cleaned.csv", input_b="corpus_b_cleaned.csv"):
    """
    Berechnet die mittlere Function-Word-Ratio (FWR) pro Dokument für beide Korpora
    auf Basis von spaCy-POS-Tags. Funktion nimmt bereinigten Texte als Eingabe entgegen.
    FWR = Anzahl Funktionswörter / Anzahl Inhaltswörter pro Post.
    Speichert Mittelwerte, Differenz und Standardabweichungen in fwr_results.json.
    """
    print("--- Start FWR-Analyse (Verbosity Check) ---")
    
    path_a = PROCESSED_FULL / input_a
    path_b = PROCESSED_FULL / input_b

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
    save_as_json("fwr_results.json", meta, res, output_dir=RESULTS_FWR_FULL)

def run_fwr_analysis_downsampled(sample_num=1):
    """
    Berechnet die mittlere Function-Word-Ratio (FWR) pro Dokument für beide Korpora
    auf Basis von spaCy-POS-Tags. Funktion nimmt bereinigten Texte als Eingabe entgegen.
    FWR = Anzahl Funktionswörter / Anzahl Inhaltswörter pro Post.
    Speichert Mittelwerte, Differenz und Standardabweichungen in fwr_results.json.
    """
    print("--- Start FWR-Analyse (Verbosity Check) ---")
    
    path_a = PROCESSED_SAMPLES / f"sample{sample_num}_pre_n500.csv"
    path_b = PROCESSED_SAMPLES / f"sample{sample_num}_post_n500.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    size = len(df_a)  # Entspricht n=500

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
        "sample_size": size,
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
    save_as_json(f"fwr_results_sample{sample_num}.json", meta, res, output_dir=RESULTS_FWR_SAMPLES)


def run_fwr_analysis_filtered():
    """
    Berechnet FWR auf den token-laengen-gefilterten Reddit-Korpora (Primaeranalyse-Layer).
    Liest aus PROCESSED_FILTERED, subsampelt auf min(n_a, n_b). spaCy live (untagged-Variante).
    """
    print("--- Start FWR-Analyse Filtered (untagged, Verbosity Check) ---")

    path_a = PROCESSED_FILTERED / "corpus_a_filtered.csv"
    path_b = PROCESSED_FILTERED / "corpus_b_filtered.csv"

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
        "layer": "filtered",
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
    save_as_json("fwr_results_filtered.json", meta, res, output_dir=RESULTS_FWR_FILTERED)


def run_fwr_analysis_llm():
    """
    Vergleicht FWR: Reddit-Korpus B (filtered, post-2022) vs. Corpus C (LLM).
    Liest aus PROCESSED_FILTERED, subsampelt B auf n_c. spaCy live (untagged-Variante).
    """
    print("--- Start FWR-Analyse LLM (untagged, B vs C) ---")

    path_b = PROCESSED_FILTERED / "corpus_b_filtered.csv"
    path_c = PROCESSED_FILTERED / "corpus_c_filtered.csv"

    df_b = pd.read_csv(path_b)
    df_c = pd.read_csv(path_c)

    min_len = min(len(df_b), len(df_c))
    print(f"Sampling auf {min_len} Posts...")
    df_b = df_b.sample(n=min_len, random_state=42)
    df_c = df_c.sample(n=min_len, random_state=42)

    fwr_b = calculate_fwr_per_doc(df_b['text'])
    fwr_c = calculate_fwr_per_doc(df_c['text'])

    mean_b = np.mean(fwr_b)
    mean_c = np.mean(fwr_c)
    diff = mean_c - mean_b

    print("\n--- ERGEBNISSE ---")
    print(f"FWR B (Reddit post-2022): {mean_b:.4f}")
    print(f"FWR C (LLM):              {mean_c:.4f}")
    print(f"Differenz (C - B): {diff:.4f}")

    meta = {
        "sample_size": min_len,
        "mode": "fwr",
        "layer": "llm",
        "comparison": "B_reddit_filtered vs C_llm",
        "source_files": [str(path_b), str(path_c)]
    }
    res = {
        "mean_fwr_b": float(mean_b),
        "mean_fwr_c": float(mean_c),
        "diff_fwr": float(diff),
        "std_fwr_b": float(np.std(fwr_b)),
        "std_fwr_c": float(np.std(fwr_c))
    }
    save_as_json("fwr_results_llm.json", meta, res, output_dir=RESULTS_FWR_LLM)


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        run_fwr_analysis()
    elif mode == "filtered":
        run_fwr_analysis_filtered()
    elif mode == "llm":
        run_fwr_analysis_llm()
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        run_fwr_analysis_downsampled(sample_num=sample)