import pandas as pd
import matplotlib.pyplot as plt

def analyze_baseline(path_a, path_b):
    print("--- BASELINE ANALYSE ---")
    
    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    
    df_a['corpus'] = 'A (2019-21)'
    df_b['corpus'] = 'B (2023-25)'
    
    df_a['tokens'] = df_a['text'].astype(str).apply(lambda x: len(x.split()))
    df_b['tokens'] = df_b['text'].astype(str).apply(lambda x: len(x.split()))
    
    print(f"\nKORPUS A (Pre-LLM):")
    print(f"Anzahl Posts: {len(df_a)}")
    print(f"Durchschnittliche Länge: {df_a['tokens'].mean():.2f} Wörter")
    print(f"Median Länge: {df_a['tokens'].median():.2f} Wörter")
    
    print(f"\nKORPUS B (Post-LLM):")
    print(f"Anzahl Posts: {len(df_b)}")
    print(f"Durchschnittliche Länge: {df_b['tokens'].mean():.2f} Wörter")
    print(f"Median Länge: {df_b['tokens'].median():.2f} Wörter")
    
    min_count = min(len(df_a), len(df_b))
    print(f"\n>>> EMPFEHLUNG FÜR DOWNSAMPLING: Reduziere beide auf {min_count} Posts.")

if __name__ == "__main__":
    analyze_baseline('corpus_a_clean.csv', 'corpus_b_clean.csv')