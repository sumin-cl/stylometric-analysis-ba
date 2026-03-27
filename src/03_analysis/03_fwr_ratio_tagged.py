# src/03_analysis/03_fwr_ratio_tagged.py
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from utils.paths import FINAL, TAGGED
from utils.nlp_utils import save_as_json

def run_fwr_analysis_tagged(input_a="corpus_a_tagged.csv", input_b="corpus_b_tagged.csv"):
    """
    Berechnet die FWR direkt aus vorgetaggten POS-Strings der getaggten Korpora.
    Führt einen zweiseitigen Mann-Whitney-U-Test auf den dokumentweisen FWR-Verteilungen durch.
    Speichert Ergebnisse inkl. p-Wert und Signifikanz-Flag in fwr_results.json.
    """
    path_a = TAGGED / input_a
    path_b = TAGGED / input_b

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
    save_as_json("fwr_results_tagged.json", meta, res)

def run_fwr_analysis_tagged_downsampled(sample_num=1):
    """
    Berechnet die FWR direkt aus vorgetaggten POS-Strings der getaggten Korpora.
    Führt einen zweiseitigen Mann-Whitney-U-Test auf den dokumentweisen FWR-Verteilungen durch.
    Speichert Ergebnisse inkl. p-Wert und Signifikanz-Flag in fwr_results.json.
    """
    path_a = TAGGED / f"sample{sample_num}_pre_n500_tagged.csv"
    path_b = TAGGED / f"sample{sample_num}_post_n500_tagged.csv"

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
    save_as_json("fwr_results_tagged.json", meta, res)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        run_fwr_analysis_tagged()
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        run_fwr_analysis_tagged_downsampled(sample_num=sample)
