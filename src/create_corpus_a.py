import pandas as pd

print("Lade Basis-Daten...")
df = pd.read_csv('reddit_database.csv', low_memory=False)

# 1. Filtern auf r/MachineLearning
df = df[df['subreddit'] == 'MachineLearning'].copy()

# 2. Zeitstempel umwandeln
df['date'] = pd.to_datetime(df['created_timestamp'], unit='s')

# 3. Filter für Corpus A: 2019-01-01 bis 2021-12-31
start_date = '2019-01-01'
end_date = '2021-12-31'
mask = (df['date'] >= start_date) & (df['date'] <= end_date)
corpus_A = df.loc[mask].copy()

# 4. Nur notwendige Spalten behalten (spart Speicher & Zwang-Verwirrung)
# Wir brauchen nur ID, Datum und den Text
corpus_A = corpus_A[['id', 'date', 'post']]

# 5. Leere Posts entfernen
corpus_A = corpus_A.dropna(subset=['post'])

print(f"Corpus A (Pre-LLM) erstellt.")
print(f"Anzahl Dokumente zwischen 2019 und 2021: {len(corpus_A)}")

# Speichern als neue, kompakte Datei
corpus_A.to_csv('corpus_A_2019_2021.csv', index=False)
print("Datei 'corpus_A_2019_2021.csv' wurde erfolgreich gespeichert.")