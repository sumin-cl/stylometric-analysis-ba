# src/03_syntax.py
import pandas as pd
import numpy as np
from utils.paths import FINAL, PROCESSED_FULL, PROCESSED_FILTERED, PROCESSED_SAMPLES, \
                        PARSED_FULL, PARSED_FILTERED, PARSED_SAMPLES, \
                        RESULTS_PTD_FULL, RESULTS_PTD_FILTERED, RESULTS_PTD_SAMPLES
from utils.nlp_utils import analyze_syntax_complexity, save_as_json
import json

def run_syntax_analysis():
    """
    Berechnet die durchschnittliche Dependency-Parse-Tree-Tiefe pro Post für beide Korpora.
    Eine geringere mittlere Tiefe deutet auf geringere syntaktische Komplexität hin.
    Subsampelt indexbasiert auf min(n_a, n_b), damit Mean ueber balanciertem Set rechnet
    (konsistent mit den anderen Analysen im full-Modus).
    Speichert Mittelwerte und Differenz in syntax_parse_depth.json.
    Gibt die beiden Listen mit Post-Tiefen für nachgelagerte Signifikanztests zurück.
    """
    print("--- SYNTACTIC COMPLEXITY (Parse Tree Depth) ---")

    path_a = PROCESSED_FULL / "corpus_a_cleaned.csv"
    path_b = PROCESSED_FULL / "corpus_b_cleaned.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)

    depths_a_full = json.load(open(PARSED_FULL / "corpus_a_cleaned_parsed_depths.json"))
    depths_b_full = json.load(open(PARSED_FULL / "corpus_b_cleaned_parsed_depths.json"))

    # Sanity check: depths-Liste muss zu df passen
    assert len(depths_a_full) == len(df_a), \
        f"Laenge-Mismatch A: depths={len(depths_a_full)} vs df={len(df_a)}"
    assert len(depths_b_full) == len(df_b), \
        f"Laenge-Mismatch B: depths={len(depths_b_full)} vs df={len(df_b)}"

    min_len = min(len(df_a), len(df_b))
    print(f"Subsample auf {min_len} Posts pro Korpus (Index-basiert)...")

    df_a_sub = df_a.sample(n=min_len, random_state=42)
    df_b_sub = df_b.sample(n=min_len, random_state=42)

    # depths nach den selben Indizes auswaehlen
    depths_a = [depths_a_full[i] for i in df_a_sub.index]
    depths_b = [depths_b_full[i] for i in df_b_sub.index]

    mean_a = np.mean(depths_a)
    mean_b = np.mean(depths_b)
    diff = mean_b - mean_a

    print("\n--- ERGEBNISSE ---")
    print(f"Durchschnittliche Baumtiefe A: {mean_a:.2f}")
    print(f"Durchschnittliche Baumtiefe B: {mean_b:.2f}")
    print(f"Differenz: {diff:.2f}")

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
        "mean_ptd_a": float(mean_a),
        "mean_ptd_b": float(mean_b),
        "diff_ptd": float(diff)
    }
    save_as_json("syntax_parse_depth.json", meta, res, output_dir=RESULTS_PTD_FULL)

    return depths_a, depths_b

def run_syntax_analysis_downsampled(sample_num=1):
    """
    Berechnet die durchschnittliche Dependency-Parse-Tree-Tiefe pro Post für beide Korpora.
    Eine geringere mittlere Tiefe deutet auf geringere syntaktische Komplexität hin.
    Speichert Mittelwerte und Differenz in syntax_parse_depth.json.
    Gibt die beiden Listen mit Post-Tiefen für nachgelagerte Signifikanztests zurück.
    """
    print("--- SYNTACTIC COMPLEXITY (Parse Tree Depth) ---")

    path_a = PROCESSED_SAMPLES / f"sample{sample_num}_pre_n500.csv"
    path_b = PROCESSED_SAMPLES / f"sample{sample_num}_post_n500.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    size = len(df_a)
    
    print(f"Verarbeite {size} Posts pro Korpus...")

    print("\nKorpus A (2019-21):")
    depths_a = json.load(open(PARSED_SAMPLES / f"sample{sample_num}_pre_n500_parsed_depths.json"))

    print("\nKorpus B (2023-25):")
    depths_b = json.load(open(PARSED_SAMPLES / f"sample{sample_num}_post_n500_parsed_depths.json"))

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
    save_as_json(f"syntax_parse_depth_sample{sample_num}.json", meta, res, output_dir=RESULTS_PTD_SAMPLES)

    return depths_a, depths_b, sample_num


