# src/02_eda/02_eda_length.py
"""
Analysiert die Token-Längenverteilung der bereinigten Korpora (A und B).
Erzeugt ein interaktives Histogramm (Plotly) und eine Übersichtstabelle.

Output: data/final/02_eda/length_distribution.html
"""
import pandas as pd
import plotly.graph_objects as go
from utils.paths import PROCESSED_FULL, EDA


def run_length_eda():
    print("Lade Korpora...")
    df_a = pd.read_csv(PROCESSED_FULL / "corpus_a_cleaned.csv")
    df_b = pd.read_csv(PROCESSED_FULL / "corpus_b_cleaned.csv")

    df_a['tokens'] = df_a['text'].astype(str).str.split().str.len()
    df_b['tokens'] = df_b['text'].astype(str).str.split().str.len()

    # ── Übersichtstabelle in der Konsole ──────────────────────────────────────
    bins = list(range(0, 1050, 50))
    labels = [f"{bins[i]}–{bins[i+1]}" for i in range(len(bins)-1)]

    counts_a = pd.cut(df_a['tokens'], bins=bins, labels=labels, right=False).value_counts().sort_index()
    counts_b = pd.cut(df_b['tokens'], bins=bins, labels=labels, right=False).value_counts().sort_index()

    table = pd.DataFrame({
        "Intervall":     labels,
        "Corpus A (Pre)":  counts_a.values,
        "Corpus B (Post)": counts_b.values,
    })

    # Nur Zeilen mit mindestens einem Post anzeigen
    table = table[(table["Corpus A (Pre)"] > 0) | (table["Corpus B (Post)"] > 0)]
    print("\nToken-Längenverteilung (Bins à 50):")
    print(table.to_string(index=False))

    # Kennzahlen
    for name, df in [("Corpus A (Pre-2022)", df_a), ("Corpus B (Post-2022)", df_b)]:
        t = df['tokens']
        in_window = ((t >= 150) & (t <= 300)).sum()
        print(f"\n{name}:")
        print(f"  Gesamt:        {len(df):>6}")
        print(f"  Median:        {t.median():>6.0f} Tokens")
        print(f"  Mittelwert:    {t.mean():>6.1f} Tokens")
        print(f"  Min / Max:     {t.min()} / {t.max()}")
        print(f"  150–300 Fenster: {in_window:>5} Posts ({in_window/len(df)*100:.1f}%)")

    # ── Plotly Histogramm ─────────────────────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df_a['tokens'],
        xbins=dict(start=0, end=1000, size=50),
        name="Corpus A (Pre-2022)",
        marker_color="steelblue",
        opacity=0.7,
    ))

    fig.add_trace(go.Histogram(
        x=df_b['tokens'],
        xbins=dict(start=0, end=1000, size=50),
        name="Corpus B (Post-2022)",
        marker_color="tomato",
        opacity=0.7,
    ))

    # Markierung des aktuellen Analysefensters
    fig.add_vrect(
        x0=150, x1=300,
        fillcolor="gold", opacity=0.12,
        line_width=1, line_color="goldenrod",
        annotation_text="aktuelles Fenster (150–300)",
        annotation_position="top left",
        annotation_font_size=11,
    )

    fig.update_layout(
        barmode="overlay",
        title="Token-Längenverteilung: Corpus A vs. Corpus B",
        xaxis_title="Token-Anzahl pro Post (Bins à 50)",
        yaxis_title="Anzahl Posts",
        legend=dict(x=0.72, y=0.97),
        template="plotly_white",
        font=dict(family="Arial", size=13),
        bargap=0.05,
    )

    out_path = EDA / "length_distribution.html"
    fig.write_html(str(out_path))
    print(f"\n[OK] Histogramm gespeichert unter: {out_path}")


if __name__ == "__main__":
    run_length_eda()