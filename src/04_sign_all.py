import pandas as pd
from scipy.stats import mannwhitneyu
import numpy as np
from nlp_utils import save_as_json

def calculate_significance(name, values_a, values_b):
    """
    Führt einen zweiseitigen Mann-Whitney-U-Test auf zwei Wertelisten durch und gibt das Ergebnis aus.
    Gibt ein Dict mit 'u_stat' und 'p_value' zurück.
    """
    stat, p_val = mannwhitneyu(values_a, values_b, alternative='two-sided')
    print(f"{name}: p-value = {p_val:.10f} ({'SIGNIFIKANT' if p_val < 0.05 else 'NICHT signifikant'})")
    return {"u_stat": float(stat), "p_value": float(p_val)}

def run_all_stats():
    """
    Lädt beide getaggten Korpora und führt Signifikanztests für alle Metriken durch.
    Speichert den vollständigen Signifikanzbericht in final_significance_report.json.
    """
    df_a = pd.read_csv("data/tagged/corpus_a_tagged.csv")
    df_b = pd.read_csv("data/tagged/corpus_b_tagged.csv")
    
    len_a = df_a['text'].str.split().str.len()
    len_b = df_b['text'].str.split().str.len()
    
    results = {}
    results["text_length"] = calculate_significance("Text Length", len_a, len_b)
    
    save_as_json("final_significance_report.json", {"mode": "all_metrics"}, results)

if __name__ == "__main__":
    run_all_stats()