def run_syntax_analysis_filtered():
    """
    Berechnet PTD auf den token-laengen-gefilterten Reddit-Korpora (Primaeranalyse-Layer).
    Liest depths aus PARSED_FILTERED (vorberechnet via 01_parse_and_cache.py filtered).
    Subsampelt indexbasiert auf min(n_a, n_b), damit Mean ueber balanciertem Set rechnet.
    """
    print("--- SYNTACTIC COMPLEXITY (Parse Tree Depth) — Filtered ---")

    path_a = PROCESSED_FILTERED / "corpus_a_filtered.csv"
    path_b = PROCESSED_FILTERED / "corpus_b_filtered.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)

    depths_a_full = json.load(open(PARSED_FILTERED / "corpus_a_filtered_parsed_depths.json"))
    depths_b_full = json.load(open(PARSED_FILTERED / "corpus_b_filtered_parsed_depths.json"))

    # Sanity check: depths-Liste muss zu df passen
    assert len(depths_a_full) == len(df_a), \
        f"Laenge-Mismatch A: depths={len(depths_a_full)} vs df={len(df_a)}"
    assert len(depths_b_full) == len(df_b), \
        f"Laenge-Mismatch B: depths={len(depths_b_full)} vs df={len(df_b)}"

    min_len = min(len(df_a), len(df_b))
    print(f"Subsample auf {min_len} Posts pro Korpus (Index-basiert)...")

    df_a_sub = df_a.sample(n=min_len, random_state=42)
    df_b_sub = df_b.sample(n=min_len, random_state=42)

    # depths nach den selben Indizes auswaehlen
    depths_a = [depths_a_full[i] for i in df_a_sub.index]
    depths_b = [depths_b_full[i] for i in df_b_sub.index]

    mean_a = np.mean(depths_a)
    mean_b = np.mean(depths_b)
    diff = mean_b - mean_a

    print("\n--- ERGEBNISSE ---")
    print(f"Durchschnittliche Baumtiefe A: {mean_a:.2f}")
    print(f"Durchschnittliche Baumtiefe B: {mean_b:.2f}")
    print(f"Differenz: {diff:.2f}")

    if mean_b < mean_a:
        print(">> Hypothese gestützt: Die Satzstruktur wird flacher (weniger komplex).")
    else:
        print(">> Hypothese abgelehnt: Sätze werden tiefer verschachtelt.")

    meta = {
        "sample_size": min_len,
        "mode": "parse_tree_depth",
        "layer": "filtered",
        "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mean_ptd_a": float(mean_a),
        "mean_ptd_b": float(mean_b),
        "diff_ptd": float(diff)
    }
    save_as_json("syntax_parse_depth_filtered.json", meta, res, output_dir=RESULTS_PTD_FILTERED)

    return depths_a, depths_b


# src/03_analysis/03_mannwhitney.py
from scipy.stats import mannwhitneyu
import numpy as np
from utils.nlp_utils import append_to_json

def run_significance_test(depths_a, depths_b, sample_num=None, layer=None):
    """
    Führt einen zweiseitigen Mann-Whitney-U-Test auf den Baumtiefe-Verteilungen durch.
    Fügt U-Statistik, p-Wert und rangbiserialen Effektgröße r an die jeweilige
    syntax_parse_depth*.json an.
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

    if layer == "filtered":
        filename = "syntax_parse_depth_filtered.json"
        out_dir = RESULTS_PTD_FILTERED
    elif sample_num is not None:
        filename = f"syntax_parse_depth_sample{sample_num}.json"
        out_dir = RESULTS_PTD_SAMPLES
    else:
        filename = "syntax_parse_depth.json"
        out_dir = RESULTS_PTD_FULL

    append_to_json(filename, {
        "mann_whitney_u": float(stat),
        "p_value": float(p_val),
        "effect_size_r": abs(stat) / (len(depths_a) * len(depths_b))**0.5
    }, output_dir=out_dir)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        depths_a, depths_b = run_syntax_analysis()
        mwu_outcome = run_significance_test(depths_a, depths_b)
    elif mode == "filtered":
        depths_a, depths_b = run_syntax_analysis_filtered()
        mwu_outcome = run_significance_test(depths_a, depths_b, layer="filtered")
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        depths_a, depths_b, sample_num = run_syntax_analysis_downsampled(sample)
        mwu_outcome = run_significance_test(depths_a, depths_b, sample_num)