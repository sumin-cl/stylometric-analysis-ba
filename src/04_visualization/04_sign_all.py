"""
Aggregator: Sammelt alle Signifikanz- und Effektgroessen-Statistiken in
eine zentrale Uebersichtstabelle.

Liest die existierenden MWU+r_rb-Werte aus den Pipeline-JSONs (Phase D)
und ergaenzt sie um drei komplementaere Statistiken:
  - Levene-Test (Varianzhomogenitaet)
  - Kolmogorov-Smirnov (Verteilungs-Form)
  - Cohen's d (parametrische Effektgroesse)

Output:
  data/final/results/significance/aggregate_report.csv
  data/final/results/significance/aggregate_report.md

Hinweis: FWR-untagged-Stats benoetigen per-doc-Werte, die nicht in den
Pipeline-JSONs gespeichert sind; diese werden hier on-the-fly mit spaCy
neu berechnet (~5-8 Minuten Laufzeit). Mit Flag --quick wird das
uebersprungen (nur Cohen's d aus Mean/Std).

Verwendung:
    python src/04_visualization/04_sign_all.py
    python src/04_visualization/04_sign_all.py --quick   # ohne spaCy-Lauf
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import levene, ks_2samp

from utils.paths import (
    PROCESSED_FILTERED, TAGGED_FILTERED, PARSED_FILTERED,
    RESULTS_MTLD_FILTERED, RESULTS_MTLD_LLM,
    RESULTS_SHANNON_FILTERED, RESULTS_SHANNON_LLM,
    RESULTS_FWR_FILTERED, RESULTS_FWR_LLM,
    RESULTS_PTD_FILTERED, RESULTS_PTD_LLM,
    RESULTS_SIGNIF,
)

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cohens_d(values_a, values_b):
    """Cohen's d mit pooled std (Cohen 1988). Vorzeichen-Konvention:
    d > 0 -> values_a groesser, d < 0 -> values_b groesser."""
    n1, n2 = len(values_a), len(values_b)
    m1, m2 = np.mean(values_a), np.mean(values_b)
    s1, s2 = np.std(values_a, ddof=1), np.std(values_b, ddof=1)
    pooled = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    return float((m1 - m2) / pooled) if pooled > 0 else 0.0


def cohens_d_from_summary(m1, s1, n1, m2, s2, n2):
    """Cohen's d nur aus den Summary-Statistiken (Mean/Std/N), falls
    Raw-Daten nicht verfuegbar."""
    pooled = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    return float((m1 - m2) / pooled) if pooled > 0 else 0.0


def classify_rrb(r):
    a = abs(r)
    return ("negligible" if a < 0.1 else
            "small"      if a < 0.3 else
            "medium"     if a < 0.5 else
            "large")


def classify_cohen(d):
    a = abs(d)
    return ("negligible" if a < 0.2 else
            "small"      if a < 0.5 else
            "medium"     if a < 0.8 else
            "large")


# ---------------------------------------------------------
# Raw-Daten-Loader
# ---------------------------------------------------------
def load_mtld_chunks(layer):
    if layer == "filtered":
        res = _load_json(RESULTS_MTLD_FILTERED / "mtld_chunks_filtered.json")["results"]
        return res["mtld_chunks_a"], res["mtld_chunks_b"]
    else:
        res = _load_json(RESULTS_MTLD_LLM / "mtld_chunks_llm.json")["results"]
        return res["mtld_chunks_b"], res["mtld_chunks_c"]


def load_shannon_per_post(layer, mode):
    """mode: 'word' oder 'pos'"""
    if layer == "filtered":
        res = _load_json(RESULTS_SHANNON_FILTERED / f"entropy_per_post_{mode}_filtered.json")["results"]
        return res["entropy_per_post_a"], res["entropy_per_post_b"]
    else:
        res = _load_json(RESULTS_SHANNON_LLM / f"entropy_per_post_{mode}_llm.json")["results"]
        return res["entropy_per_post_b"], res["entropy_per_post_c"]


def load_ptd(layer):
    a = _load_json(PARSED_FILTERED / "corpus_a_filtered_parsed_depths.json")
    b = _load_json(PARSED_FILTERED / "corpus_b_filtered_parsed_depths.json")
    c = _load_json(PARSED_FILTERED / "corpus_c_filtered_parsed_depths.json")
    return (a, b) if layer == "filtered" else (b, c)


def compute_fwr_tagged_pair(letter_1, letter_2):
    """FWR tagged per-doc fuer ein Korpus-PAAR, mit Pipeline-identischem
    Subsampling (min-Laenge, random_state=42).
    FWR tagged = Funktions-Tokens / Gesamt-Tokens."""
    func_tags = {"PRON", "DET", "ADP", "CCONJ", "SCONJ", "PART"}

    df_1 = pd.read_csv(TAGGED_FILTERED / f"corpus_{letter_1}_filtered_tagged.csv")
    df_2 = pd.read_csv(TAGGED_FILTERED / f"corpus_{letter_2}_filtered_tagged.csv")

    min_len = min(len(df_1), len(df_2))
    df_1 = df_1.sample(n=min_len, random_state=42)
    df_2 = df_2.sample(n=min_len, random_state=42)

    def fwr_of(pos_string):
        tags = str(pos_string).split()
        if not tags:
            return 0.0
        return sum(1 for t in tags if t in func_tags) / len(tags)

    return (df_1["pos_tags"].apply(fwr_of).tolist(),
            df_2["pos_tags"].apply(fwr_of).tolist())


def compute_fwr_untagged_pair(letter_1, letter_2, nlp_model):
    """Berechnet FWR untagged per-doc fuer ein Korpus-PAAR, mit identischem
    Subsampling wie die Pipeline (min-Laenge, random_state=42). Gibt
    (fwr_list_1, fwr_list_2) zurueck.

    FWR untagged = Funktions-Tokens / Inhalts-Tokens (analog calculate_fwr_per_doc).
    """
    from tqdm import tqdm

    df_1 = pd.read_csv(PROCESSED_FILTERED / f"corpus_{letter_1}_filtered.csv")
    df_2 = pd.read_csv(PROCESSED_FILTERED / f"corpus_{letter_2}_filtered.csv")

    # Subsampling identisch zur Pipeline (03_fwr_ratio.py)
    min_len = min(len(df_1), len(df_2))
    df_1 = df_1.sample(n=min_len, random_state=42)
    df_2 = df_2.sample(n=min_len, random_state=42)

    content_tags = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
    func_tags    = {"ADP", "AUX", "CONJ", "CCONJ", "SCONJ", "DET", "PART", "PRON"}

    def fwr_per_doc(texts, desc):
        ratios = []
        for doc in tqdm(nlp_model.pipe(texts.astype(str), batch_size=100),
                        total=len(texts), desc=desc):
            n_func = sum(1 for t in doc if t.pos_ in func_tags)
            n_cont = sum(1 for t in doc if t.pos_ in content_tags)
            ratios.append(n_func / n_cont if n_cont > 0 else 0.0)
        return ratios

    fwr_1 = fwr_per_doc(df_1["text"], f"FWR untagged ({letter_1})")
    fwr_2 = fwr_per_doc(df_2["text"], f"FWR untagged ({letter_2})")
    return fwr_1, fwr_2


# ---------------------------------------------------------
# Statistik-Berechnung
# ---------------------------------------------------------
def compute_complementary_stats(raw_a, raw_b):
    """Levene, KS, Cohen's d aus zwei Roh-Listen."""
    raw_a = np.asarray(raw_a, dtype=float)
    raw_b = np.asarray(raw_b, dtype=float)
    levene_w, p_lev = levene(raw_a, raw_b)
    ks_d,     p_ks  = ks_2samp(raw_a, raw_b)
    d = cohens_d(raw_a, raw_b)
    return {
        "levene_W":    float(levene_w),
        "p_levene":    float(p_lev),
        "ks_D":        float(ks_d),
        "p_ks":        float(p_ks),
        "cohens_d":    d,
        "abs_cohens_d": abs(d),
        "cohen_effect": classify_cohen(d),
    }


