# src/01_preprocessing/01b_filter.py
"""
Filtert die bereinigten Korpora auf ein Token-Fenster und speichert
die gefilterten Dateien als stabilen Pool fuer spaeteres Sampling.

Input:  data/final/01_processed/full/corpus_*_cleaned.csv
Output: data/final/01_processed/filtered/corpus_*_filtered.csv

Verwendung:
    python src/01_preprocessing/01b_filter.py                # Reddit A+B, Standard 100-400
    python src/01_preprocessing/01b_filter.py 150 300        # Reddit A+B, eigene Grenzen
    python src/01_preprocessing/01b_filter.py llm            # LLM (Corpus C), Standard 100-400
    python src/01_preprocessing/01b_filter.py llm 150 300    # LLM (Corpus C), eigene Grenzen
"""
import sys
import pandas as pd
from utils.paths import PROCESSED_FULL, PROCESSED_FILTERED

CORPORA_REDDIT = {
    "a": "corpus_a_cleaned.csv",
    "b": "corpus_b_cleaned.csv",
}
CORPORA_LLM = {
    "c": "corpus_c_cleaned.csv",
}


def filter_corpora(min_tokens=100, max_tokens=400, mode="reddit"):
    corpora = CORPORA_LLM if mode == "llm" else CORPORA_REDDIT
    print(f"\n=== FILTER ({mode}): {min_tokens}–{max_tokens} Tokens ===\n")

    for letter, filename in corpora.items():
        path = PROCESSED_FULL / filename
        if not path.exists():
            print(f"[SKIP] Nicht gefunden: {path}")
            continue

        df = pd.read_csv(path)
        df['token_count'] = df['text'].astype(str).str.split().str.len()
        df_filtered = df[(df['token_count'] >= min_tokens) &
                         (df['token_count'] <= max_tokens)].copy()
        df_filtered = df_filtered.drop(columns=['token_count'])

        total = len(df)
        kept  = len(df_filtered)
        print(f"corpus_{letter} ({filename})")
        print(f"  Gesamt: {total}  |  gefiltert: {kept} ({kept/total*100:.1f}%)")

        out = PROCESSED_FILTERED / f"corpus_{letter}_filtered.csv"
        df_filtered.to_csv(out, index=False)
        print(f"  Gespeichert: {out.name}\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = "reddit"
    if args and args[0] == "llm":
        mode = "llm"
        args = args[1:]

    if len(args) == 2:
        try:
            min_t, max_t = int(args[0]), int(args[1])
        except ValueError:
            print("[FEHLER] Token-Argumente muessen Ganzzahlen sein.")
            sys.exit(1)
    elif len(args) == 0:
        min_t, max_t = 100, 400
    else:
        print("Verwendung: python 01b_filter.py [llm] [min_tokens max_tokens]")
        sys.exit(1)

    filter_corpora(min_t, max_t, mode=mode)