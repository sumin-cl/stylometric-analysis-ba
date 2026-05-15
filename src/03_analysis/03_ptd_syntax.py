# src/03_syntax.py
import pandas as pd
import numpy as np
from utils.paths import FINAL, PROCESSED_FULL, PROCESSED_FILTERED, PROCESSED_SAMPLES, \
                        PARSED_FULL, PARSED_FILTERED, PARSED_SAMPLES, \
                        RESULTS_PTD_FULL, RESULTS_PTD_FILTERED, RESULTS_PTD_SAMPLES, RESULTS_PTD_LLM
from utils.nlp_utils import analyze_syntax_complexity, save_as_json, compute_mwu, print_mwu_summary
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

    mwu = compute_mwu(depths_a, depths_b)
    print_mwu_summary(mwu, label="PTD A vs B (full)")

    meta = {
        "sample_size": min_len,
        "mode": "parse_tree_depth",
        "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mean_ptd_a": float(mean_a),
        "mean_ptd_b": float(mean_b),
        "diff_ptd": float(diff),
        **mwu,
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

    mwu = compute_mwu(depths_a, depths_b)
    print_mwu_summary(mwu, label=f"PTD A vs B (sample {sample_num})")

    meta = {
        "sample_size": size,
        "mode": "parse_tree_depth",
        "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mean_ptd_a": mean_a,
        "mean_ptd_b": mean_b,
        "diff_ptd": diff,
        **mwu,
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

    mwu = compute_mwu(depths_a, depths_b)
    print_mwu_summary(mwu, label="PTD A vs B (filtered)")

    meta = {
        "sample_size": min_len,
        "mode": "parse_tree_depth",
        "layer": "filtered",
        "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mean_ptd_a": float(mean_a),
        "mean_ptd_b": float(mean_b),
        "diff_ptd": float(diff),
        **mwu,
    }
    save_as_json("syntax_parse_depth_filtered.json", meta, res, output_dir=RESULTS_PTD_FILTERED)

    return depths_a, depths_b


def run_syntax_analysis_llm():
    """
    Vergleicht PTD: Reddit-Korpus B (filtered, post-2022) vs. Corpus C (LLM).
    Liest depths aus PARSED_FILTERED. Subsampelt B auf n_c indexbasiert,
    damit Mean ueber balanciertem Set rechnet.
    """
    print("--- SYNTACTIC COMPLEXITY (Parse Tree Depth) — LLM: B vs C ---")

    path_b = PROCESSED_FILTERED / "corpus_b_filtered.csv"
    path_c = PROCESSED_FILTERED / "corpus_c_filtered.csv"

    df_b = pd.read_csv(path_b)
    df_c = pd.read_csv(path_c)

    depths_b_full = json.load(open(PARSED_FILTERED / "corpus_b_filtered_parsed_depths.json"))
    depths_c_full = json.load(open(PARSED_FILTERED / "corpus_c_filtered_parsed_depths.json"))

    assert len(depths_b_full) == len(df_b), \
        f"Laenge-Mismatch B: depths={len(depths_b_full)} vs df={len(df_b)}"
    assert len(depths_c_full) == len(df_c), \
        f"Laenge-Mismatch C: depths={len(depths_c_full)} vs df={len(df_c)}"

    min_len = min(len(df_b), len(df_c))
    print(f"Subsample auf {min_len} Posts pro Korpus (Index-basiert)...")

    df_b_sub = df_b.sample(n=min_len, random_state=42)
    df_c_sub = df_c.sample(n=min_len, random_state=42)

    depths_b = [depths_b_full[i] for i in df_b_sub.index]
    depths_c = [depths_c_full[i] for i in df_c_sub.index]

    mean_b = np.mean(depths_b)
    mean_c = np.mean(depths_c)
    diff = mean_c - mean_b

    print("\n--- ERGEBNISSE ---")
    print(f"Durchschnittliche Baumtiefe B (Reddit post-2022): {mean_b:.2f}")
    print(f"Durchschnittliche Baumtiefe C (LLM):              {mean_c:.2f}")
    print(f"Differenz (C - B): {diff:.2f}")

    if mean_c < mean_b:
        print(">> LLM-Output hat flachere Parse-Bäume als Reddit B.")
    else:
        print(">> LLM-Output hat tiefere Parse-Bäume als Reddit B.")

    mwu = compute_mwu(depths_b, depths_c)
    print_mwu_summary(mwu, label="PTD B vs C (LLM)")

    meta = {
        "sample_size": min_len,
        "mode": "parse_tree_depth",
        "layer": "llm",
        "comparison": "B_reddit_filtered vs C_llm",
        "source_files": [str(path_b), str(path_c)]
    }
    res = {
        "mean_ptd_b": float(mean_b),
        "mean_ptd_c": float(mean_c),
        "diff_ptd": float(diff),
        **mwu,
    }
    save_as_json("syntax_parse_depth_llm.json", meta, res, output_dir=RESULTS_PTD_LLM)

    return depths_b, depths_c


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        run_syntax_analysis()
    elif mode == "filtered":
        run_syntax_analysis_filtered()
    elif mode == "llm":
        run_syntax_analysis_llm()
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        run_syntax_analysis_downsampled(sample)