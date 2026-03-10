import seaborn as sns
import matplotlib.pyplot as plt
import json
from utils.paths import RESULTS
from pathlib import Path

sns.set_theme(style="whitegrid", context="talk")

def plot_entropy_distribution():
    path = RESULTS / "entropy_per_post_word.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entropy_a = data["results"]["entropy_per_post_a"]
    entropy_b = data["results"]["entropy_per_post_b"]

    sns.kdeplot(entropy_a, label="Pre-LLM (2019–21)", fill=True, alpha=0.3, color="blue")
    sns.kdeplot(entropy_b, label="Post-LLM (2023–25)", fill=True, alpha=0.3, color="red")

    plt.title("Distribution of Shannon Entropy (Vocabulary Intersection)")
    plt.xlabel("Entropy")
    plt.ylabel("Density")
    plt.legend()
    plt.show()

def plot_mtld_standard():
    path = RESULTS / "mtld_alignment_results.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mtld_a = data["results"]["mtld_a_standard"]
    mtld_b = data["results"]["mtld_b_standard"]
    mtld_b_filtered = data["results"]["mtld_b_filtered"]

    sns.barplot(
        x=[mtld_a, mtld_b, mtld_b_filtered],
        y=["A (Standard)", "B (Standard)", "B (Filtered)"]
    )

    plt.xlabel("MTLD")
    plt.title("MTLD Comparison")
    plt.show()

def plot_mtld_chunks_unfiltered():
    path = RESULTS / "mtld_chunks_results.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mtld_chunks_a = data["results"]["mtld_chunks_a"]
    mtld_chunks_b = data["results"]["mtld_chunks_b"]

    sns.boxplot(data=[mtld_chunks_a, mtld_chunks_b], orient="h")
    plt.yticks([0, 1], ["A", "B"])
    plt.xlabel("MTLD")
    plt.title("MTLD Distribution Across 500-Word Chunks (Unfiltered)")
    plt.show()

def plot_mtld_chunks_filtered():
    path = RESULTS / "mtld_chunks_results.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mtld_chunks_a = data["results"]["mtld_chunks_a"]
    mtld_chunks_b_filtered = data["results"]["mtld_chunks_b_filtered"]

    sns.boxplot(data=[mtld_chunks_a, mtld_chunks_b_filtered], orient="h")
    plt.yticks([0, 1], ["A", "B"])
    plt.xlabel("MTLD")
    plt.title("MTLD Distribution Across 500-Word Chunks (Filtered)")
    plt.show()

def run_all_plots():
    print("\n[Plot] Entropy Distribution…")
    plot_entropy_distribution()

    print("\n[Plot] MTLD Standard Comparison…")
    plot_mtld_standard()

    print("\n[Plot] MTLD Chunks (Unfiltered)…")
    plot_mtld_chunks_unfiltered()

    print("\n[Plot] MTLD Chunks (Filtered)…")
    plot_mtld_chunks_filtered()
