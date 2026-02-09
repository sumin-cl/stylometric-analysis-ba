import requests
import pandas as pd
import time
import datetime

# Konfiguration
SUBREDDIT = "MachineLearning"
TARGET_YEARS = [2023, 2024]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Thesis-Scraper/1.0"

def get_posts():
    url = f"https://www.reddit.com/r/{SUBREDDIT}/new.json"
    headers = {'User-Agent': USER_AGENT}
    posts = []
    after = None
    
    print(f"Starte Scraper für r/{SUBREDDIT}...")
    
    # Wir machen max 50 Runden à ~25-100 Posts (das ist das Limit für Public JSON)
    for i in range(50):
        params = {'limit': 100, 'after': after}
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"Fehler: {response.status_code}")
                break
                
            data = response.json()
            children = data['data']['children']
            
            if not children:
                print("Keine weiteren Posts gefunden.")
                break
                
            for child in children:
                post_data = child['data']
                # Zeitstempel umwandeln
                created_utc = post_data['created_utc']
                dt = datetime.datetime.fromtimestamp(created_utc)
                
                # Wir sammeln alles und filtern später (sicherer)
                posts.append({
                    'id': post_data['id'],
                    'date': dt,
                    'title': post_data['title'],
                    'post': post_data['selftext']
                })
            
            # Pagination: Das Token für die nächste Seite
            after = data['data']['after']
            
            print(f"Runde {i+1}: {len(children)} Posts geladen. Letztes Datum: {posts[-1]['date']}")
            
            if after is None:
                break
                
            # Pause, damit Reddit uns nicht blockt
            time.sleep(2)
            
        except Exception as e:
            print(f"Absturz in Runde {i}: {e}")
            break

    return pd.DataFrame(posts)

# Ausführen
df = get_posts()

# Filtern nach Jahren (2023 & 2024)
print("\n--- Filterung ---")
df['year'] = df['date'].dt.year
corpus_b = df[df['year'].isin(TARGET_YEARS)]

print(f"Gesamt gescraped: {len(df)}")
print(f"Davon in 2023/2024: {len(corpus_b)}")

if len(corpus_b) > 0:
    filename = "corpus_B_raw.csv"
    corpus_b.to_csv(filename, index=False)
    print(f"Erfolg! Gespeichert als {filename}")
else:
    print("Warnung: Keine Posts aus 2023/2024 erreicht. Wir müssen eine andere Strategie (Suche) nutzen.")