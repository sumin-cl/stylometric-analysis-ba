import pandas as pd
import json
from pathlib import Path
from utils.paths import GENERATED

def validate_topics(file_name):
    path = GENERATED / file_name
    print(f"--- Validating {path} ---")

    df = pd.read_csv(path)

    errors = []
    warnings = []

    for idx, row in df.iterrows():
        row_id = row["id"]

        # --- JSON VALIDATION ---
        for col in ["nouns", "adjectives", "tokens"]:
            try:
                parsed = json.loads(row[col])
                if not isinstance(parsed, list):
                    errors.append((row_id, f"{col} is not a list"))
            except Exception as e:
                errors.append((row_id, f"Invalid JSON in {col}: {e}"))

        # --- EMPTY TOKENS ---
        try:
            tokens = json.loads(row["tokens"])
            if len(tokens) == 0:
                warnings.append((row_id, "tokens list is empty"))
        except:
            pass

        # --- EMPTY POS LISTS ---
        try:
            nouns = json.loads(row["nouns"])
            adjs = json.loads(row["adjectives"])
            if len(nouns) == 0 and len(adjs) == 0:
                warnings.append((row_id, "nouns AND adjectives empty"))
        except:
            pass

        # --- SAMPLE ID CHECK ---
        sample_id = row["sample_id"]
        if pd.isna(sample_id):
            pass  # allowed for full corpus
        else:
            if not str(sample_id).isdigit():
                warnings.append((row_id, f"Invalid sample_id: {sample_id}"))

        # --- SOURCE CHECK ---
        source = row["source"]
        if not isinstance(source, str) or len(source.strip()) == 0:
            warnings.append((row_id, "source is empty or invalid"))

        # --- OUTLIER CHECK ---
        if len(json.loads(row["nouns"])) > 2000:
            warnings.append((row_id, "nouns unusually long (>2000) — preprocessing issue?"))

    # --- SUMMARY ---
    print("\n--- VALIDATION SUMMARY ---")
    print(f"Rows checked: {len(df)}")
    print(f"Errors:   {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print("\n--- ERRORS ---")
        for row_id, msg in errors[:20]:
            print(f"Row {row_id}: {msg}")
        if len(errors) > 20:
            print(f"... {len(errors)-20} more")

    if warnings:
        print("\n--- WARNINGS ---")
        for row_id, msg in warnings[:20]:
            print(f"Row {row_id}: {msg}")
        if len(warnings) > 20:
            print(f"... {len(warnings)-20} more")

    print("\nDone.\n")


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python topic_validation.py <filename>")
        return

    validate_topics(sys.argv[1])


if __name__ == "__main__":
    main()
