import pandas as pd
from lexical_diversity import lex_div as ld
from scipy import stats

def calculate_mtld(text):
    tokens = ld.tokenize(text)
    if len(tokens) < 10: 
        return None
    return ld.mtld(tokens)

def run_analysis():
    print("--- Start MTLD-Analyse ---")
    
    df_a = pd.read_csv('corpus_a_2019_2021.csv')
    df_b = pd.read_csv('corpus_b_2023_2024.csv')

    print("Verarbeite Korpus A...")
    df_a['mtld'] = df_a['text'].apply(calculate_mtld)
    
    print("Verarbeite Korpus B...")
    df_b['mtld'] = df_b['text'].apply(calculate_mtld)

    results_a = df_a['mtld'].dropna()
    results_b = df_b['mtld'].dropna()

    mean_a = results_a.mean()
    mean_b = results_b.mean()
    
    t_stat, p_val = stats.ttest_ind(results_a, results_b)

    print("\n--- ERGEBNISSE ---")
    print(f"Korpus A (2020-21) Mittelwert: {mean_a:.2f}")
    print(f"Korpus B (2023-25) Mittelwert: {mean_b:.2f}")
    print(f"Differenz: {mean_b - mean_a:.2f}")
    
    print("\n--- SIGNIFIKANZ ---")
    print(f"p-Wert: {p_val:.4f}")
    if p_val < 0.05:
        print("Ergebnis ist SIGNIFIKANT (p < 0.05)")
    else:
        print("Ergebnis ist NICHT signifikant.")

if __name__ == "__main__":
    run_analysis()