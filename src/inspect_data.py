import pandas as pd

print("Lade Datensatz... (bitte warten)")
df = pd.read_csv('reddit_database.csv', low_memory=False)

# Nur r/MachineLearning 
df_ml = df[df['subreddit'] == 'MachineLearning'].copy()

# created timestamp in lesbares Datum umwandeln
df_ml['date'] = pd.to_datetime(df_ml['created_timestamp'], unit='s')

print(f"\n--- Statistik für r/MachineLearning ---")
print(f"Anzahl Posts: {len(df_ml)}")
print(f"Zeitraum: von {df_ml['date'].min()} bis {df_ml['date'].max()}")

print("\nStichprobe der Texte (Spalte 'post'):")
# keine leeren Posts
sample_texts = df_ml[df_ml['post'].notna()]['post'].head(3)
for i, t in enumerate(sample_texts):
    print(f"\nPost {i+1}:\n{t[:300]}...") # Zeige die ersten 300 Zeichen