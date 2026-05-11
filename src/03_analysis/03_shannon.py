# src/03_analysis/03_shannon.py
import pandas as pd
from utils.nlp_utils import nlp, save_as_json, get_flat_tokens, get_pos_tags, downsample_corpora, calculate_shannon_entropy, filter_list_by_reference
from utils.paths import FINAL, PROCESSED_FULL, PROCESSED_FILTERED, PROCESSED_SAMPLES, \
                        TAGGED_FULL, TAGGED_FILTERED, TAGGED_SAMPLES
from tqdm import tqdm


def _pos_list(df):
    """
    Liefert flache POS-Liste. Bevorzugt vor-getaggte 'pos_tags'-Spalte
    (schneller, konsistent mit FWR_tagged). Fallback: spaCy live auf df['text'].
    """
    if "pos_tags" in df.columns:
        tokens = []
        for pos_string in df["pos_tags"]:
            tokens.extend(str(pos_string).split())
        return tokens
    else:
        return get_pos_tags(df['text'])


def _resolve_paths(cleaned_a, cleaned_b, tagged_a, tagged_b):
    """
    Versucht, vor-getaggte CSVs zu nutzen (df hat dann 'pos_tags'-Spalte).
    Fallback auf cleaned CSVs, wenn tagged Files nicht existieren.
    Returns (path_a, path_b, tag_source).
    """
    if tagged_a.exists() and tagged_b.exists():
        print(f"[INFO] Verwende pre-getaggte POS-Tags ({tagged_a.parent.name}/).")
        return tagged_a, tagged_b, "pre_tagged"
    else:
        print(f"[WARN] Tagged Files nicht gefunden — spaCy live.")
        print(f"       Tip: vorab 01b_pos_tagger.py mit passendem Modus laufen lassen (Speedup ~5-10x).")
        return cleaned_a, cleaned_b, "spacy_live"

def analyze_entropy_per_post(df, mode):
    entropies = []
    if mode == "POS":
        if "pos_tags" in df.columns:
            for pos_string in tqdm(df["pos_tags"], desc="Entropie pro Post (POS, pre-tagged)"):
                tokens = str(pos_string).split()
                entropies.append(calculate_shannon_entropy(tokens))
        else:
            all_docs = list(nlp.pipe(df["text"].astype(str), batch_size=100, disable=["parser", "ner"]))
            for doc in tqdm(all_docs, desc="Entropie pro Post (POS, spaCy live)"):
                tokens = [token.pos_ for token in doc]
                entropies.append(calculate_shannon_entropy(tokens))
    else:
        for text in tqdm(df["text"], desc="Entropie pro Post (WORD)"):
            tokens = get_flat_tokens(pd.Series([text]), use_tqdm=False)
            entropies.append(calculate_shannon_entropy(tokens))
    return entropies

def analyze_entropy(mode="WORD"):
    """
    mode: "WORD" für Wort-Entropie, "POS" für Grammatik-Entropie.
    Berechnet globale Entropie und dokumentweise Entropie.
    """
    print(f"\n=== STARTE ENTROPIE-ANALYSE: {mode} ===")
    path_a, path_b, tag_source = _resolve_paths(
        PROCESSED_FULL / "corpus_a_cleaned.csv",
        PROCESSED_FULL / "corpus_b_cleaned.csv",
        TAGGED_FULL / "corpus_a_tagged.csv",
        TAGGED_FULL / "corpus_b_tagged.csv",
    )

    df_a, df_b, size = downsample_corpora(path_a, path_b)

    if mode == "WORD":
        list_a = get_flat_tokens(df_a['text'])
        list_b = get_flat_tokens(df_b['text'])
    elif mode == "POS":
        list_a = _pos_list(df_a)
        list_b = _pos_list(df_b)
    
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
        "tagging_source": tag_source,
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

