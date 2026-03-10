import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from utils.nlp_utils import save_as_json

def run_fwr_analysis_tagged():
    """
    Berechnet die FWR direkt aus vorgetaggten POS-Strings der getaggten Korpora.
    Führt einen zweiseitigen Mann-Whitney-U-Test auf den dokumentweisen FWR-Verteilungen durch.
    Speichert Ergebnisse inkl. p-Wert und Signifikanz-Flag in fwr_results.json.
    """
    df_a = pd.read_csv("data/final/03_tagged/corpus_a_tagged.csv")
    df_b = pd.read_csv("data/final/03_tagged/corpus_b_tagged.csv")
    
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

    res = {
        "mean_fwr_a": np.mean(fwr_a),
        "mean_fwr_b": np.mean(fwr_b),
        "p_value": float(p_val),
        "u_stat": float(stat),
        "significant": bool(p_val < 0.05)
    }
    
    print(f"Ergebnis: p={p_val:.10f}")
    save_as_json("fwr_results_tagged.json", {"mode": "fwr_tagged"}, res)

if __name__ == "__main__":
    run_fwr_analysis_tagged()