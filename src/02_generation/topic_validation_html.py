import pandas as pd
import json
from pathlib import Path
from utils.paths import GENERATED

HTML_HEADER = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Topic Validation Report</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; }
h1 { color: #333; }
h2 { margin-top: 40px; }
table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
th { background-color: #f2f2f2; }
.error { background-color: #ffcccc; }
.warning { background-color: #fff3cd; }
.ok { background-color: #d4edda; }
details { margin-bottom: 20px; }
summary { font-weight: bold; cursor: pointer; }
</style>
</head>
<body>
<h1>Topic Validation Report</h1>
"""

HTML_FOOTER = """
</body>
</html>
"""

def validate_file(path: Path):
    df = pd.read_csv(path)
    errors = []
    warnings = []

    for idx, row in df.iterrows():
        row_id = row["id"]

        # JSON validation
        for col in ["nouns", "adjectives", "tokens"]:
            try:
                parsed = json.loads(row[col])
                if not isinstance(parsed, list):
                    errors.append((row_id, col, "Not a list"))
            except Exception as e:
                errors.append((row_id, col, f"Invalid JSON: {e}"))

        # Empty tokens
        try:
            tokens = json.loads(row["tokens"])
            if len(tokens) == 0:
                warnings.append((row_id, "tokens", "Tokens list is empty"))
        except:
            pass

        # Empty POS lists
        try:
            nouns = json.loads(row["nouns"])
            adjs = json.loads(row["adjectives"])
            if len(nouns) == 0 and len(adjs) == 0:
                warnings.append((row_id, "POS", "Both nouns and adjectives empty"))
        except:
            pass

        # sample_id
        sample_id = row["sample_id"]
        if not (pd.isna(sample_id) or str(sample_id).isdigit()):
            warnings.append((row_id, "sample_id", f"Invalid sample_id: {sample_id}"))

        # source
        source = row["source"]
        if not isinstance(source, str) or len(source.strip()) == 0:
            warnings.append((row_id, "source", "Source empty or invalid"))

        # Outlier
        if len(json.loads(row["nouns"])) > 2000:
            warnings.append((row_id, "nouns", "Unusually long nouns list (>2000)"))

    return errors, warnings, len(df)


def generate_html_report(files, output_path):
    html = [HTML_HEADER]
    html.append("<h2>Summary</h2>")
    html.append("<table><tr><th>File</th><th>Rows</th><th>Errors</th><th>Warnings</th></tr>")

    results = {}

    for file in files:
        path = GENERATED / file
        errors, warnings, rows = validate_file(path)
        results[file] = (errors, warnings, rows)

        html.append(
            f"<tr><td>{file}</td><td>{rows}</td>"
            f"<td>{len(errors)}</td><td>{len(warnings)}</td></tr>"
        )

    html.append("</table>")

    # Detailed sections
    for file, (errors, warnings, rows) in results.items():
        html.append(f"<h2>{file}</h2>")

        # Errors
        html.append("<details><summary>Errors</summary>")
        if errors:
            html.append("<table><tr><th>Row</th><th>Column</th><th>Message</th></tr>")
            for row_id, col, msg in errors:
                html.append(
                    f"<tr class='error'><td>{row_id}</td><td>{col}</td><td>{msg}</td></tr>"
                )
            html.append("</table>")
        else:
            html.append("<p class='ok'>No errors found.</p>")
        html.append("</details>")

        # Warnings
        html.append("<details><summary>Warnings</summary>")
        if warnings:
            html.append("<table><tr><th>Row</th><th>Column</th><th>Message</th></tr>")
            for row_id, col, msg in warnings:
                html.append(
                    f"<tr class='warning'><td>{row_id}</td><td>{col}</td><td>{msg}</td></tr>"
                )
            html.append("</table>")
        else:
            html.append("<p class='ok'>No warnings found.</p>")
        html.append("</details>")

    html.append(HTML_FOOTER)

    output_path.write_text("\n".join(html), encoding="utf-8")
    print(f"HTML report saved to: {output_path}")


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python topic_validation_html.py <file1> <file2> ...")
        return

    files = sys.argv[1:]
    report_dir = GENERATED / "reports"
    report_dir.mkdir(exist_ok=True)

    output_path = report_dir / "topic_validation_report.html"
    generate_html_report(files, output_path)


if __name__ == "__main__":
    main()
