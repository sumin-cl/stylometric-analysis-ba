import requests
import pandas as pd
import time
import datetime

# Konfiguration
SUBREDDIT = "MachineLearning"
KEYWORDS = [
    "ChatGPT", "GPT-4", "OpenAI", "Bard", "Bing", 
    "LLaMA", "Alpaca", "Vicuna", "PaLM", "Gemini",
    "AGI", "Alignment", "Safety", "Hallucination"
]
TARGET_YEARS = [2023, 2024]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Thesis-Scraper/Search-Method"

def search_posts():
    all_posts = {}  #ID als Key, um Duplikate zu verhindern
    
    print(f"Starte Keyword-Suche in r/{SUBREDDIT}...")
    
    for keyword in KEYWORDS:
        print(f"\n--- Suche nach: '{keyword}' ---")
        url = f"https://www.reddit.com/r/{SUBREDDIT}/search.json"
        after = None
        
        # Pro Keyword holen wir max 5-10 Seiten (ca. 500 Posts)
        for i in range(10):
            params = {
                'q': keyword,
                'restrict_sr': 1,  # Nur in diesem Subreddit
                'sort': 'relevance',     # Relevant zuerst
                't': 'all',
                'limit': 100,
                'after': after
            }
            
            try:
                response = requests.get(url, headers={'User-Agent': USER_AGENT}, params=params)
                if response.status_code != 200:
                    print(f"Fehler bei '{keyword}': {response.status_code}")
                    break
                
                data = response.json()
                children = data['data']['children']
                
                if not children:
                    break
                
                for child in children:
                    post = child['data']
                    pid = post['id']
                    
                    # Neue Posts
                    if pid not in all_posts:
                        created_utc = post['created_utc']
                        dt = datetime.datetime.fromtimestamp(created_utc)
                        
                        # Nur nehmen, wenn das Jahr passt (spart Speicher)
                        if dt.year in TARGET_YEARS:
                            all_posts[pid] = {
                                'id': pid,
                                'date': dt,
                                'title': post['title'],
                                'post': post['selftext']
                            }
                
                after = data['data']['after']
                if after is None:
                    break
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Fehler: {e}")
                break
        
        print(f"Aktuelle Anzahl relevanter Posts (2023-2024): {len(all_posts)}")

    return pd.DataFrame(list(all_posts.values()))

# Ausführen
df = search_posts()

if not df.empty:
    # Sortieren nach Datum
    df = df.sort_values(by='date')
    
    # Statistik
    print("\n=== E R G E B N I S ===")
    print(f"Gesamt gefundene Posts für 2023/2024: {len(df)}")
    print(f"Zeitraum: {df['date'].min()} bis {df['date'].max()}")
    
    # Speichern
    filename = "corpus_B_2023_2024.csv"
    df.to_csv(filename, index=False)
    print(f"Gespeichert als {filename}")
else:
    print("Leider keine Posts gefunden. Versuche andere Keywords.")