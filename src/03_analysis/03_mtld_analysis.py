# src/03_analysis/03_mtld_analysis.py
import pandas as pd
from collections import Counter
from lexical_diversity import lex_div as ld
from tqdm import tqdm
from utils.paths import FINAL, PROCESSED_FULL, PROCESSED_FILTERED, PROCESSED_SAMPLES, \
                        RESULTS_MTLD_FULL, RESULTS_MTLD_FILTERED, RESULTS_MTLD_SAMPLES
from utils.nlp_utils import save_as_json

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
    path_a = PROCESSED_FULL / "corpus_a_cleaned.csv"
    path_b = PROCESSED_FULL / "corpus_b_cleaned.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)

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
    "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mtld_a_standard": float(mtld_a),
        "mtld_b_standard": float(mtld_b),
        "mtld_b_filtered": float(mtld_b_filt),
        "diff_mtld_filtered": float(mtld_b_filt - mtld_a)
    }
    
    save_as_json("mtld_alignment_results.json", meta, res, output_dir=RESULTS_MTLD_FULL)

    mtld_chunks_a = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_a, chunk_size), desc="MTLD Chunks A")]
    mtld_chunks_b = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_b, chunk_size), desc="MTLD Chunks B")]
    mtld_chunks_b_filtered = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_b_filtered, chunk_size), desc="MTLD Chunks B (Filtered)")]

    res_chunks = {
        "mtld_chunks_a": mtld_chunks_a,
        "mtld_chunks_b": mtld_chunks_b,
        "mtld_chunks_b_filtered": mtld_chunks_b_filtered
    }
    save_as_json("mtld_chunks_results.json", meta, res_chunks, output_dir=RESULTS_MTLD_FULL)

def mtld_analysis_downsampled(sample_num=1, chunk_size=500):
    """
    Berechnet MTLD für vorbereitete Downsampling-Samples (n=500, 150-300 Tokens).
    Analog zu mtld_analysis(), aber ohne internes Sampling — die Samples sind bereits
    balanciert und gefiltert. Berechnet zusätzlich einen vokabulargefilterten MTLD
    für Korpus B (nur Typen mit min. 3 Vorkommen in A) zur Kontrolle des Topic-Shifts.
    Speichert globale Ergebnisse in mtld_results_sample{sample_num}.json und
    Chunk-Werte in mtld_chunks_sample{sample_num}.json.
    """
    print(f"\n=== STARTE MTLD-ANALYSE (Sample {sample_num}) ===")
 
    path_a = PROCESSED_SAMPLES / f"sample{sample_num}_pre_n500.csv"
    path_b = PROCESSED_SAMPLES / f"sample{sample_num}_post_n500.csv"
 
    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    size = len(df_a)  # n=500
 
    tokens_a = " ".join(df_a['text'].astype(str)).lower().split()
    tokens_b = " ".join(df_b['text'].astype(str)).lower().split()
 
    mtld_a = ld.mtld(tokens_a)
    mtld_b = ld.mtld(tokens_b)
 
    vocab_a = {w for w, c in Counter(tokens_a).items() if c >= 3}
    tokens_b_filtered = [t for t in tokens_b if t in vocab_a]
    mtld_b_filt = ld.mtld(tokens_b_filtered)
 
    print(f"Ergebnisse (Sample {sample_num}, N={size}):")
    print(f"MTLD A (Pre):    {mtld_a:.2f}")
    print(f"MTLD B (Raw):    {mtld_b:.2f}")
    print(f"MTLD B (Filt):   {mtld_b_filt:.2f} (Differenz zu A: {mtld_b_filt - mtld_a:.2f})")
 
    meta = {
        "sample_size": size,
        "sample_num": sample_num,
        "mode": "mtld",
        "source_files": [path_a.name, path_b.name]
    }
    res = {
        "mtld_a_standard": float(mtld_a),
        "mtld_b_standard": float(mtld_b),
        "mtld_b_filtered": float(mtld_b_filt),
        "diff_mtld_filtered": float(mtld_b_filt - mtld_a)
    }
    save_as_json(f"mtld_results_sample{sample_num}.json", meta, res, output_dir=RESULTS_MTLD_SAMPLES)
 
    mtld_chunks_a = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_a, chunk_size), desc="MTLD Chunks A")]
    mtld_chunks_b = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_b, chunk_size), desc="MTLD Chunks B")]
    mtld_chunks_b_filtered = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_b_filtered, chunk_size), desc="MTLD Chunks B (Filt)")]
 
    res_chunks = {
        "mtld_chunks_a": mtld_chunks_a,
        "mtld_chunks_b": mtld_chunks_b,
        "mtld_chunks_b_filtered": mtld_chunks_b_filtered
    }
    save_as_json(f"mtld_chunks_sample{sample_num}.json", meta, res_chunks, output_dir=RESULTS_MTLD_SAMPLES)


