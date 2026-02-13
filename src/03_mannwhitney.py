# src/03_mannwhitney.py
from scipy.stats import mannwhitneyu
import numpy as np

def run_significance_test(depths_a, depths_b):
    print("\n--- STATISTISCHE SIGNIFIKANZ (Mann-Whitney-U) ---")
    
    stat, p_val = mannwhitneyu(depths_a, depths_b, alternative='two-sided')
    
    print(f"U-Statistik: {stat:.2f}")
    print(f"p-Wert: {p_val:.10f}") # Nachkommastellen

    if p_val < 0.05:
        print(">>> Ergebnis ist SIGNIFIKANT (p < 0.05). Der Unterschied ist kein Zufall.")
        if p_val < 0.001:
            print(">>> Höchste Signifikanzstufe erreicht (p < 0.001).")
    else:
        print(">>> Ergebnis ist NICHT signifikant. Der Unterschied könnte Zufall sein.")

    # Effektstärke berechnen
    # Ein kleiner Unterschied bei großem N ist oft signifikant, 
    # aber die Effektstärke zeigt, wie groß der Unterschied tatsächlich ist.
    mean_diff = np.mean(depths_a) - np.mean(depths_b)
    print(f"Absolute Differenz der Mittelwerte: {mean_diff:.4f}")

run_significance_test(depts_a, depts_b)