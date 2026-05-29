"""
Findet repraesentative Beispiel-Posts pro Korpus fuer das Thesis-Satzbeispiel.

Datengetrieben statt augenschein-basiert: waehlt Posts, deren Metrikprofil
typisch fuer ihr Korpus ist (nahe am Korpus-Median in mehreren Metriken
gleichzeitig), nicht Posts, die "menschlich" oder "maschinell" klingen.

Anker ist PTD: die parsed_depths-Cache-Liste ist 1:1 zur filtered-CSV
(kein Sampling), daher koennen Post-Text und PTD per Zeilenindex sauber
verknuepft werden. FWR wird live nachgerechnet, Shannon per-post optional.

Verwendung:
    python src/04_visualization/05_example_pairs.py          # B vs C (Standard)
    python src/04_visualization/05_example_pairs.py --pair ab # A vs B
    python src/04_visualization/05_example_pairs.py --n 5     # mehr Kandidaten
"""
import json
import sys
import argparse

import numpy as np
import pandas as pd
import spacy

from utils.paths import PARSED_FILTERED, PROCESSED_FILTERED

CONTENT_TAGS = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
FUNC_TAGS    = {"ADP", "AUX", "CONJ", "CCONJ", "SCONJ", "DET", "PART", "PRON"}


def load_corpus(letter):
    """Laedt CSV + PTD-Cache (1:1 zur CSV) und gibt einen DataFrame mit
    Spalten text, ptd, token_len zurueck."""
    df = pd.read_csv(PROCESSED_FILTERED / f"corpus_{letter}_filtered.csv")
    depths = json.load(open(PARSED_FILTERED / f"corpus_{letter}_filtered_parsed_depths.json"))
    assert len(df) == len(depths), \
        f"Mismatch corpus_{letter}: df={len(df)} vs depths={len(depths)}"
    df = df.reset_index(drop=True)
    df["ptd"] = depths
    df["token_len"] = df["text"].astype(str).str.split().str.len()
    return df


def add_fwr(df, nlp):
    """FWR untagged (Funktions-/Inhaltswoerter) pro Post, live berechnet."""
    fwr = []
    for doc in nlp.pipe(df["text"].astype(str), batch_size=100):
        n_func = sum(1 for t in doc if t.pos_ in FUNC_TAGS)
        n_cont = sum(1 for t in doc if t.pos_ in CONTENT_TAGS)
        fwr.append(n_func / n_cont if n_cont > 0 else 0.0)
    df["fwr"] = fwr
    return df


def typicality_score(df, metrics):
    """Wie typisch ist jeder Post fuer sein Korpus? Summe der absoluten
    z-Scores ueber die gewaehlten Metriken; niedrig = nahe am Korpus-Zentrum
    in ALLEN Metriken gleichzeitig."""
    score = np.zeros(len(df))
    for m in metrics:
        vals = df[m].to_numpy(dtype=float)
        std = vals.std(ddof=0)
        if std > 0:
            score += np.abs((vals - vals.mean()) / std)
    return score


def find_representatives(df, metrics, n=3, len_range=None):
    """Gibt die n typischsten Posts zurueck, optional auf ein Laengenfenster
    eingeschraenkt (fuer faire Paar-Vergleichbarkeit)."""
    sub = df
    if len_range:
        lo, hi = len_range
        sub = df[(df["token_len"] >= lo) & (df["token_len"] <= hi)].copy()
    sub = sub.copy()
    sub["typicality"] = typicality_score(sub, metrics)
    return sub.nsmallest(n, "typicality")


def print_corpus_profile(df, label, metrics):
    print(f"\n=== {label} (n={len(df)}) — Korpus-Mediane ===")
    for m in metrics:
        print(f"  {m:12s}: median={df[m].median():.3f}  mean={df[m].mean():.3f}")


def show_candidates(cands, label, metrics):
    print(f"\n--- {label}: {len(cands)} typischste Kandidaten ---")
    for rank, (_, row) in enumerate(cands.iterrows(), 1):
        print(f"\n[{label} #{rank}]  token_len={int(row['token_len'])}")
        for m in metrics:
            print(f"    {m:12s} = {row[m]:.3f}")
        text = str(row["text"]).replace("\n", " ").strip()
        preview = text[:400] + ("..." if len(text) > 400 else "")
        print(f"    text: {preview}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", choices=["bc", "ab"], default="bc",
                    help="bc = B vs C (Mensch vs LLM, Standard), ab = A vs B")
    ap.add_argument("--n", type=int, default=3, help="Kandidaten pro Korpus")
    args = ap.parse_args()

    metrics = ["ptd", "fwr"]   # erweiterbar um shannon, falls verknuepft

    print("Lade spaCy (fuer FWR)...")
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

    if args.pair == "bc":
        left_letter, left_label   = "b", "B (Post-2022 Reddit)"
        right_letter, right_label = "c", "C (gpt-4o)"
    else:
        left_letter, left_label   = "a", "A (Pre-2022 Reddit)"
        right_letter, right_label = "b", "B (Post-2022 Reddit)"

    print(f"Lade Korpus {left_letter.upper()}...")
    df_left = add_fwr(load_corpus(left_letter), nlp)
    print(f"Lade Korpus {right_letter.upper()}...")
    df_right = add_fwr(load_corpus(right_letter), nlp)

    print_corpus_profile(df_left, left_label, metrics)
    print_corpus_profile(df_right, right_label, metrics)

    # Gemeinsames Laengenfenster: ueberlappender Interquartilsbereich,
    # damit das Paar nicht durch Laengenunterschiede verzerrt ist.
    lo = int(max(df_left["token_len"].quantile(0.25),
                 df_right["token_len"].quantile(0.25)))
    hi = int(min(df_left["token_len"].quantile(0.75),
                 df_right["token_len"].quantile(0.75)))
    print(f"\nGemeinsames Laengenfenster fuer faire Paarung: {lo}-{hi} Tokens")

    cands_left  = find_representatives(df_left,  metrics, n=args.n, len_range=(lo, hi))
    cands_right = find_representatives(df_right, metrics, n=args.n, len_range=(lo, hi))

    show_candidates(cands_left,  left_label,  metrics)
    show_candidates(cands_right, right_label, metrics)

    print("\n" + "=" * 60)
    print("Waehle je einen Post aus den Kandidaten manuell aus.")
    print("Empfehlung: aehnliche token_len, klarer PTD/FWR-Kontrast,")
    print("inhaltlich unverfaenglich (kein PII, kein sensibler Inhalt).")


if __name__ == "__main__":
    main()