def build_record(metric, comparison, summary_json_path, mean_keys, raw_a, raw_b):
    """Sammelt alles fuer eine (Metrik, Comparison)-Zeile.
    
    summary_json_path: liefert Mean-Werte + MWU+r_rb
    mean_keys: tuple (key_for_corpus_1, key_for_corpus_2) in summary["results"]
    raw_a, raw_b: per-doc/chunk-Werte fuer Levene/KS/Cohen's d (oder None)
    """
    j = _load_json(summary_json_path)["results"]

    # Mean-Werte ggf. aus Listen aggregieren (z.B. MTLD chunks)
    v1 = j[mean_keys[0]]
    v2 = j[mean_keys[1]]
    mean_1 = float(np.mean(v1)) if isinstance(v1, list) else float(v1)
    mean_2 = float(np.mean(v2)) if isinstance(v2, list) else float(v2)

    rec = {
        "metric":     metric,
        "comparison": comparison,
        "mean_1":     mean_1,
        "mean_2":     mean_2,
        "diff":       mean_2 - mean_1,
        "n1":         int(j["n1"]),
        "n2":         int(j["n2"]),
        # MWU + rangbiserial (aus JSON)
        "U":          float(j["mann_whitney_u"]),
        "p_mwu":      float(j["p_value"]),
        "r_rb":       float(j["effect_size_r"]),
        "abs_r_rb":   abs(float(j["effect_size_r"])),
        "rrb_effect": classify_rrb(j["effect_size_r"]),
    }

    if raw_a is not None and raw_b is not None:
        rec.update(compute_complementary_stats(raw_a, raw_b))
    else:
        # Fallback: nur Cohen's d aus Summary
        std_keys = mean_keys[0].replace("mean_", "std_"), mean_keys[1].replace("mean_", "std_")
        if std_keys[0] in j and std_keys[1] in j:
            d = cohens_d_from_summary(
                mean_1, float(j[std_keys[0]]), int(j["n1"]),
                mean_2, float(j[std_keys[1]]), int(j["n2"])
            )
            rec.update({
                "levene_W": np.nan, "p_levene": np.nan,
                "ks_D": np.nan,     "p_ks": np.nan,
                "cohens_d": d, "abs_cohens_d": abs(d),
                "cohen_effect": classify_cohen(d),
            })
        else:
            for k in ["levene_W", "p_levene", "ks_D", "p_ks",
                      "cohens_d", "abs_cohens_d", "cohen_effect"]:
                rec[k] = np.nan

    return rec


