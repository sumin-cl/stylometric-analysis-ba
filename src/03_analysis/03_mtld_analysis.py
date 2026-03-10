# src/03_analysis.py
import pandas as pd
from collections import Counter
from lexical_diversity import lex_div as ld
from tqdm import tqdm

def chunk_tokens(tokens, chunk_size=500):
    """Teilt eine Tokenliste in gleich große Chunks auf."""
    for i in range(0, len(tokens), chunk_size):
        yield tokens[i:i + chunk_size]

def mtld_analysis(chunk_size=500):
    """
    Berechnet den MTLD-Wert (Measure of Textual Lexical Diversity) für beide Korpora.
    Zusätzlich wird ein vokabulargefilterter MTLD für Korpus B berechnet, der nur
    Typen enthält, die in Korpus A mindestens 3-mal vorkommen — zur Kontrolle des Topic-Shifts.
    Speichert alle drei MTLD-Werte und die gefilterte Differenz in mtld_alignment_results.json.
    """
    df_a = pd.read_csv("data/final/corpus_a_clean.csv")
    df_b = pd.read_csv("data/final/corpus_b_clean.csv")

    size = min(len(df_a), len(df_b))
    df_a = df_a.sample(n=size, random_state=42)
    df_b = df_b.sample(n=size, random_state=42)

    tokens_a = " ".join(df_a['text'].astype(str)).lower().split()
    tokens_b = " ".join(df_b['text'].astype(str)).lower().split()

    mtld_a = ld.mtld(tokens_a)
    mtld_b = ld.mtld(tokens_b)

    # min_freq=3 as occurence requirement
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
    from utils.nlp_utils import save_as_json
    save_as_json(f"mtld_alignment_results.json", meta, res)

    mtld_chunks_a = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_a, chunk_size), desc="MTLD Chunks A")]
    mtld_chunks_b = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_b, chunk_size), desc="MTLD Chunks B")]
    mtld_chunks_b_filtered = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_b_filtered, chunk_size), desc="MTLD Chunks B (Filtered)")]

    res_chunks = {
        "mtld_chunks_a": mtld_chunks_a,
        "mtld_chunks_b": mtld_chunks_b,
        "mtld_chunks_b_filtered": mtld_chunks_b_filtered
    }
    save_as_json(f"mtld_chunks_results.json", meta, res_chunks)

if __name__ == "__main__":
    mtld_analysis()