import pandas as pd
from preprocessing_test import clean_reddit_text

def process_corpus(input_path, output_path, corpus_name):
    print(f"--- Verarbeite {corpus_name} ---")

    df = pd.read_csv(input_path)
    original_count = len(df)
    print(f"Start: {original_count} Posts")

    print("Cleaning läuft...")
    df['text'] = df['post'].apply(clean_reddit_text)
    
    df = df[df['text'].str.strip() != ""]

    # Token-Count Filter (Minimum 30 Wörter für Stylometrie), später mit spaCy
    df['token_count'] = df['text'].apply(lambda x: len(x.split()))
    
    df_filtered = df[df['token_count'] >= 30].copy()
    
    # Statistik Drop Rate
    final_count = len(df_filtered)
    removed = original_count - final_count
    print(f"Entfernt (<30 Wörter oder leer): {removed} ({removed/original_count:.1%})")
    print(f"Final: {final_count} Posts")

    # Wir speichern 'text' statt 'post'
    df_filtered[['id', 'date', 'text']].to_csv(output_path, index=False)
    print(f"Gespeichert unter: {output_path}\n")

if __name__ == "__main__":
    # Korpus A (Pre-LLM)
    process_corpus('C:\\Users\\smcho\\Documents\\Projects\\stylometric-analysis-ba\\data\\corpus_A_2019_2021.csv', 'corpus_a_clean.csv', 'Korpus A (2019-21)')
    
    # Korpus B (Post-LLM)
    #process_corpus('C:\\Users\\smcho\\Documents\\Projects\\stylometric-analysis-ba\\data\\corpus_B_2023_2025.csv', 'corpus_b_clean.csv', 'Korpus B (2023-25)')