# ---------------------------------------------------------
# Hauptlogik
# ---------------------------------------------------------
def aggregate(quick=False):
    records = []

    # ── MTLD chunks ──────────────────────────────────────
    print("[1/6] MTLD chunks...")
    a, b = load_mtld_chunks("filtered")
    records.append(build_record(
        "MTLD", "A vs B (filtered)",
        RESULTS_MTLD_FILTERED / "mtld_chunks_filtered.json",
        ("mtld_chunks_a", "mtld_chunks_b"),  # nicht direkt nutzbar — Workaround unten
        a, b,
    ))
    # MTLD-Mean ist eigentlich ueber Chunks; nutze alignment-File fuer single-value:
    alignment_f = _load_json(RESULTS_MTLD_FILTERED / "mtld_alignment_filtered.json")["results"]
    records[-1]["mean_1"] = alignment_f.get("mtld_a_standard", np.mean(a))
    records[-1]["mean_2"] = alignment_f.get("mtld_b_standard", np.mean(b))
    records[-1]["diff"]   = records[-1]["mean_2"] - records[-1]["mean_1"]

    b2, c = load_mtld_chunks("llm")
    records.append(build_record(
        "MTLD", "B vs C (LLM)",
        RESULTS_MTLD_LLM / "mtld_chunks_llm.json",
        ("mtld_chunks_b", "mtld_chunks_c"),
        b2, c,
    ))
    alignment_l = _load_json(RESULTS_MTLD_LLM / "mtld_alignment_llm.json")["results"]
    records[-1]["mean_1"] = alignment_l.get("mtld_b_standard", np.mean(b2))
    records[-1]["mean_2"] = alignment_l.get("mtld_c_standard", np.mean(c))
    records[-1]["diff"]   = records[-1]["mean_2"] - records[-1]["mean_1"]

    # ── Shannon WORD ─────────────────────────────────────
    print("[2/6] Shannon WORD...")
    a, b = load_shannon_per_post("filtered", "word")
    records.append(build_record(
        "Shannon WORD", "A vs B (filtered)",
        RESULTS_SHANNON_FILTERED / "entropy_word_filtered.json",
        ("entropy_a", "entropy_b"),
        a, b,
    ))
    b2, c = load_shannon_per_post("llm", "word")
    records.append(build_record(
        "Shannon WORD", "B vs C (LLM)",
        RESULTS_SHANNON_LLM / "entropy_word_llm.json",
        ("entropy_b", "entropy_c"),
        b2, c,
    ))

    # ── Shannon POS ──────────────────────────────────────
    print("[3/6] Shannon POS...")
    a, b = load_shannon_per_post("filtered", "pos")
    records.append(build_record(
        "Shannon POS", "A vs B (filtered)",
        RESULTS_SHANNON_FILTERED / "entropy_pos_filtered.json",
        ("entropy_a", "entropy_b"),
        a, b,
    ))
    b2, c = load_shannon_per_post("llm", "pos")
    records.append(build_record(
        "Shannon POS", "B vs C (LLM)",
        RESULTS_SHANNON_LLM / "entropy_pos_llm.json",
        ("entropy_b", "entropy_c"),
        b2, c,
    ))

    # ── PTD ──────────────────────────────────────────────
    print("[4/6] PTD...")
    a, b = load_ptd("filtered")
    records.append(build_record(
        "PTD", "A vs B (filtered)",
        RESULTS_PTD_FILTERED / "syntax_parse_depth_filtered.json",
        ("mean_ptd_a", "mean_ptd_b"),
        a, b,
    ))
    b2, c = load_ptd("llm")
    records.append(build_record(
        "PTD", "B vs C (LLM)",
        RESULTS_PTD_LLM / "syntax_parse_depth_llm.json",
        ("mean_ptd_b", "mean_ptd_c"),
        b2, c,
    ))

    # ── FWR tagged (per-doc aus TAGGED CSV, Pipeline-Subsampling) ──
    print("[5/6] FWR tagged (aus TAGGED CSV)...")
    fwr_t_a, fwr_t_b_ab = compute_fwr_tagged_pair("a", "b")
    fwr_t_b_bc, fwr_t_c = compute_fwr_tagged_pair("b", "c")
    records.append(build_record(
        "FWR tagged", "A vs B (filtered)",
        RESULTS_FWR_FILTERED / "fwr_results_tagged_filtered.json",
        ("mean_fwr_a", "mean_fwr_b"),
        fwr_t_a, fwr_t_b_ab,
    ))
    records.append(build_record(
        "FWR tagged", "B vs C (LLM)",
        RESULTS_FWR_LLM / "fwr_results_tagged_llm.json",
        ("mean_fwr_b", "mean_fwr_c"),
        fwr_t_b_bc, fwr_t_c,
    ))

    # ── FWR untagged (spaCy live oder quick mode) ────────
    print("[6/6] FWR untagged...")
    if quick:
        print("  [quick mode] -> Cohen's d aus Summary, Levene/KS = N/A")
        records.append(build_record(
            "FWR untagged", "A vs B (filtered)",
            RESULTS_FWR_FILTERED / "fwr_results_filtered.json",
            ("mean_fwr_a", "mean_fwr_b"),
            None, None,
        ))
        records.append(build_record(
            "FWR untagged", "B vs C (LLM)",
            RESULTS_FWR_LLM / "fwr_results_llm.json",
            ("mean_fwr_b", "mean_fwr_c"),
            None, None,
        ))
    else:
        import spacy
        print("  Lade spaCy...")
        nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        # Jedes Paar separat subsamplen (B unterscheidet sich: vs A -> 8848, vs C -> 1196)
        fwr_u_a, fwr_u_b_ab = compute_fwr_untagged_pair("a", "b", nlp)
        fwr_u_b_bc, fwr_u_c = compute_fwr_untagged_pair("b", "c", nlp)
        records.append(build_record(
            "FWR untagged", "A vs B (filtered)",
            RESULTS_FWR_FILTERED / "fwr_results_filtered.json",
            ("mean_fwr_a", "mean_fwr_b"),
            fwr_u_a, fwr_u_b_ab,
        ))
        records.append(build_record(
            "FWR untagged", "B vs C (LLM)",
            RESULTS_FWR_LLM / "fwr_results_llm.json",
            ("mean_fwr_b", "mean_fwr_c"),
            fwr_u_b_bc, fwr_u_c,
        ))

    return records


