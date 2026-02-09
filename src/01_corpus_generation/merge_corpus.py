import pandas as pd

# Dateinamen (Pass auf, dass die exakt stimmen!)
file1 = "corpus_B_part1.csv"  # Die von vorhin (579 Posts)
file2 = "corpus_B_2023_part.csv"  # Die von gerade eben (427 Posts)

try:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Zusammenfügen
    full_df = pd.concat([df1, df2])
    
    # Duplikate entfernen (falls sich ein Post überschnitten hat)
    before = len(full_df)
    full_df = full_df.drop_duplicates(subset=['id'])
    after = len(full_df)
    
    # Sortieren nach Datum
    full_df['date'] = pd.to_datetime(full_df['date'])
    full_df = full_df.sort_values(by='date')
    
    print(f"Zusammengefügt!")
    print(f"Vorher: {before} -> Nachher (ohne Duplikate): {after}")
    print(f"Zeitraum: {full_df['date'].min()} bis {full_df['date'].max()}")
    
    # Speichern
    full_df.to_csv("CORPUS_B_FINAL.csv", index=False)
    print("Gespeichert als 'CORPUS_B_FINAL.csv'. DAS DING IST FERTIG.")

except Exception as e:
    print(f"Fehler: {e}")
    print("Check mal, ob die Dateinamen oben stimmen.")