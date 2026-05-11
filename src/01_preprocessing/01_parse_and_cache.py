import pandas as pd
import json
from utils.paths import PROCESSED_FULL, PROCESSED_SAMPLES, PROCESSED_FILTERED, \
                        PARSED_FULL, PARSED_SAMPLES, PARSED_FILTERED
from utils.nlp_utils import analyze_syntax_complexity


def cache_parse_depths():
    """Vollkorpus (alle Tokenlängen) — optional, nicht im Launcher."""
    for corpus in ["corpus_a_cleaned.csv", "corpus_b_cleaned.csv"]:
        df = pd.read_csv(PROCESSED_FULL / corpus)
        depths = analyze_syntax_complexity(df["text"])
        out_path = PARSED_FULL / (corpus.replace(".csv", "_parsed_depths.json"))
        with open(out_path, "w") as f:
            json.dump(depths, f)
        print(f"Gespeichert: {out_path}")


def cache_parse_depths_downsampled(sample_num=1):
    for corpus in [f"sample{sample_num}_pre_n500.csv", f"sample{sample_num}_post_n500.csv"]:
        df = pd.read_csv(PROCESSED_SAMPLES / corpus)
        depths = analyze_syntax_complexity(df["text"])
        out_path = PARSED_SAMPLES / (corpus.replace(".csv", "_parsed_depths.json"))
        with open(out_path, "w") as f:
            json.dump(depths, f)
        print(f"Gespeichert: {out_path}")


def cache_parse_depths_filtered():
    """Reddit-Korpora nach Token-Filter (Primaeranalyse-Layer)."""
    for corpus in ["corpus_a_filtered.csv", "corpus_b_filtered.csv"]:
        df = pd.read_csv(PROCESSED_FILTERED / corpus)
        depths = analyze_syntax_complexity(df["text"])
        out_path = PARSED_FILTERED / (corpus.replace(".csv", "_parsed_depths.json"))
        with open(out_path, "w") as f:
            json.dump(depths, f)
        print(f"Gespeichert: {out_path}")


def cache_parse_depths_llm():
    corpus = "corpus_c_filtered.csv"
    df = pd.read_csv(PROCESSED_FILTERED / corpus)
    depths = analyze_syntax_complexity(df["text"])
    out_path = PARSED_FILTERED / "corpus_c_filtered_parsed_depths.json"
    with open(out_path, "w") as f:
        json.dump(depths, f)
    print(f"Gespeichert: {out_path}")


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        cache_parse_depths()
    elif mode == "filtered":
        cache_parse_depths_filtered()
    elif mode == "llm":
        cache_parse_depths_llm()
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        cache_parse_depths_downsampled(sample_num=sample)