import seaborn as sns
import matplotlib.pyplot as plt
import json

with open("data/final/results/entropy_per_post_word.json") as f:
    data = json.load(f)

entropy_a = data["results"]["entropy_per_post_a"]
entropy_b = data["results"]["entropy_per_post_b"]

sns.kdeplot(entropy_a, label="Pre-LLM (2019-21)", fill=True, alpha=0.3, color="blue")
sns.kdeplot(entropy_b, label="Post-LLM (2023-25)", fill=True, alpha=0.3, color="red")

plt.title("Distribution of Shannon Entropy (Vocabulary Intersection)")
plt.xlabel("Entropy")
plt.ylabel("Density")
plt.legend()
plt.show()

with open("data/final/results/mtld_alignment_results.json") as f:
    data = json.load(f)

mtld_a = data["results"]["mtld_a_standard"]
mtld_b = data["results"]["mtld_b_standard"]
mtld_b_filtered = data["results"]["mtld_b_filtered"]
labels = ["A (Standard)", "B (Standard)", "B (Filtered)"]

sns.barplot(x=[mtld_a, mtld_b, mtld_b_filtered], y=labels)
plt.xlabel("MTLD")
plt.title("MTLD Comparison")
plt.show()

with open("data/final/results/mtld_chunks_results.json") as f:
    data = json.load(f)

mtld_chunks_a = data["results"]["mtld_chunks_a"]
mtld_chunks_b = data["results"]["mtld_chunks_b"]
mtld_chunks_b_filtered = data["results"]["mtld_chunks_b_filtered"]

sns.boxplot(data=[mtld_chunks_a, mtld_chunks_b], orient="h")
plt.yticks([0, 1], ["A", "B"])
plt.xlabel("MTLD")
plt.title("MTLD Distribution Across 500-Word Chunks (Unfiltered)")
plt.show()

sns.boxplot(data=[mtld_chunks_a, mtld_chunks_b_filtered], orient="h")
plt.yticks([0, 1], ["A", "B"])
plt.xlabel("MTLD")
plt.title("MTLD Distribution Across 500-Word Chunks (Filtered)")
plt.show()