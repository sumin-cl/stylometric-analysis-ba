# src/00_extraction/00_extract_c_from_jsonl.py
"""
Liest generierte synthetische Texte aus einer *_synthetic.jsonl-Datei
und speichert sie als corpus_c_raw.csv im Extraction-Ordner.

Input:  data/final/02_generation/synthetic_corpus/*_synthetic.jsonl
Output: data/final/00_extraction/corpus_c_raw.csv

Verwendung:
    python src/00_extraction/00_extract_c_from_jsonl.py
    python src/00_extraction/00_extract_c_from_jsonl.py pfad/zur/datei.jsonl
"""
import json
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from utils.paths import GENERATED_CORPUS, EXTRACTED


def extract_from_jsonl(jsonl_path=None):
    if jsonl_path is None:
        files = sorted(GENERATED_CORPUS.glob("*_synthetic.jsonl"))
        if not files:
            raise FileNotFoundError(
                f"Keine *_synthetic.jsonl in {GENERATED_CORPUS} gefunden.\n"
                "Bitte zuerst LLM-Korpus generieren (Option [4] im Synthetic-Menü)."
            )
        jsonl_path = files[-1]
        print(f"Automatisch gewählt: {jsonl_path.name}")

    jsonl_path = Path(jsonl_path)
    print(f"Lese: {jsonl_path}")

    records = []
    errors  = 0
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                text = data.get("synthetic_text", "").strip()
                if text:
                    records.append({
                        "id":   f"llm_{i}",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "post": text
                    })
            except json.JSONDecodeError as e:
                errors += 1
                print(f"  [WARN] Zeile {i} übersprungen: {e}")

    df      = pd.DataFrame(records)
    out     = EXTRACTED / "corpus_c_raw.csv"
    df.to_csv(out, index=False)
    print(f"\n[OK] {len(df)} synthetische Texte gespeichert: {out}")
    if errors:
        print(f"[WARN] {errors} fehlerhafte Zeilen übersprungen.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    extract_from_jsonl(path)