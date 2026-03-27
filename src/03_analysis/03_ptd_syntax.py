# src/03_syntax.py
import pandas as pd
import numpy as np
from utils.paths import FINAL, PROCESSED, PARSED
from utils.nlp_utils import analyze_syntax_complexity, save_as_json
import json

def run_syntax_analysis():
    """
    Berechnet die durchschnittliche Dependency-Parse-Tree-Tiefe pro Post für beide Korpora.
    Eine geringere mittlere Tiefe deutet auf geringere syntaktische Komplexität hin.
    Speichert Mittelwerte und Differenz in syntax_parse_depth.json.
    Gibt die beiden Listen mit Post-Tiefen für nachgelagerte Signifikanztests zurück.
    """
    print("--- SYNTACTIC COMPLEXITY (Parse Tree Depth) ---")

    path_a = PROCESSED / "corpus_a_cleaned.csv"
    path_b = PROCESSED / "corpus_b_cleaned.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)

    min_len = min(len(df_a), len(df_b))
        
    df_a = df_a.sample(n=min_len, random_state=42)
    df_b = df_b.sample(n=min_len, random_state=42)
    
    print(f"Verarbeite {min_len} Posts pro Korpus...")

    print("\nKorpus A (2019-21):")
    depths_a = json.load(open(PARSED /"corpus_a_cleaned_parsed_depths.json"))

    print("\nKorpus B (2023-25):")
    depths_b = json.load(open(PARSED / "corpus_b_cleaned_parsed_depths.json"))

    mean_a = np.mean(depths_a)
    mean_b = np.mean(depths_b)

    diff = mean_b - mean_a
    
    print("\n--- ERGEBNISSE ---")
    print(f"Durchschnittliche Baumtiefe A: {mean_a:.2f}")
    print(f"Durchschnittliche Baumtiefe B: {mean_b:.2f}")
    print(f"Differenz: {mean_b - mean_a:.2f}")
    
    if mean_b < mean_a:
        print(">> Hypothese gestützt: Die Satzstruktur wird flacher (weniger komplex).")
    else:
        print(">> Hypothese abgelehnt: Sätze werden tiefer verschachtelt.")

    meta = {
        "sample_size": min_len,
        "mode": "parse_tree_depth",
        "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mean_ptd_a": mean_a,
        "mean_ptd_b": mean_b,
        "diff_ptd": diff
    }
    save_as_json(f"syntax_parse_depth.json", meta, res)

    return depths_a, depths_b

def run_syntax_analysis_downsampled(sample_num=1):
    """
    Berechnet die durchschnittliche Dependency-Parse-Tree-Tiefe pro Post für beide Korpora.
    Eine geringere mittlere Tiefe deutet auf geringere syntaktische Komplexität hin.
    Speichert Mittelwerte und Differenz in syntax_parse_depth.json.
    Gibt die beiden Listen mit Post-Tiefen für nachgelagerte Signifikanztests zurück.
    """
    print("--- SYNTACTIC COMPLEXITY (Parse Tree Depth) ---")

    path_a = PROCESSED / f"sample{sample_num}_pre_n500.csv"
    path_b = PROCESSED / f"sample{sample_num}_post_n500.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    size = len(df_a)
    
    print(f"Verarbeite {size} Posts pro Korpus...")

    print("\nKorpus A (2019-21):")
    depths_a = json.load(open(PARSED /f"sample{sample_num}_pre_n500_parsed_depths.json"))

    print("\nKorpus B (2023-25):")
    depths_b = json.load(open(PARSED / f"sample{sample_num}_post_n500_parsed_depths.json"))

    mean_a = np.mean(depths_a)
    mean_b = np.mean(depths_b)

    diff = mean_b - mean_a
    
    print("\n--- ERGEBNISSE ---")
    print(f"Durchschnittliche Baumtiefe A: {mean_a:.2f}")
    print(f"Durchschnittliche Baumtiefe B: {mean_b:.2f}")
    print(f"Differenz: {mean_b - mean_a:.2f}")
    
    if mean_b < mean_a:
        print(">> Hypothese gestützt: Die Satzstruktur wird flacher (weniger komplex).")
    else:
        print(">> Hypothese abgelehnt: Sätze werden tiefer verschachtelt.")

    meta = {
        "sample_size": size,
        "mode": "parse_tree_depth",
        "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mean_ptd_a": mean_a,
        "mean_ptd_b": mean_b,
        "diff_ptd": diff
    }
    save_as_json(f"syntax_parse_depth_sample{sample_num}.json", meta, res)

    return depths_a, depths_b, sample_num

# src/03_analysis/03_mannwhitney.py
from scipy.stats import mannwhitneyu
import numpy as np
from utils.nlp_utils import append_to_json

def run_significance_test(depths_a, depths_b, sample_num):
    """
    Führt einen zweiseitigen Mann-Whitney-U-Test auf den Baumtiefe-Verteilungen durch.
    Fügt U-Statistik, p-Wert und rangbiserialen Effektgröße r an syntax_parse_depth.json an.
    """
    print("\n--- STATISTISCHE SIGNIFIKANZ (Mann-Whitney-U) ---")
    
    stat, p_val = mannwhitneyu(depths_a, depths_b, alternative='two-sided')
    
    print(f"U-Statistik: {stat:.2f}")
    print(f"p-Wert: {p_val:.10f}")

    if p_val < 0.05:
        print(">>> Ergebnis ist signifikant (p < 0.05). Der Unterschied ist kein Zufall.")
        if p_val < 0.001:
            print(">>> Höchste Signifikanzstufe erreicht (p < 0.001).")
    else:
        print(">>> Ergebnis ist nicht signifikant. Der Unterschied könnte Zufall sein.")

    mean_diff = np.mean(depths_a) - np.mean(depths_b)
    print(f"Absolute Differenz der Mittelwerte: {mean_diff:.4f}")

    append_to_json(
        f"syntax_parse_depth_sample{sample_num}.json",
        {
            "mann_whitney_u": float(stat),
            "p_value": float(p_val),
            "effect_size_r": abs(stat) / (len(depths_a) * len(depths_b))**0.5
        }
    )

if __name__ == "__main__":
    depths_a, depths_b, sample_num = run_syntax_analysis_downsampled()
    mwu_outcome = run_significance_test(depths_a, depths_b, sample_num)