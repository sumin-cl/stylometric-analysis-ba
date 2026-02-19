# src/03_analysis.py
import pandas as pd
from collections import Counter
from lexical_diversity import lex_div as ld

def mtld_analysis():
    df_a = pd.read_csv("data/final/corpus_a_clean.csv")
    df_b = pd.read_csv("data/final/corpus_b_clean.csv")

    # Downsampling für fairen Vergleich
    size = min(len(df_a), len(df_b))
    df_a = df_a.sample(n=size, random_state=42)
    df_b = df_b.sample(n=size, random_state=42)

    # Token-Listen vorbereiten
    tokens_a = " ".join(df_a['text'].astype(str)).lower().split()
    tokens_b = " ".join(df_b['text'].astype(str)).lower().split()

    # 1. Standard MTLD
    mtld_a = ld.mtld(tokens_a)
    mtld_b = ld.mtld(tokens_b)

    # 2. Vocab Intersection (min_freq=3)
    vocab_a = {w for w, c in Counter(tokens_a).items() if c >= 3}
    tokens_b_filtered = [t for t in tokens_b if t in vocab_a]
    mtld_b_filt = ld.mtld(tokens_b_filtered)

    print(f"Ergebnisse (N={size}):")
    print(f"MTLD A (19-21): {mtld_a:.2f}")
    print(f"MTLD B (Raw):    {mtld_b:.2f}")
    print(f"MTLD B (Filt):   {mtld_b_filt:.2f} (Differenz zu A: {mtld_b_filt - mtld_a:.2f})")

    meta = {
    "sample_size": size,
    "mode": "mtld",
    "source_files": ["corpus_a_clean.csv", "corpus_b_clean.csv"]
    }
    res = {
        "mtld_a_standard": mtld_a,
        "mtld_b_standard": mtld_b,
        "mtld_b_filtered": mtld_b_filt,
        "diff_mtld_filtered": mtld_b_filt - mtld_a
    }
    from nlp_utils import save_as_json
    save_as_json(f"mtld_alignment_results.json", meta, res)

if __name__ == "__main__":
    mtld_analysis()