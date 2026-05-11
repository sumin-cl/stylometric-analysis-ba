# src/01_preprocessing/01c_sampling.py
"""
Zieht 3 unabhaengige Samples a n=500 aus den gefilterten Korpora.

Input:  data/final/01_processed/filtered/corpus_*_filtered.csv
Output: data/final/01_processed/samples/sample{N}_{pre/post}_n500.csv

Verwendung:
    python src/01_preprocessing/01c_sampling.py
    python src/01_preprocessing/01c_sampling.py 300   # anderes n
"""
import sys
import pandas as pd
from utils.paths import PROCESSED_FILTERED, PROCESSED_SAMPLES

CORPORA = {
    "pre":  "corpus_a_filtered.csv",
    "post": "corpus_b_filtered.csv",
}

SEEDS    = [42, 43, 44]


def create_samples(target_n=500):
    print(f"\n=== SAMPLING: {len(SEEDS)} Samples a n={target_n} ===\n")

    for name, filename in CORPORA.items():
        path = PROCESSED_FILTERED / filename
        if not path.exists():
            print(f"[SKIP] Nicht gefunden: {path}")
            print(f"  -> Bitte zuerst 01b_filter.py ausfuehren.\n")
            continue

        df = pd.read_csv(path)
        total = len(df)
        print(f"{name.upper()} ({filename}) — {total} Posts verfuegbar")

        if total < target_n:
            print(f"  [FEHLER] Zu wenig Posts! Benoetigt: {target_n}\n")
            continue

        for i, seed in enumerate(SEEDS, start=1):
            sample = df.sample(n=target_n, random_state=seed)
            out    = PROCESSED_SAMPLES / f"sample{i}_{name}_n{target_n}.csv"
            sample.to_csv(out, index=False)
            print(f"  Sample {i} (seed={seed}): {out.name}")

        print()


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    create_samples(target_n=n)
