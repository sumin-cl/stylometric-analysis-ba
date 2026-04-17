import pandas as pd
import spacy
import json

from utils.paths import PROCESSED, GENERATED
from pathlib import Path

from tqdm import tqdm

NLP = spacy.load("en_core_web_sm")

def extract_topics(text, max_tokens=8):
    doc = NLP(text)

    nouns = [t.lemma_ for t in doc if t.pos_ in ("NOUN", "PROPN")]
    adjs  = [t.lemma_ for t in doc if t.pos_ == "ADJ"]

    raw_tokens = nouns + adjs

    filtered = [t for t in raw_tokens if is_valid_seed(t)]

    tokens = filtered[:max_tokens]

    return nouns, adjs, tokens

def process_file(input_name, output_name=None):    
    input_path = PROCESSED / input_name

    source = input_name
    sample_id = None
    if input_name.startswith("sample"):
        sample_id = int(input_name.split("_")[0].replace("sample", ""))

    if output_name is None:
        stem = Path(input_name).stem.replace("_cleaned", "")
        output_name = f"{stem}_topics.csv"

    print(f"--- Starte Topic Extraction für {input_path} ---")
    df = pd.read_csv(input_path)
    print(f"Verarbeite: {input_path.name} ({len(df)} Einträge)")
    nouns_list = []
    adjs_list = []
    tokens_list = []

    for text in tqdm(df["text"].astype(str), desc="Extrahiere Topics"):
        nouns, adjs, tokens = extract_topics(text)
        nouns_list.append(json.dumps(nouns))
        adjs_list.append(json.dumps(adjs))
        tokens_list.append(json.dumps(tokens))

    df_out = pd.DataFrame({
        "id": range(len(df)),
        "source": source,
        "sample_id": sample_id,
        "nouns": nouns_list,
        "adjectives": adjs_list,
        "tokens": tokens_list
    })

    out_path = GENERATED / output_name
    df_out.to_csv(out_path, index=False)
    print(f"Gespeichert: {out_path.name}")

import re

def is_valid_seed(tok: str) -> bool:
    # blacklist: digits, punctuation, model names, hardware, code
    if re.search(r"\d|=|\.|/|\\|[A-Z]{2,}|[A-Z]\d", tok):
        return False

    # whitelist: alphabetic, lowercase, length > 2
    if not tok.isalpha():
        return False
    if not tok.islower():
        return False
    if len(tok) <= 2:
        return False

    return True

def main():
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        process_file("corpus_a_cleaned.csv")
        process_file("corpus_b_cleaned.csv")
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        process_file(f"sample{sample}_pre_n500.csv")
        process_file(f"sample{sample}_post_n500.csv")

if __name__ == "__main__":
    main()