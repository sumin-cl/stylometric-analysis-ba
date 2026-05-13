# src/03_analysis/03_fwr_ratio_tagged.py
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from utils.paths import FINAL, TAGGED_FULL, TAGGED_FILTERED, TAGGED_SAMPLES, \
                        RESULTS_FWR_FULL, RESULTS_FWR_FILTERED, RESULTS_FWR_SAMPLES, RESULTS_FWR_LLM
from utils.nlp_utils import save_as_json

def run_fwr_analysis_tagged(input_a="corpus_a_tagged.csv", input_b="corpus_b_tagged.csv"):
    """
    Berechnet die FWR direkt aus vorgetaggten POS-Strings der getaggten Korpora.
    Führt einen zweiseitigen Mann-Whitney-U-Test auf den dokumentweisen FWR-Verteilungen durch.
    Speichert Ergebnisse inkl. p-Wert und Signifikanz-Flag in fwr_results.json.
    """
    path_a = TAGGED_FULL / input_a
    path_b = TAGGED_FULL / input_b

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    
    func_tags = {'PRON', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART'}

    def get_fwr(pos_string):
        tags = str(pos_string).split()
        if not tags: return 0
        func_count = sum(1 for t in tags if t in func_tags)
        return func_count / len(tags)

    print("Berechne FWR aus POS-Tags...")
    fwr_a = df_a['pos_tags'].apply(get_fwr).tolist()
    fwr_b = df_b['pos_tags'].apply(get_fwr).tolist()

    stat, p_val = mannwhitneyu(fwr_a, fwr_b, alternative='two-sided')

    meta = {
        "mode": "fwr_tagged",
        "source_files": [str(path_a), str(path_b)]
    }

    res = {
        "mean_fwr_a": float(np.mean(fwr_a)),
        "mean_fwr_b": float(np.mean(fwr_b)),
        "p_value": float(p_val),
        "u_stat": float(stat),
        "significant": bool(p_val < 0.05)
    }
    
    print(f"Ergebnis: p={p_val:.10f}")
    save_as_json("fwr_results_tagged.json", meta, res, output_dir=RESULTS_FWR_FULL)

def run_fwr_analysis_tagged_downsampled(sample_num=1):
    """
    Berechnet die FWR direkt aus vorgetaggten POS-Strings der getaggten Korpora.
    Führt einen zweiseitigen Mann-Whitney-U-Test auf den dokumentweisen FWR-Verteilungen durch.
    Speichert Ergebnisse inkl. p-Wert und Signifikanz-Flag in fwr_results.json.
    """
    path_a = TAGGED_SAMPLES / f"sample{sample_num}_pre_n500_tagged.csv"
    path_b = TAGGED_SAMPLES / f"sample{sample_num}_post_n500_tagged.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    
    func_tags = {'PRON', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART'}

    def get_fwr(pos_string):
        tags = str(pos_string).split()
        if not tags: return 0
        func_count = sum(1 for t in tags if t in func_tags)
        return func_count / len(tags)

    print("Berechne FWR aus POS-Tags...")
    fwr_a = df_a['pos_tags'].apply(get_fwr).tolist()
    fwr_b = df_b['pos_tags'].apply(get_fwr).tolist()

    stat, p_val = mannwhitneyu(fwr_a, fwr_b, alternative='two-sided')

    meta = {
        "mode": "fwr_tagged",
        "sample_num": sample_num,
        "source_files": [str(path_a), str(path_b)]
    }

    res = {
        "mean_fwr_a": float(np.mean(fwr_a)),
        "mean_fwr_b": float(np.mean(fwr_b)),
        "p_value": float(p_val),
        "u_stat": float(stat),
        "significant": bool(p_val < 0.05)
    }
    
    print(f"Ergebnis: p={p_val:.10f}")
    save_as_json(f"fwr_results_tagged_sample{sample_num}.json", meta, res, output_dir=RESULTS_FWR_SAMPLES)


def run_fwr_analysis_tagged_filtered():
    """
    Berechnet FWR auf den vor-getaggten, token-laengen-gefilterten Reddit-Korpora
    (Primaeranalyse-Layer, tagged). Liest aus TAGGED_FILTERED.
    Subsampelt auf min(n_a, n_b) fuer Vergleichbarkeit, fuehrt Mann-Whitney-U-Test durch.
    """
    path_a = TAGGED_FILTERED / "corpus_a_filtered_tagged.csv"
    path_b = TAGGED_FILTERED / "corpus_b_filtered_tagged.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)

    min_len = min(len(df_a), len(df_b))
    print(f"Sampling auf {min_len} Posts...")
    df_a = df_a.sample(n=min_len, random_state=42)
    df_b = df_b.sample(n=min_len, random_state=42)

    func_tags = {'PRON', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART'}

    def get_fwr(pos_string):
        tags = str(pos_string).split()
        if not tags: return 0
        func_count = sum(1 for t in tags if t in func_tags)
        return func_count / len(tags)

    print("Berechne FWR aus POS-Tags (filtered)...")
    fwr_a = df_a['pos_tags'].apply(get_fwr).tolist()
    fwr_b = df_b['pos_tags'].apply(get_fwr).tolist()

    stat, p_val = mannwhitneyu(fwr_a, fwr_b, alternative='two-sided')

    meta = {
        "sample_size": min_len,
        "mode": "fwr_tagged",
        "layer": "filtered",
        "source_files": [str(path_a), str(path_b)]
    }

    res = {
        "mean_fwr_a": float(np.mean(fwr_a)),
        "mean_fwr_b": float(np.mean(fwr_b)),
        "p_value": float(p_val),
        "u_stat": float(stat),
        "significant": bool(p_val < 0.05)
    }

    print(f"Ergebnis: p={p_val:.10f}")
    save_as_json("fwr_results_tagged_filtered.json", meta, res, output_dir=RESULTS_FWR_FILTERED)


def run_fwr_analysis_tagged_llm():
    """
    Vergleicht FWR (tagged): Reddit-Korpus B (filtered, post-2022) vs. Corpus C (LLM).
    Liest aus TAGGED_FILTERED. Subsampelt B auf n_c, Mann-Whitney-U-Test.
    """
    print("--- Start FWR-Analyse LLM (tagged, B vs C) ---")

    path_b = TAGGED_FILTERED / "corpus_b_filtered_tagged.csv"
    path_c = TAGGED_FILTERED / "corpus_c_filtered_tagged.csv"

    df_b = pd.read_csv(path_b)
    df_c = pd.read_csv(path_c)

    min_len = min(len(df_b), len(df_c))
    print(f"Sampling auf {min_len} Posts...")
    df_b = df_b.sample(n=min_len, random_state=42)
    df_c = df_c.sample(n=min_len, random_state=42)

    func_tags = {'PRON', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART'}

    def get_fwr(pos_string):
        tags = str(pos_string).split()
        if not tags: return 0
        func_count = sum(1 for t in tags if t in func_tags)
        return func_count / len(tags)

    print("Berechne FWR aus POS-Tags (LLM-Vgl)...")
    fwr_b = df_b['pos_tags'].apply(get_fwr).tolist()
    fwr_c = df_c['pos_tags'].apply(get_fwr).tolist()

    stat, p_val = mannwhitneyu(fwr_b, fwr_c, alternative='two-sided')

    meta = {
        "sample_size": min_len,
        "mode": "fwr_tagged",
        "layer": "llm",
        "comparison": "B_reddit_filtered vs C_llm",
        "source_files": [str(path_b), str(path_c)]
    }

    res = {
        "mean_fwr_b": float(np.mean(fwr_b)),
        "mean_fwr_c": float(np.mean(fwr_c)),
        "p_value": float(p_val),
        "u_stat": float(stat),
        "significant": bool(p_val < 0.05)
    }

    print(f"Ergebnis: p={p_val:.10f}")
    save_as_json("fwr_results_tagged_llm.json", meta, res, output_dir=RESULTS_FWR_LLM)


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        run_fwr_analysis_tagged()
    elif mode == "filtered":
        run_fwr_analysis_tagged_filtered()
    elif mode == "llm":
        run_fwr_analysis_tagged_llm()
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        run_fwr_analysis_tagged_downsampled(sample_num=sample)