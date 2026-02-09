import requests
import pandas as pd
import time
import datetime

# Konfiguration
SUBREDDIT = "MachineLearning"
# Diese Keywords waren ANFANG 2023 heiß -> Damit finden wir die alten Posts
KEYWORDS = [
    "ChatGPT", "GPT-4", "OpenAI", "LLaMA", "Alpaca", "Vicuna", 
    "PaLM", "Bard", "Bing", "Plugin", "AutoGPT", "Foundation Model"
]
TARGET_YEARS = [2023] # Wir zielen spezifisch auf das fehlende Jahr
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Thesis-Scraper/Final"

def search_old_posts():
    all_posts = {}
    print(f"Starte Zeitmaschinen-Suche für 2023 in r/{SUBREDDIT}...")
    
    for keyword in KEYWORDS:
        print(f"Suche nach '{keyword}'...")
        # WICHTIG: Wir sortieren nach RELEVANCE, nicht New. Das gräbt tiefer.
        url = f"https://www.reddit.com/r/{SUBREDDIT}/search.json?q={keyword}&restrict_sr=1&sort=relevance&t=all&limit=100"
        
        try:
            response = requests.get(url, headers={'User-Agent': USER_AGENT})
            if response.status_code == 200:
                data = response.json()
                children = data['data']['children']
                
                for child in children:
                    post = child['data']
                    # Zeit checken
                    created = datetime.datetime.fromtimestamp(post['created_utc'])
                    
                    if created.year == 2023:
                        all_posts[post['id']] = {
                            'id': post['id'],
                            'date': created,
                            'post': post['selftext']
                        }
            time.sleep(1) # Kurz warten
        except Exception as e:
            print(f"Fehler: {e}")

    print(f"\n--- ERGEBNIS ---")
    print(f"Gefundene Posts aus 2023: {len(all_posts)}")
    return pd.DataFrame(list(all_posts.values()))

# Ausführen
df = search_old_posts()
if not df.empty:
    df.to_csv("corpus_B_2023_part.csv", index=False)
    print("Gespeichert!")