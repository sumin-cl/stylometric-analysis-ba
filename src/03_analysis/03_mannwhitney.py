# src/03_analysis/03_mannwhitney.py
from scipy.stats import mannwhitneyu
import numpy as np

def run_significance_test(depths_a, depths_b):
    """
    Führt einen zweiseitigen Mann-Whitney-U-Test auf zwei Listen von Baumtiefen durch.
    Gibt U-Statistik, p-Wert, Signifikanzniveau und absolute Mittelwertdifferenz aus.
    """
    print("\n--- STATISTISCHE SIGNIFIKANZ (Mann-Whitney-U) ---")
    
    stat, p_val = mannwhitneyu(depths_a, depths_b, alternative='two-sided')
    
    print(f"U-Statistik: {stat:.2f}")
    print(f"p-Wert: {p_val:.10f}") 

    if p_val < 0.05:
        print(">>> Ergebnis ist signifikant (p < 0.05). Der Unterschied ist kein Zufall.")
        if p_val < 0.001:
            print(">>> Höchste Signifikanzstufe erreicht (p < 0.001).")
    else:
        print(">>> Ergebnis ist nicht signifikant. Der Unterschied könnte Zufall sein.")

    mean_diff = np.mean(depths_a) - np.mean(depths_b)
    print(f"Absolute Differenz der Mittelwerte: {mean_diff:.4f}")