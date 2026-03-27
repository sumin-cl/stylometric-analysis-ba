# src/01_tagging/01b_pos_tagging.py
import pandas as pd
from utils.nlp_utils import nlp 
from tqdm import tqdm
from utils.paths import FINAL, PROCESSED, TAGGED
from pathlib import Path

def tag_and_save(input_name, output_name=None):
    """
    Führt spaCy-POS-Tagging für alle Posts in input_file durch.
    Speichert die Tag-Sequenz jedes Posts als leerzeichen-getrennten String
    in einer neuen Spalte 'pos_tags' und schreibt das Ergebnis nach output_file.
    Erwartet Dateien aus data/final/.
    Speichert die POS-Tag-Sequenzen unter data/final/tagged/.
    """
    input_path = PROCESSED / input_name

    if output_name is None:
        stem = Path(input_name).stem.replace("_cleaned", "")
        output_name = f"{stem}_tagged"

    print(f"--- Starte Tagging für {input_path} ---")
    df = pd.read_csv(input_path)
    
    pos_tags_list = []
    
    for doc in tqdm(nlp.pipe(df['text'].astype(str), batch_size=100, disable=["parser", "ner"]), total=len(df)):
        tags = " ".join([token.pos_ for token in doc])
        pos_tags_list.append(tags)
    
    df['pos_tags'] = pos_tags_list
    
    tagged_dir = TAGGED
    tagged_dir.mkdir(parents=True, exist_ok=True)

    output_path = tagged_dir / f"{output_name}.csv"
    df.to_csv(output_path, index=False)

    print(f"Gespeichert: {output_path} ({len(df)} Zeilen)")

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "downsampled"
    if mode == "full":
        tag_and_save("corpus_a_cleaned.csv")
        tag_and_save("corpus_b_cleaned.csv")
    else:
        sample = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        tag_and_save("sample{sample}_pre_n500.csv")
        tag_and_save("sample{sample}_post_n500.csv")