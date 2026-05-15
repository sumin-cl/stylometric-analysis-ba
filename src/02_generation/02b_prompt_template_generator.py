import json
import random
from pathlib import Path
import pandas as pd

from utils.paths import GENERATED_TOPICS, GENERATED_PROMPTS

# ---------------------------------------------------------
# Seed Loader
# ---------------------------------------------------------

def load_seeds():
    topic_files = sorted(GENERATED_TOPICS.glob("*_topics.csv"))
    print(f"Lade Topic-Dateien aus {GENERATED_TOPICS}/  ({len(topic_files)} gefunden)")
    seeds = []

    for f in topic_files:
        df = pd.read_csv(f)
        n_before = len(seeds)
        for row in df["tokens"]:
            try:
                toks = json.loads(row)
                if isinstance(toks, list):
                    seeds.append(toks)
            except json.JSONDecodeError:
                pass
        print(f"  {f.name}: +{len(seeds) - n_before} seeds")

    return seeds


# ---------------------------------------------------------
# Templates
# ---------------------------------------------------------

TEMPLATES_A = [
    "Write a short analytical paragraph discussing the following machine learning concepts: {seeds}. Keep the tone neutral and abstract.",
    "Produce a concise explanation that connects these ML-related ideas: {seeds}. Avoid specific datasets or models.",
    "Generate a brief technical reflection on the themes represented by: {seeds}. Maintain an academic-neutral style."
]

TEMPLATES_B = [
    "Write a Reddit-style post where someone casually discusses issues or thoughts related to: {seeds}. Keep it informal.",
    "Generate a short Reddit-like question or opinion about: {seeds}. Use a conversational tone.",
    "Create a casual Reddit-style comment reflecting on experiences with: {seeds}.",
    "Write a short informal post that mentions challenges or insights about: {seeds}. Keep it natural."
]

TEMPLATES_C = [
    "Write a short research-abstract-style paragraph that conceptually relates: {seeds}. Keep it formal.",
    "Produce a concise academic-style summary discussing: {seeds}. Avoid references to real papers.",
    "Generate a structured, abstract-like explanation focusing on: {seeds}. Maintain a scientific tone."
]


# ---------------------------------------------------------
# Prompt Generator
# ---------------------------------------------------------

def generate_prompt(style, seeds):
    if style == "A":
        template = random.choice(TEMPLATES_A)
    elif style == "B":
        template = random.choice(TEMPLATES_B)
    elif style == "C":
        template = random.choice(TEMPLATES_C)
    else:
        raise ValueError("Unknown style")

    return template.format(seeds=", ".join(seeds))


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python 02b_prompt_template_generator.py <style A/B/C> <count>")
        return

    style = sys.argv[1].upper()
    count = int(sys.argv[2])

    seeds_pool = load_seeds()
    if not seeds_pool:
        print("No seeds found.")
        return

    print(f"Total seeds im Pool: {len(seeds_pool)}")

    out_dir = GENERATED_PROMPTS
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"prompts_style_{style}_{count}.jsonl"

    with open(out_path, "w", encoding="utf-8") as f:
        for _ in range(count):
            seed_list = random.choice(seeds_pool)
            prompt = generate_prompt(style, seed_list)
            f.write(json.dumps({"style": style, "seeds": seed_list, "prompt": prompt}) + "\n")

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()