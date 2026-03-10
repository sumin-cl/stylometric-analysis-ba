# src/03_analysis/03_shannon.py
import pandas as pd
from utils.nlp_utils import save_as_json, get_flat_tokens, get_pos_tags, downsample_corpora, calculate_shannon_entropy, filter_list_by_reference
from utils.paths import FINAL

def analyze_entropy_per_post(df, mode):
    entropies = []
    for text in df["text"]:
        if mode == "WORD":
            tokens = get_flat_tokens(pd.Series([text]), use_tqdm=False)
        else:
            tokens = get_pos_tags(pd.Series([text]))
        entropies.append(calculate_shannon_entropy(tokens))
    return entropies

def analyze_entropy(mode="WORD"):
    """
    mode: "WORD" für Wort-Entropie, "POS" für Grammatik-Entropie.
    Berechnet globale Entropie und dokumentweise Entropie.
    """
    print(f"\n=== STARTE ENTROPIE-ANALYSE: {mode} ===")
    path_a = FINAL / "corpus_a_cleaned.csv"
    path_b = FINAL / "corpus_b_cleaned.csv"

    df_a, df_b, size = downsample_corpora(path_a, path_b)

    if mode == "WORD":
        list_a = get_flat_tokens(df_a['text'])
        list_b = get_flat_tokens(df_b['text'])
    elif mode == "POS":
        list_a = get_pos_tags(df_a['text'])
        list_b = get_pos_tags(df_b['text'])
    
    entropy_a = calculate_shannon_entropy(list_a)
    entropy_b = calculate_shannon_entropy(list_b)
    
    print(f"Entropie A ({mode}): {entropy_a:.4f}")
    print(f"Entropie B ({mode}): {entropy_b:.4f}")
    
    print("Filtere B basierend auf A (einseitiges Alignment)...")
    min_freq = 3 if mode == "WORD" else 1
    list_b_filtered = filter_list_by_reference(list_b, list_a, min_freq=min_freq)
        
    entropy_b_filt = calculate_shannon_entropy(list_b_filtered)
    print(f"Entropie B (Filtered): {entropy_b_filt:.4f}")
    
    diff_raw = entropy_b - entropy_a
    diff_filt = entropy_b_filt - entropy_a
    
    print(f"Differenz (Raw): {diff_raw:.4f}")
    print(f"Differenz (Bereinigt): {diff_filt:.4f}")

    meta = {
        "sample_size": size,
        "mode": mode,
        "source_files": [str(path_a), str(path_b)]
    }
    res_global = {
        "entropy_a": float(entropy_a),
        "entropy_b": float(entropy_b),
        "diff_entropy_raw": float(diff_raw),
        "diff_entropy_filtered": float(diff_filt)
    }

    save_as_json(f"entropy_{mode.lower()}.json", meta, res_global)

    df_a["entropy_post"] = analyze_entropy_per_post(df_a, mode)
    df_b["entropy_post"] = analyze_entropy_per_post(df_b, mode)

    res_posts = {
        "entropy_per_post_a": df_a["entropy_post"].tolist(),
        "entropy_per_post_b": df_b["entropy_post"].tolist()
    }

    save_as_json(f"entropy/entropy_per_post_{mode.lower()}.json", meta, res_posts)


if __name__ == "__main__":
    analyze_entropy(mode="WORD")
    analyze_entropy(mode="POS")