# src/01_preprocessing/01b_filter.py
"""
Filtert die bereinigten Korpora auf ein Token-Fenster und speichert
die gefilterten Dateien als stabilen Pool fuer spaeteres Sampling.

Input:  data/final/01_processed/full/corpus_*_cleaned.csv
Output: data/final/01_processed/filtered/corpus_*_filtered.csv

Verwendung:
    python src/01_preprocessing/01b_filter.py           # Standard: 150-300
    python src/01_preprocessing/01b_filter.py 100 400   # Eigene Grenzen
"""
import sys
import pandas as pd
from utils.paths import PROCESSED_FULL, PROCESSED_FILTERED

CORPORA = {
    "pre":  "corpus_a_cleaned.csv",
    "post": "corpus_b_cleaned.csv",
}


def filter_corpora(min_tokens=150, max_tokens=300):
    print(f"\n=== FILTER: {min_tokens}–{max_tokens} Tokens ===\n")

    for name, filename in CORPORA.items():
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
        print(f"{name.upper()} ({filename})")
        print(f"  Gesamt: {total}  |  gefiltert: {kept} ({kept/total*100:.1f}%)")

        out = PROCESSED_FILTERED / f"corpus_{('a' if name == 'pre' else 'b')}_filtered.csv"
        df_filtered.to_csv(out, index=False)
        print(f"  Gespeichert: {out.name}\n")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        try:
            min_t, max_t = int(sys.argv[1]), int(sys.argv[2])
        except ValueError:
            print("[FEHLER] Argumente muessen Ganzzahlen sein.")
            sys.exit(1)
    elif len(sys.argv) == 1:
        min_t, max_t = 150, 300
    else:
        print("Verwendung: python 01b_filter.py [min_tokens max_tokens]")
        sys.exit(1)

    filter_corpora(min_t, max_t)