def analyze_entropy_downsampled(mode="WORD", sample_num=1):
    """
    mode: "WORD" für Wort-Entropie, "POS" für Grammatik-Entropie.
    Liest direkt die vorbereiteten Samples aus PROCESSED.
    """
    print(f"\n=== STARTE ENTROPIE-ANALYSE: {mode} (Sample {sample_num}) ===")

    path_a, path_b, tag_source = _resolve_paths(
        PROCESSED_SAMPLES / f"sample{sample_num}_pre_n500.csv",
        PROCESSED_SAMPLES / f"sample{sample_num}_post_n500.csv",
        TAGGED_SAMPLES / f"sample{sample_num}_pre_n500_tagged.csv",
        TAGGED_SAMPLES / f"sample{sample_num}_post_n500_tagged.csv",
    )

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    size = len(df_a)  # Entspricht n=500

    if mode == "WORD":
        list_a = get_flat_tokens(df_a['text'])
        list_b = get_flat_tokens(df_b['text'])
    elif mode == "POS":
        list_a = _pos_list(df_a)
        list_b = _pos_list(df_b)
    
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
        "sample_num": sample_num,
        "tagging_source": tag_source,
        "source_files":[path_a.name, path_b.name]
    }
    res_global = {
        "entropy_a": float(entropy_a),
        "entropy_b": float(entropy_b),
        "diff_entropy_raw": float(diff_raw),
        "diff_entropy_filtered": float(diff_filt)
    }

    save_as_json(f"entropy_{mode.lower()}_sample{sample_num}.json", meta, res_global)

    df_a["entropy_post"] = analyze_entropy_per_post(df_a, mode)
    df_b["entropy_post"] = analyze_entropy_per_post(df_b, mode)

    res_posts = {
        "entropy_per_post_a": df_a["entropy_post"].tolist(),
        "entropy_per_post_b": df_b["entropy_post"].tolist()
    }

    save_as_json(f"entropy/entropy_per_post_{mode.lower()}_sample{sample_num}.json", meta, res_posts)


def analyze_entropy_filtered(mode="WORD"):
    """
    Berechnet Shannon-Entropie auf den token-laengen-gefilterten Reddit-Korpora
    (Primaeranalyse-Layer). Liest aus PROCESSED_FILTERED, subsampelt via
    downsample_corpora auf min(n_a, n_b). Berechnet globale Entropie + Per-Post-Werte
    (für spaetere Boxplots / Mann-Whitney).
    mode: "WORD" oder "POS".
    """
    print(f"\n=== STARTE ENTROPIE-ANALYSE: {mode} (Filtered) ===")

    path_a, path_b, tag_source = _resolve_paths(
        PROCESSED_FILTERED / "corpus_a_filtered.csv",
        PROCESSED_FILTERED / "corpus_b_filtered.csv",
        TAGGED_FILTERED / "corpus_a_filtered_tagged.csv",
        TAGGED_FILTERED / "corpus_b_filtered_tagged.csv",
    )

    df_a, df_b, size = downsample_corpora(path_a, path_b)

    if mode == "WORD":
        list_a = get_flat_tokens(df_a['text'])
        list_b = get_flat_tokens(df_b['text'])
    elif mode == "POS":
        list_a = _pos_list(df_a)
        list_b = _pos_list(df_b)

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
        "layer": "filtered",
        "tagging_source": tag_source,
        "source_files": [str(path_a), str(path_b)]
    }
    res_global = {
        "entropy_a": float(entropy_a),
        "entropy_b": float(entropy_b),
        "diff_entropy_raw": float(diff_raw),
        "diff_entropy_filtered": float(diff_filt)
    }

    save_as_json(f"entropy_{mode.lower()}_filtered.json", meta, res_global)

    df_a["entropy_post"] = analyze_entropy_per_post(df_a, mode)
    df_b["entropy_post"] = analyze_entropy_per_post(df_b, mode)

    res_posts = {
        "entropy_per_post_a": df_a["entropy_post"].tolist(),
        "entropy_per_post_b": df_b["entropy_post"].tolist()
    }

    save_as_json(f"entropy/entropy_per_post_{mode.lower()}_filtered.json", meta, res_posts)


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        analyze_entropy(mode="WORD")
        analyze_entropy(mode="POS")
    elif mode == "filtered":
        analyze_entropy_filtered(mode="WORD")
        analyze_entropy_filtered(mode="POS")
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        analyze_entropy_downsampled(mode="WORD", sample_num=sample)
        analyze_entropy_downsampled(mode="POS", sample_num=sample)