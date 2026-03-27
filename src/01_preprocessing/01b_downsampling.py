# src/01_preprocessing/01b_downsample.py
import pandas as pd
from utils.paths import PROCESSED
from pathlib import Path

# Hier trägst du später einfach dein LLM-Korpus ein
CORPORA = {
    "pre": PROCESSED / "corpus_a_cleaned.csv",
    "post": PROCESSED / "corpus_b_cleaned.csv",
    "llm": PROCESSED / "corpus_llm_cleaned.csv"  # <- Platzhalter für dein 3. Korpus
}

SEEDS = [42, 43, 44]
TARGET_N = 500

def create_samples():
    for name, path in CORPORA.items():
        if not path.exists():
            print(f"[SKIP] Datei nicht gefunden: {path.name}")
            continue
            
        print(f"\n--- Lade {name.upper()} ---")
        df = pd.read_csv(path)
        
        # 1. Filtern: 150 - 300 Tokens
        df['token_count'] = df['text'].astype(str).str.split().str.len()
        df_filtered = df[(df['token_count'] >= 150) & (df['token_count'] <= 300)]
        
        print(f"Texte im Bereich 150-300 Tokens: {len(df_filtered)} / {len(df)}")
        
        if len(df_filtered) < TARGET_N:
            print(f"[FEHLER] Zu wenig Texte für {name}! (Soll: {TARGET_N}, Ist: {len(df_filtered)})")
            continue

        # 2. Samplen und speichern (in PROCESSED)
        for i, seed in enumerate(SEEDS, start=1):
            sample_df = df_filtered.sample(n=TARGET_N, random_state=seed)
            out_file = PROCESSED / f"sample{i}_{name}_n{TARGET_N}.csv"
            
            sample_df.drop(columns=['token_count']).to_csv(out_file, index=False)
            print(f"Gespeichert: {out_file.name}")

if __name__ == "__main__":
    create_samples()