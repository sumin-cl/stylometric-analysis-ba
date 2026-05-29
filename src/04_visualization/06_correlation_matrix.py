"""
Berechnet rangbasierte (Spearman) Korrelationen zwischen den fuenf Per-Doc-
Metriken (PTD, FWR untagged, FWR tagged, Shannon WORD, Shannon POS) je Korpus
und erzeugt drei Heatmaps nebeneinander (A | B | C).

MTLD ist NICHT enthalten: MTLD ist chunk-basiert (per 500-Token-Block, nicht
per Dokument) und liegt damit auf einer anderen Granularitaet. Eine gemeinsame
per-Dokument-Korrelationsmatrix waere methodisch unsauber.

Datenfluss (alles aus EINER Quelle, damit Reihenfolge garantiert aligned ist):
  - text + pos_tags : TAGGED_FILTERED/corpus_{letter}_filtered_tagged.csv
  - PTD             : PARSED_FILTERED/corpus_{letter}_filtered_parsed_depths.json
                      (1:1 zur filtered-CSV, gleiche Reihenfolge wie tagged-CSV)
  - FWR untagged    : live aus pos_tags
  - FWR tagged      : live aus pos_tags
  - Shannon WORD    : live aus text
  - Shannon POS     : live aus pos_tags

Outputs:
  - data/final/02_eda/plots/07_correlation_heatmap.png
  - data/final/results/correlation_matrices.csv  (lange Form: corpus, m1, m2, rho)

Verwendung (aus src/):
  python -m 04_visualization.06_correlation_matrix
"""
import json
from collections import Counter
from math import log2

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

from utils.paths import PARSED_FILTERED, TAGGED_FILTERED, FINAL

# --- POS-Tag-Mengen (konsistent mit Aggregator / FWR-Berechnung) -------------
CONTENT_TAGS = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
FUNC_TAGS    = {"ADP", "AUX", "CONJ", "CCONJ", "SCONJ", "DET", "PART", "PRON"}

METRIC_ORDER = ["PTD", "FWR_unt", "FWR_tag", "Sha_W", "Sha_P"]
METRIC_LABELS = {
    "PTD":     "PTD",
    "FWR_unt": "FWR (untag.)",
    "FWR_tag": "FWR (tag.)",
    "Sha_W":   "Shannon (W)",
    "Sha_P":   "Shannon (P)",
}


def shannon_entropy(tokens):
    """Shannon-Entropie einer Tokenliste, in Bit."""
    n = len(tokens)
    if n == 0:
        return 0.0
    counts = Counter(tokens)
    return -sum((c / n) * log2(c / n) for c in counts.values())


def per_doc_metrics(letter):
    """Lädt einen Korpus und berechnet alle fuenf Per-Doc-Metriken.
    Returns: DataFrame mit Spalten METRIC_ORDER, eine Zeile pro Dokument."""
    csv_path = TAGGED_FILTERED / f"corpus_{letter}_filtered_tagged.csv"
    ptd_path = PARSED_FILTERED / f"corpus_{letter}_filtered_parsed_depths.json"

    df = pd.read_csv(csv_path)
    depths = json.load(open(ptd_path))
    assert len(df) == len(depths), \
        f"Mismatch corpus_{letter}: tagged-csv={len(df)} vs depths={len(depths)}"

    rows = []
    for text, pos_string, ptd in zip(df["text"].astype(str),
                                      df["pos_tags"].astype(str),
                                      depths):
        pos_tokens = pos_string.split()
        word_tokens = text.lower().split()

        n_func = sum(1 for t in pos_tokens if t in FUNC_TAGS)
        n_cont = sum(1 for t in pos_tokens if t in CONTENT_TAGS)
        n_total = len(pos_tokens)

        fwr_unt = n_func / n_cont if n_cont > 0 else 0.0
        fwr_tag = n_func / n_total if n_total > 0 else 0.0
        sha_w   = shannon_entropy(word_tokens)
        sha_p   = shannon_entropy(pos_tokens)

        rows.append({
            "PTD": ptd,
            "FWR_unt": fwr_unt,
            "FWR_tag": fwr_tag,
            "Sha_W":   sha_w,
            "Sha_P":   sha_p,
        })

    return pd.DataFrame(rows, columns=METRIC_ORDER)


def spearman_matrix(df):
    """Paarweise Spearman-Korrelationen als DataFrame (Metric x Metric)."""
    n = len(METRIC_ORDER)
    mat = np.eye(n)
    for i, m1 in enumerate(METRIC_ORDER):
        for j, m2 in enumerate(METRIC_ORDER):
            if i < j:
                rho, _ = spearmanr(df[m1], df[m2])
                mat[i, j] = rho
                mat[j, i] = rho
    return pd.DataFrame(mat, index=METRIC_ORDER, columns=METRIC_ORDER)


def plot_three_heatmaps(matrices, labels, out_path):
    """matrices: dict {label: DataFrame}, drei Heatmaps nebeneinander."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    vmin, vmax = -1, 1

    for ax, label in zip(axes, labels):
        mat = matrices[label]
        im = ax.imshow(mat.values, cmap="RdBu_r", vmin=vmin, vmax=vmax)
        ax.set_xticks(range(len(METRIC_ORDER)))
        ax.set_yticks(range(len(METRIC_ORDER)))
        ax.set_xticklabels([METRIC_LABELS[m] for m in METRIC_ORDER],
                           rotation=45, ha="right", fontsize=9)
        ax.set_yticklabels([METRIC_LABELS[m] for m in METRIC_ORDER],
                           fontsize=9)
        ax.set_title(label, fontsize=11)
        # Zahlen ins Feld schreiben
        for i in range(len(METRIC_ORDER)):
            for j in range(len(METRIC_ORDER)):
                val = mat.values[i, j]
                color = "white" if abs(val) > 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color=color, fontsize=8)

    fig.suptitle("Spearman correlations between per-document metrics",
                 fontsize=12, y=1.02)
    fig.colorbar(im, ax=axes, shrink=0.7, label=r"Spearman $\rho$")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Heatmap gespeichert: {out_path}")


def main():
    corpora = {
        "A (Pre-2022)":  "a",
        "B (Post-2022)": "b",
        "C (LLM)":       "c",
    }

    print("Lade Korpora und berechne Per-Doc-Metriken...")
    per_doc = {}
    for label, letter in corpora.items():
        print(f"  {label}...")
        per_doc[label] = per_doc_metrics(letter)
        print(f"    n={len(per_doc[label])}")

    print("\nBerechne Spearman-Korrelationsmatrizen...")
    matrices = {label: spearman_matrix(df) for label, df in per_doc.items()}

    # CSV-Export (lange Form)
    long_rows = []
    for label, mat in matrices.items():
        for m1 in METRIC_ORDER:
            for m2 in METRIC_ORDER:
                long_rows.append({
                    "corpus": label,
                    "metric_1": m1,
                    "metric_2": m2,
                    "rho": mat.loc[m1, m2],
                })
    csv_path = FINAL / "results" / "correlation_matrices.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(long_rows).to_csv(csv_path, index=False)
    print(f"CSV gespeichert: {csv_path}")

    # Konsolen-Ueberblick
    print("\n--- Korrelationsmatrizen (Spearman) ---")
    for label, mat in matrices.items():
        print(f"\n{label}:")
        print(mat.round(3).to_string())

    # Plot
    plot_path = FINAL / "02_eda" / "plots" / "07_correlation_heatmap.png"
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    plot_three_heatmaps(matrices, list(corpora.keys()), plot_path)

    print("\nFertig.")


if __name__ == "__main__":
    main()