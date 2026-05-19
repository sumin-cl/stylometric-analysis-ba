"""
Visualisierungen aller Stylometrie-Befunde.

Liest aus den finalen JSONs in data/final/results/ und schreibt PNGs in
data/final/02_eda/plots/. Jeder Plot existiert in zwei Varianten:
A-vs-B (filtered) links, B-vs-C (LLM) rechts, damit der zentrale Befund --
Effektgroessen-Asymmetrie -- direkt visuell wird.

Verwendung:
    python src/04_visualization/04_visualization.py            # alle Plots
    python src/04_visualization/04_visualization.py effects    # nur Effektgroessen-Plot
    python src/04_visualization/04_visualization.py ptd        # nur PTD
    ...
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from utils.paths import (
    FINAL, PARSED_FILTERED,
    RESULTS_MTLD_FILTERED, RESULTS_MTLD_LLM,
    RESULTS_SHANNON_FILTERED, RESULTS_SHANNON_LLM,
    RESULTS_FWR_FILTERED, RESULTS_FWR_LLM,
    RESULTS_PTD_FILTERED, RESULTS_PTD_LLM,
)

sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)

PLOTS_DIR = FINAL / "02_eda" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

PALETTE = {
    "A": "#3a6ea5",   # blau:  Pre-2022 Reddit
    "B": "#c44536",   # rot:   Post-2022 Reddit
    "C": "#6a994e",   # gruen: LLM
}

EFFECT_BANDS = [0.1, 0.3, 0.5]  # negligible | small | medium | large


def _load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _r_rb(j):
    return j["results"].get("effect_size_r", float("nan"))


def _save(fig, name):
    out = PLOTS_DIR / name
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"  [PNG] {out}")
    plt.close(fig)


# ---------------------------------------------------------
# 1) Effect-size overview: das zentrale Bild der Thesis
# ---------------------------------------------------------
def plot_effect_sizes():
    print("[Plot] Effect sizes (|r_rb|) -- alle Metriken, beide Vergleiche")

    # Daten einsammeln
    metrics = ["MTLD", "Shannon WORD", "Shannon POS", "FWR untagged", "FWR tagged", "PTD"]

    filtered_sources = {
        "MTLD":         RESULTS_MTLD_FILTERED    / "mtld_chunks_filtered.json",
        "Shannon WORD": RESULTS_SHANNON_FILTERED / "entropy_word_filtered.json",
        "Shannon POS":  RESULTS_SHANNON_FILTERED / "entropy_pos_filtered.json",
        "FWR untagged": RESULTS_FWR_FILTERED     / "fwr_results_filtered.json",
        "FWR tagged":   RESULTS_FWR_FILTERED     / "fwr_results_tagged_filtered.json",
        "PTD":          RESULTS_PTD_FILTERED     / "syntax_parse_depth_filtered.json",
    }
    llm_sources = {
        "MTLD":         RESULTS_MTLD_LLM    / "mtld_chunks_llm.json",
        "Shannon WORD": RESULTS_SHANNON_LLM / "entropy_word_llm.json",
        "Shannon POS":  RESULTS_SHANNON_LLM / "entropy_pos_llm.json",
        "FWR untagged": RESULTS_FWR_LLM     / "fwr_results_llm.json",
        "FWR tagged":   RESULTS_FWR_LLM     / "fwr_results_tagged_llm.json",
        "PTD":          RESULTS_PTD_LLM     / "syntax_parse_depth_llm.json",
    }

    r_filtered = [abs(_r_rb(_load(filtered_sources[m]))) for m in metrics]
    r_llm      = [abs(_r_rb(_load(llm_sources[m])))      for m in metrics]

    x = np.arange(len(metrics))
    w = 0.4

    fig, ax = plt.subplots(figsize=(10, 5))
    b1 = ax.bar(x - w/2, r_filtered, w, label="A vs B  (diachronic)", color=PALETTE["A"])
    b2 = ax.bar(x + w/2, r_llm,      w, label="B vs C  (LLM)",        color=PALETTE["C"])

    # Effekt-Bands
    for level, label in zip(EFFECT_BANDS, ["small", "medium", "large"]):
        ax.axhline(level, color="grey", lw=0.8, ls="--", alpha=0.6)
        ax.text(len(metrics) - 0.4, level + 0.01, label, fontsize=9, color="grey")

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, rotation=15, ha="right")
    ax.set_ylabel(r"$|r_{rb}|$  (rank-biserial effect size)")
    ax.set_title("Effect-size comparison: diachronic drift vs LLM divergence")
    ax.legend(loc="upper left")
    ax.set_ylim(0, max(max(r_filtered), max(r_llm)) * 1.18)

    # Werte ueber den Balken
    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.008, f"{h:.2f}",
                    ha="center", va="bottom", fontsize=8)

    _save(fig, "01_effect_sizes.png")


# ---------------------------------------------------------
# 2) PTD distribution: violin + median strip
# ---------------------------------------------------------
def plot_ptd_distribution():
    print("[Plot] PTD: Verteilung der Baumtiefen pro Korpus")

    depths_a = _load(PARSED_FILTERED / "corpus_a_filtered_parsed_depths.json")
    depths_b = _load(PARSED_FILTERED / "corpus_b_filtered_parsed_depths.json")
    depths_c = _load(PARSED_FILTERED / "corpus_c_filtered_parsed_depths.json")

    fig, ax = plt.subplots(figsize=(8, 5))
    data = [depths_a, depths_b, depths_c]
    parts = ax.violinplot(data, positions=[0, 1, 2], showmeans=True, showmedians=False)

    colors = [PALETTE["A"], PALETTE["B"], PALETTE["C"]]
    for body, c in zip(parts["bodies"], colors):
        body.set_facecolor(c)
        body.set_alpha(0.55)
        body.set_edgecolor("black")

    means = [np.mean(d) for d in data]
    ax.scatter([0, 1, 2], means, color="black", zorder=3, s=30)
    for i, m in enumerate(means):
        ax.annotate(f"{m:.2f}", (i, m), textcoords="offset points",
                    xytext=(10, 0), fontsize=10, va="center")

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["A  (Pre-2022)", "B  (Post-2022)", "C  (LLM)"])
    ax.set_ylabel("Parse Tree Depth (mean per document)")
    ax.set_title("Distribution of parse tree depth per document")

    _save(fig, "02_ptd_violin.png")


# ---------------------------------------------------------
# 3) MTLD chunks: zwei Panels (filtered + llm) mit aligned-Vergleich
# ---------------------------------------------------------
def plot_mtld_chunks():
    print("[Plot] MTLD: Chunk-Verteilungen, raw vs vocab-aligned")

    f = _load(RESULTS_MTLD_FILTERED / "mtld_chunks_filtered.json")
    l = _load(RESULTS_MTLD_LLM      / "mtld_chunks_llm.json")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    # filtered: A vs B raw vs B aligned-to-A
    ax = axes[0]
    data = [f["results"]["mtld_chunks_a"],
            f["results"]["mtld_chunks_b"],
            f["results"]["mtld_chunks_b_filtered"]]
    labels = ["A", "B (raw)", "B (aligned to A)"]
    bp = ax.boxplot(data, labels=labels, patch_artist=True, showfliers=False)
    for patch, c in zip(bp["boxes"], [PALETTE["A"], PALETTE["B"], "#aa7e63"]):
        patch.set_facecolor(c)
        patch.set_alpha(0.65)
    ax.set_ylabel("MTLD (per 500-token chunk)")
    ax.set_title(f"A vs B (filtered)   $|r_{{rb}}|$ = {abs(_r_rb(f)):.3f}")
    ax.tick_params(axis="x", rotation=10)

    # llm: B vs C raw vs C aligned-to-B
    ax = axes[1]
    data = [l["results"]["mtld_chunks_b"],
            l["results"]["mtld_chunks_c"],
            l["results"]["mtld_chunks_c_filtered"]]
    labels = ["B", "C (raw)", "C (aligned to B)"]
    bp = ax.boxplot(data, labels=labels, patch_artist=True, showfliers=False)
    for patch, c in zip(bp["boxes"], [PALETTE["B"], PALETTE["C"], "#8a9d5a"]):
        patch.set_facecolor(c)
        patch.set_alpha(0.65)
    ax.set_title(f"B vs C (LLM)   $|r_{{rb}}|$ = {abs(_r_rb(l)):.3f}")
    ax.tick_params(axis="x", rotation=10)

    fig.suptitle("MTLD chunks: raw vs vocabulary-aligned")
    fig.tight_layout()

    _save(fig, "03_mtld_chunks.png")


# ---------------------------------------------------------
# 4) Shannon per-post entropy: zwei Panels (WORD und POS), KDE
# ---------------------------------------------------------
def plot_shannon_per_post():
    print("[Plot] Shannon: per-post Entropie, KDE-Verteilungen")

    sources = {
        "WORD": (RESULTS_SHANNON_FILTERED / "entropy_per_post_word_filtered.json",
                 RESULTS_SHANNON_LLM      / "entropy_per_post_word_llm.json"),
        "POS":  (RESULTS_SHANNON_FILTERED / "entropy_per_post_pos_filtered.json",
                 RESULTS_SHANNON_LLM      / "entropy_per_post_pos_llm.json"),
    }

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, mode in zip(axes, ["WORD", "POS"]):
        f_path, l_path = sources[mode]
        f = _load(f_path)
        l = _load(l_path)

        sns.kdeplot(f["results"]["entropy_per_post_a"], label="A (Pre-2022)",
                    fill=True, alpha=0.25, color=PALETTE["A"], ax=ax)
        sns.kdeplot(l["results"]["entropy_per_post_b"], label="B (Post-2022)",
                    fill=True, alpha=0.25, color=PALETTE["B"], ax=ax)
        sns.kdeplot(l["results"]["entropy_per_post_c"], label="C (LLM)",
                    fill=True, alpha=0.25, color=PALETTE["C"], ax=ax)

        ax.set_xlabel(f"Per-post Shannon entropy ({mode})")
        ax.set_ylabel("Density")
        ax.set_title(f"{mode}-level entropy")
        ax.legend()

    fig.suptitle("Shannon entropy distributions per document")
    fig.tight_layout()
    _save(fig, "04_shannon_per_post.png")


# ---------------------------------------------------------
# 5) FWR: Mittelwerte + Std, beide Varianten + beide Vergleiche
# ---------------------------------------------------------
def plot_fwr_means():
    print("[Plot] FWR: Mittelwerte mit Std, untagged + tagged")

    f_u = _load(RESULTS_FWR_FILTERED / "fwr_results_filtered.json")
    f_t = _load(RESULTS_FWR_FILTERED / "fwr_results_tagged_filtered.json")
    l_u = _load(RESULTS_FWR_LLM      / "fwr_results_llm.json")
    l_t = _load(RESULTS_FWR_LLM      / "fwr_results_tagged_llm.json")

    # Daten: 3 Korpora x 2 Varianten
    # Aus filtered nehmen wir A; B und C kommen aus LLM-Vergleich fuer Konsistenz mit den restl. Plots
    means = {
        "A": [f_u["results"]["mean_fwr_a"], f_t["results"]["mean_fwr_a"]],
        "B": [l_u["results"]["mean_fwr_b"], l_t["results"]["mean_fwr_b"]],
        "C": [l_u["results"]["mean_fwr_c"], l_t["results"]["mean_fwr_c"]],
    }
    stds = {
        "A": [f_u["results"]["std_fwr_a"], None],
        "B": [l_u["results"]["std_fwr_b"], None],
        "C": [l_u["results"]["std_fwr_c"], None],
    }

    x = np.arange(2)  # untagged, tagged
    w = 0.27

    fig, ax = plt.subplots(figsize=(8, 5))
    for i, c in enumerate(["A", "B", "C"]):
        offset = (i - 1) * w
        ax.bar(x + offset, means[c], w, label=c, color=PALETTE[c], alpha=0.85,
               yerr=[s if s is not None else 0 for s in stds[c]], capsize=4)

    ax.set_xticks(x)
    ax.set_xticklabels(["FWR untagged", "FWR tagged"])
    ax.set_ylabel("Mean function-word ratio")
    ax.set_title("Function-word ratio: mean per corpus (error bars: std, where available)")
    ax.legend(title="Corpus")

    _save(fig, "05_fwr_means.png")


# ---------------------------------------------------------
# 6) Length distribution (uebersichtshalber)
# ---------------------------------------------------------
def plot_length_distribution():
    """Optional: zeigt die Token-Laengen pro Korpus nach dem 100-400-Filter."""
    print("[Plot] Token-Laengen-Verteilung (filtered)")

    import pandas as pd
    from utils.paths import PROCESSED_FILTERED

    df_a = pd.read_csv(PROCESSED_FILTERED / "corpus_a_filtered.csv")
    df_b = pd.read_csv(PROCESSED_FILTERED / "corpus_b_filtered.csv")
    df_c = pd.read_csv(PROCESSED_FILTERED / "corpus_c_filtered.csv")

    len_a = df_a["text"].astype(str).str.split().str.len()
    len_b = df_b["text"].astype(str).str.split().str.len()
    len_c = df_c["text"].astype(str).str.split().str.len()

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.kdeplot(len_a, label=f"A (n={len(len_a)})", fill=True, alpha=0.25, color=PALETTE["A"], ax=ax)
    sns.kdeplot(len_b, label=f"B (n={len(len_b)})", fill=True, alpha=0.25, color=PALETTE["B"], ax=ax)
    sns.kdeplot(len_c, label=f"C (n={len(len_c)})", fill=True, alpha=0.25, color=PALETTE["C"], ax=ax)

    ax.set_xlim(100, 400)
    ax.set_xlabel("Token count per post")
    ax.set_ylabel("Density")
    ax.set_title("Post-length distribution after filtering (100--400 tokens)")
    ax.legend()
    _save(fig, "06_length_distribution.png")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
PLOTS = {
    "effects":  plot_effect_sizes,
    "ptd":      plot_ptd_distribution,
    "mtld":     plot_mtld_chunks,
    "shannon":  plot_shannon_per_post,
    "fwr":      plot_fwr_means,
    "length":   plot_length_distribution,
}


def run_all_plots():
    for name, fn in PLOTS.items():
        try:
            fn()
        except Exception as e:
            print(f"  [FEHLER bei {name}] {e}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        run_all_plots()
    elif target in PLOTS:
        PLOTS[target]()
    else:
        print(f"Unbekanntes Ziel: {target}")
        print(f"Verfuegbar: all, {', '.join(PLOTS.keys())}")
        sys.exit(1)
    print(f"\nFertig. Plots in: {PLOTS_DIR}")