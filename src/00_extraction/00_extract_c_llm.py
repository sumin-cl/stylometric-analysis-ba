# src/00_extraction/00_extract_c_llm.py
import pandas as pd
import time
from tqdm import tqdm
from openai import OpenAI
from utils.paths import EXTRACTED
from datetime import datetime

import os
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_llm_corpus():
    print("--- Generiere synthetisches LLM-Korpus ---")
    
    raw_path = EXTRACTED / "corpus_a_raw_subset.csv"
    print(f"Lade Themenspender: {raw_path.name}")
    df_raw = pd.read_csv(raw_path)

    df_raw = df_raw.dropna(subset=['post', 'title', 'subreddit'])
    
    df_sample = df_raw.sample(n=500, random_state=42).reset_index(drop=True)
    
    llm_posts =[]
    
    print("Starte OpenAI API-Abfragen (GPT-4o-mini)... das dauert ca. 3-5 Minuten.")
    for idx, row in tqdm(df_sample.iterrows(), total=len(df_sample)):
        subreddit = row['subreddit']
        title = row['title']
        
        # Der Prompt
        prompt = (
            f"Write a normal, everyday Reddit post for the subreddit r/{subreddit} "
            f"with the title '{title}'. "
            f"Write as if you are a regular human internet user. "
            f"Do not use hashtags. Make the post between 150 and 300 words long."
        )
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a regular internet user posting on Reddit."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7 # Etwas Varianz zulassen
            )
            generated_text = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"\nFehler bei Zeile {idx}: {e}")
            generated_text = "ERROR"
            time.sleep(2) # Kurz warten bei API-Fehler
            
        llm_posts.append({
            "id": f"llm_{idx}",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "post": generated_text,
            "subreddit": subreddit, # Zur Doku aufheben
            "prompt_title": title   # Zur Doku aufheben
        })
        
        # Winzige Pause um Rate-Limits zu schonen
        time.sleep(0.1)
        
    # Speichern als raw-Datei (damit es normal durch unsere Pipeline läuft)
    df_llm = pd.DataFrame(llm_posts)
    
    # Fehlerhafte Drops filtern
    df_llm = df_llm[df_llm["post"] != "ERROR"]
    
    out_path = EXTRACTED / "corpus_c_raw.csv"
    df_llm.to_csv(out_path, index=False)
    print(f"\n[ERFOLG] {len(df_llm)} synthetische Posts gespeichert unter: {out_path}")

if __name__ == "__main__":
    generate_llm_corpus()