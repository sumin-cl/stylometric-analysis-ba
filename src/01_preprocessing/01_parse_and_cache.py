import pandas as pd
import json
from utils.paths import FINAL, PARSED, PROCESSED
from utils.nlp_utils import analyze_syntax_complexity

def cache_parse_depths():
    for corpus in ["corpus_a_cleaned.csv", "corpus_b_cleaned.csv"]:
        df = pd.read_csv(PROCESSED / corpus)
        depths = analyze_syntax_complexity(df["text"])

        out_path = PARSED / (corpus.replace(".csv", "_parsed_depths.json"))

        with open(out_path, "w") as f:
            json.dump(depths, f)

        print(f"Gespeichert: {out_path}")

def cache_parse_depths_downsampled():
    for corpus in ["sample1_pre_n500.csv", "sample1_post_n500.csv"]:
        df = pd.read_csv(PROCESSED / corpus)
        depths = analyze_syntax_complexity(df["text"])

        out_path = PARSED / (corpus.replace(".csv", "_parsed_depths.json"))

        with open(out_path, "w") as f:
            json.dump(depths, f)

        print(f"Gespeichert: {out_path}")

if __name__ == "__main__":
    cache_parse_depths_downsampled()
