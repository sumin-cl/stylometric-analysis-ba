import pandas as pd
import json
from utils.paths import FINAL
from utils.nlp_utils import analyze_syntax_complexity

def cache_parse_depths():
    for corpus in ["corpus_a_cleaned.csv", "corpus_b_cleaned.csv"]:
        df = pd.read_csv(FINAL / corpus)
        depths = analyze_syntax_complexity(df["text"])

        out_path = FINAL / "parsed" / (corpus.replace(".csv", "_parsed_depths.json"))
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w") as f:
            json.dump(depths, f)

        print(f"Gespeichert: {out_path}")

if __name__ == "__main__":
    cache_parse_depths()
