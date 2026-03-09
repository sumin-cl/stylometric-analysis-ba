import pandas as pd
import os
from nlp_utils import nlp 
from tqdm import tqdm

def tag_and_save(input_file, output_file):
    """
    Führt spaCy-POS-Tagging für alle Posts in input_file durch.
    Speichert die Tag-Sequenz jedes Posts als leerzeichen-getrennten String
    in einer neuen Spalte 'pos_tags' und schreibt das Ergebnis nach output_file.
    """
    print(f"--- Starte Tagging für {input_file} ---")
    df = pd.read_csv(input_file)
    
    pos_tags_list = []
    
    for doc in tqdm(nlp.pipe(df['text'].astype(str), batch_size=100, disable=["parser", "ner"]), total=len(df)):
        tags = " ".join([token.pos_ for token in doc])
        pos_tags_list.append(tags)
    
    df['pos_tags'] = pos_tags_list
    
    os.makedirs("data/tagged", exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Erfolg: {output_file} gespeichert.\n")

if __name__ == "__main__":
    tag_and_save("data/final/corpus_a_clean.csv", "data/tagged/corpus_a_tagged.csv")
    tag_and_save("data/final/corpus_b_clean.csv", "data/tagged/corpus_b_tagged.csv")