def mtld_analysis_filtered(chunk_size=500):
    """
    Berechnet MTLD auf den token-laengen-gefilterten Reddit-Korpora (Primaeranalyse-Layer).
    Liest aus PROCESSED_FILTERED, subsampelt auf min(n_a, n_b) fuer Vergleichbarkeit.
    Berechnet zusaetzlich vokabulargefilterten MTLD fuer Korpus B (Topic-Shift-Kontrolle).
    Speichert globale Ergebnisse in mtld_alignment_filtered.json und
    Chunk-Werte in mtld_chunks_filtered.json.
    """
    print(f"\n=== STARTE MTLD-ANALYSE (Filtered) ===")

    path_a = PROCESSED_FILTERED / "corpus_a_filtered.csv"
    path_b = PROCESSED_FILTERED / "corpus_b_filtered.csv"

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)

    size = min(len(df_a), len(df_b))
    df_a = df_a.sample(n=size, random_state=42)
    df_b = df_b.sample(n=size, random_state=42)

    tokens_a = " ".join(df_a['text'].astype(str)).lower().split()
    tokens_b = " ".join(df_b['text'].astype(str)).lower().split()

    mtld_a = ld.mtld(tokens_a)
    mtld_b = ld.mtld(tokens_b)

    vocab_a = {w for w, c in Counter(tokens_a).items() if c >= 3}
    tokens_b_filtered = [t for t in tokens_b if t in vocab_a]
    mtld_b_filt = ld.mtld(tokens_b_filtered)

    print(f"Ergebnisse (Filtered, N={size}):")
    print(f"MTLD A (Pre):    {mtld_a:.2f}")
    print(f"MTLD B (Raw):    {mtld_b:.2f}")
    print(f"MTLD B (Filt):   {mtld_b_filt:.2f} (Differenz zu A: {mtld_b_filt - mtld_a:.2f})")

    meta = {
        "sample_size": size,
        "mode": "mtld_filtered",
        "source_files": [str(path_a), str(path_b)]
    }
    res = {
        "mtld_a_standard": float(mtld_a),
        "mtld_b_standard": float(mtld_b),
        "mtld_b_filtered": float(mtld_b_filt),
        "diff_mtld_filtered": float(mtld_b_filt - mtld_a)
    }
    save_as_json("mtld_alignment_filtered.json", meta, res, output_dir=RESULTS_MTLD_FILTERED)

    mtld_chunks_a = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_a, chunk_size), desc="MTLD Chunks A (Filt)")]
    mtld_chunks_b = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_b, chunk_size), desc="MTLD Chunks B (Filt)")]
    mtld_chunks_b_filtered = [ld.mtld(chunk) for chunk in tqdm(chunk_tokens(tokens_b_filtered, chunk_size), desc="MTLD Chunks B (Filt+Vocab)")]

    res_chunks = {
        "mtld_chunks_a": mtld_chunks_a,
        "mtld_chunks_b": mtld_chunks_b,
        "mtld_chunks_b_filtered": mtld_chunks_b_filtered
    }
    save_as_json("mtld_chunks_filtered.json", meta, res_chunks, output_dir=RESULTS_MTLD_FILTERED)


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        mtld_analysis()
    elif mode == "filtered":
        mtld_analysis_filtered()
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        mtld_analysis_downsampled(sample_num=sample)