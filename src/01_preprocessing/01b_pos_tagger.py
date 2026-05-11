# src/01_preprocessing/01b_pos_tagger.py
import pandas as pd
from utils.nlp_utils import nlp
from tqdm import tqdm
from utils.paths import PROCESSED_FULL, PROCESSED_SAMPLES, PROCESSED_FILTERED, \
                        TAGGED_FULL, TAGGED_SAMPLES, TAGGED_FILTERED
from pathlib import Path


def tag_and_save(input_path, output_dir):
    """
    Führt spaCy-POS-Tagging für alle Posts in input_file durch.
    Speichert die Tag-Sequenz jedes Posts als leerzeichen-getrennten String
    in einer neuen Spalte 'pos_tags' und schreibt das Ergebnis nach output_dir.
    """
    stem = Path(input_path).stem.replace("_cleaned", "")
    output_name = f"{stem}_tagged"

    print(f"--- Starte Tagging für {Path(input_path).name} ---")
    df = pd.read_csv(input_path)

    pos_tags_list = []
    for doc in tqdm(nlp.pipe(df['text'].astype(str), batch_size=100, disable=["parser", "ner"]), total=len(df)):
        tags = " ".join([token.pos_ for token in doc])
        pos_tags_list.append(tags)

    df['pos_tags'] = pos_tags_list

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{output_name}.csv"
    df.to_csv(output_path, index=False)
    print(f"Gespeichert: {output_path} ({len(df)} Zeilen)")


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"

    if mode == "full":
        """Vollkorpus (alle Tokenlängen) — optional, nicht im Launcher."""
        tag_and_save(PROCESSED_FULL / "corpus_a_cleaned.csv", TAGGED_FULL)
        tag_and_save(PROCESSED_FULL / "corpus_b_cleaned.csv", TAGGED_FULL)
    elif mode == "llm":
        tag_and_save(PROCESSED_FILTERED / "corpus_c_filtered.csv", TAGGED_FILTERED)
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        tag_and_save(PROCESSED_SAMPLES / f"sample{sample}_pre_n500.csv",  TAGGED_SAMPLES)
        tag_and_save(PROCESSED_SAMPLES / f"sample{sample}_post_n500.csv", TAGGED_SAMPLES)