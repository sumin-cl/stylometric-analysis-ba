# src/03_shannon.py
import pandas as pd
from nlp_utils import get_flat_tokens, get_pos_tags, downsample_corpora, calculate_shannon_entropy, filter_list_by_reference

def analyze_entropy(mode="WORD"):
    """
    mode: "WORD" für Wort-Entropie, "POS" für Grammatik-Entropie
    """
    print(f"\n=== STARTE ENTROPIE-ANALYSE: {mode} ===")
    df_a, df_b, size = downsample_corpora("data/final/corpus_a_clean.csv", "data/final/corpus_b_clean.csv")

    # 1. Daten extrahieren
    if mode == "WORD":
        list_a = get_flat_tokens(df_a['text'])
        list_b = get_flat_tokens(df_b['text'])
    elif mode == "POS":
        list_a = get_pos_tags(df_a['text'])
        list_b = get_pos_tags(df_b['text'])
    
    # 2. Basis-Entropie berechnen
    entropy_a = calculate_shannon_entropy(list_a)
    entropy_b = calculate_shannon_entropy(list_b)
    
    print(f"Entropie A ({mode}): {entropy_a:.4f}")
    print(f"Entropie B ({mode}): {entropy_b:.4f}")
    
    # 3. Intersection / Filterung
    print(f"Filtere B basierend auf A (Intersection)...")
    list_b_filtered = filter_list_by_reference(list_b, list_a, min_freq=1) 
    
    entropy_b_filt = calculate_shannon_entropy(list_b_filtered)
    print(f"Entropie B (Filtered): {entropy_b_filt:.4f}")
    
    # Fazit
    diff_raw = entropy_b - entropy_a
    diff_filt = entropy_b_filt - entropy_a
    
    print(f"Differenz (Raw): {diff_raw:.4f}")
    print(f"Differenz (Bereinigt): {diff_filt:.4f}")

if __name__ == "__main__":
    analyze_entropy(mode="WORD")
    analyze_entropy(mode="POS")