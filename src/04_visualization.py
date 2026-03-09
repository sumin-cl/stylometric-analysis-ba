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