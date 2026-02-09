import pandas as pd

file_path_b = 'CORPUS_B_FINAL.csv'  
output_path_b = 'corpus_b_2023_2025.csv' 

df_b = pd.read_csv(file_path_b)

print(f"Original Shape B: {df_b.shape}")

if 'title' in df_b.columns:
    df_b = df_b.drop(columns=['title'])
    print("- Spalte 'title' entfernt.")

df_b = df_b[['id', 'date', 'post']]

duplicates = df_b.duplicated(subset=['id']).sum()
if duplicates > 0:
    print(f"- {duplicates} Duplikate basierend auf 'id' entfernt.")
    df_b = df_b.drop_duplicates(subset=['id'])

df_b.to_csv(output_path_b, index=False)
print(f"Final Shape B: {df_b.shape}")
print(f"Gespeichert unter: {output_path_b}")