# ---------------------------------------------------------
# Output
# ---------------------------------------------------------
def _df_to_md(df, float_fmt=".4g"):
    """Schlanker Markdown-Writer, kein tabulate-Dependency."""
    def fmt(v):
        if isinstance(v, float):
            return f"{v:{float_fmt}}" if not np.isnan(v) else "—"
        return str(v) if v is not None else "—"

    header = "| " + " | ".join(df.columns) + " |"
    sep    = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows   = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([header, sep] + rows)


def collect_alignment_diagnostics():
    """Sammelt die Vocabulary-Alignment-Werte (Topic-Drift-Diagnose) aus den
    MTLD- und Shannon-Alignment-JSONs. Diese stehen NICHT in den Haupt-
    Effektgroessen-Records, da sie ein deskriptives Diagnose-Werkzeug sind,
    kein Effektgroessen-Mass."""
    rows = []

    # --- MTLD: absolute aligned-Werte vorhanden ---
    m_f = _load_json(RESULTS_MTLD_FILTERED / "mtld_alignment_filtered.json")["results"]
    rows.append({
        "metric": "MTLD", "comparison": "A vs B (filtered)",
        "raw_ref": m_f["mtld_a_standard"], "raw_other": m_f["mtld_b_standard"],
        "other_aligned": m_f["mtld_b_filtered"],
        "diff_aligned": m_f["diff_mtld_filtered"],
    })
    m_l = _load_json(RESULTS_MTLD_LLM / "mtld_alignment_llm.json")["results"]
    rows.append({
        "metric": "MTLD", "comparison": "B vs C (LLM)",
        "raw_ref": m_l["mtld_b_standard"], "raw_other": m_l["mtld_c_standard"],
        "other_aligned": m_l["mtld_c_filtered_on_b"],
        "diff_aligned": m_l["diff_mtld_filtered"],
    })

    # --- Shannon WORD: nur diff gespeichert -> aligned-Wert rekonstruieren ---
    for layer, comp, fname, ref_key, other_key in [
        ("filtered", "A vs B (filtered)", "entropy_word_filtered.json", "entropy_a", "entropy_b"),
        ("llm",      "B vs C (LLM)",      "entropy_word_llm.json",      "entropy_b", "entropy_c"),
    ]:
        base = RESULTS_SHANNON_FILTERED if layer == "filtered" else RESULTS_SHANNON_LLM
        s = _load_json(base / fname)["results"]
        ref = s[ref_key]
        other = s[other_key]
        diff_filt = s["diff_entropy_filtered"]
        # Echten absoluten aligned-Wert nutzen, falls vorhanden; sonst rekonstruieren
        aligned_key = "entropy_b_filtered" if layer == "filtered" else "entropy_c_filtered_on_b"
        aligned = s.get(aligned_key, ref + diff_filt)
        rows.append({
            "metric": "Shannon WORD", "comparison": comp,
            "raw_ref": ref, "raw_other": other,
            "other_aligned": aligned,
            "diff_aligned": diff_filt,
        })

    return rows


def write_outputs(records, alignment_rows=None):
    df = pd.DataFrame(records)

    # Spalten-Reihenfolge fuer Lesbarkeit
    cols = [
        "metric", "comparison", "n1", "n2",
        "mean_1", "mean_2", "diff",
        "U", "p_mwu", "r_rb", "abs_r_rb", "rrb_effect",
        "levene_W", "p_levene",
        "ks_D",     "p_ks",
        "cohens_d", "abs_cohens_d", "cohen_effect",
    ]
    df = df[[c for c in cols if c in df.columns]]

    csv_path = RESULTS_SIGNIF / "aggregate_report.csv"
    df.to_csv(csv_path, index=False, float_format="%.6g")
    print(f"\n[CSV] {csv_path}")

    if alignment_rows:
        adf = pd.DataFrame(alignment_rows)[
            ["metric", "comparison", "raw_ref", "raw_other", "other_aligned", "diff_aligned"]
        ]
        align_csv = RESULTS_SIGNIF / "alignment_diagnostics.csv"
        adf.to_csv(align_csv, index=False, float_format="%.6g")
        print(f"[CSV] {align_csv}")

    md_path = RESULTS_SIGNIF / "aggregate_report.md"
    compact = df[["metric", "comparison", "abs_r_rb", "rrb_effect",
                  "abs_cohens_d", "cohen_effect", "p_levene", "p_ks"]]
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Aggregate Significance Report\n\n")
        f.write("Primary inferential statistic: Mann-Whitney U with rank-biserial effect size.\n")
        f.write("Complementary statistics: Levene (variance), Kolmogorov-Smirnov (distribution shape),\n")
        f.write("Cohen's d (parametric effect size).\n\n")
        f.write("## Compact view (effect sizes)\n\n")
        f.write(_df_to_md(compact, float_fmt=".4f"))
        f.write("\n\n## Full table\n\n")
        f.write(_df_to_md(df, float_fmt=".4g"))
        f.write("\n")

        if alignment_rows:
            adf = pd.DataFrame(alignment_rows)[
                ["metric", "comparison", "raw_ref", "raw_other", "other_aligned", "diff_aligned"]
            ]
            f.write("\n## Vocabulary-alignment diagnostics\n\n")
            f.write("One-sided vocabulary alignment (diagnostic, not an effect-size measure). ")
            f.write("`raw_ref` = reference corpus raw value; `raw_other` = comparison corpus raw value; ")
            f.write("`other_aligned` = comparison corpus restricted to reference vocabulary (min_freq>=3 for WORD). ")
            f.write("A near-zero or negative `diff_aligned` indicates the raw difference is driven by ")
            f.write("vocabulary novelty (topic shift) rather than by distributional structure.\n\n")
            f.write(_df_to_md(adf, float_fmt=".4g"))
            f.write("\n")
    print(f"[MD]  {md_path}")

    return df


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    quick = "--quick" in sys.argv

    print("=== AGGREGATE SIGNIFICANCE REPORT ===\n")
    if quick:
        print("Modus: --quick (FWR untagged ohne Levene/KS)\n")
    else:
        print("Modus: voll (FWR untagged mit spaCy-Live-Lauf, ~5-8 min)\n")

    records = aggregate(quick=quick)
    alignment_rows = collect_alignment_diagnostics()
    df = write_outputs(records, alignment_rows=alignment_rows)

    print("\n=== KOMPAKTE UEBERSICHT ===")
    compact = df[["metric", "comparison", "abs_r_rb", "rrb_effect",
                  "abs_cohens_d", "cohen_effect", "p_levene"]]
    print(compact.to_string(index=False, float_format=lambda x: f"{x:.4f}"))