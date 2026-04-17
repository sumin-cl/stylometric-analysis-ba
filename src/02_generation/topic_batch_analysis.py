import re
import json
import pandas as pd
from pathlib import Path
from collections import Counter
from utils.paths import GENERATED

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

HTML_HEADER = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Topic Batch Analysis</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; }
h1 { color: #333; }
h2 { margin-top: 40px; }
table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
th { background-color: #f2f2f2; }
details { margin-bottom: 20px; }
summary { font-weight: bold; cursor: pointer; }
.code { color: #b30000; }
</style>
</head>
<body>
<h1>Topic Batch Analysis</h1>
"""

HTML_FOOTER = """
</body>
</html>
"""

NOISE_PATTERN = re.compile(r"[=<>]|np\.|http|www|\.com|\.py|\.cpp|\d")

def load_topics(path: Path):
    df = pd.read_csv(path)
    df["nouns"] = df["nouns"].apply(json.loads)
    df["adjectives"] = df["adjectives"].apply(json.loads)
    df["tokens"] = df["tokens"].apply(json.loads)
    return df

def is_noise_token(tok: str) -> bool:
    return bool(NOISE_PATTERN.search(tok))

def analyze_file(path: Path):
    df = load_topics(path)

    noun_counts = Counter()
    adj_counts = Counter()
    token_counts = Counter()
    noise_tokens = Counter()

    for _, row in df.iterrows():
        noun_counts.update(row["nouns"])
        adj_counts.update(row["adjectives"])
        token_counts.update(row["tokens"])
        for t in row["tokens"]:
            if is_noise_token(t):
                noise_tokens[t] += 1

    stats = {
        "rows": len(df),
        "avg_nouns": df["nouns"].apply(len).mean(),
        "avg_adjs": df["adjectives"].apply(len).mean(),
        "avg_tokens": df["tokens"].apply(len).mean(),
        "empty_pos": int(((df["nouns"].apply(len) == 0) & (df["adjectives"].apply(len) == 0)).sum()),
        "empty_tokens": int((df["tokens"].apply(len) == 0).sum()),
        "top_nouns": noun_counts.most_common(20),
        "top_adjs": adj_counts.most_common(20),
        "top_tokens": token_counts.most_common(20),
        "noise_tokens": noise_tokens.most_common(20),
    }

    return stats

def pre_post_pairs(files):
    """Erkennt pre/post anhand des Dateinamens."""
    pairs = []
    by_stem = {}
    for f in files:
        stem = f.replace("_pre", "").replace("_post", "")
        by_stem.setdefault(stem, []).append(f)
    for stem, group in by_stem.items():
        pre = [g for g in group if "_pre" in g]
        post = [g for g in group if "_post" in g]
        if pre and post:
            pairs.append((pre[0], post[0]))
    return pairs

def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

def generate_plots(results, plot_dir: Path):
    if not HAS_MPL:
        print("matplotlib nicht installiert – überspringe Plots.")
        return
    plot_dir.mkdir(exist_ok=True)
    for file, stats in results.items():
        tokens = [t for t, _ in stats["top_tokens"]]
        counts = [c for _, c in stats["top_tokens"]]
        if not tokens:
            continue
        plt.figure(figsize=(10, 4))
        plt.bar(tokens, counts)
        plt.xticks(rotation=45, ha="right")
        plt.title(f"Top Tokens – {file}")
        plt.tight_layout()
        out = plot_dir / f"{file}_top_tokens.png"
        plt.savefig(out)
        plt.close()
        print(f"Plot gespeichert: {out}")

def generate_html_report(results, output_path: Path):
    html = [HTML_HEADER]

    # Summary
    html.append("<h2>Summary</h2>")
    html.append("<table><tr><th>File</th><th>Rows</th><th>Ø Nouns</th><th>Ø Adjs</th><th>Ø Tokens</th><th>Empty POS</th><th>Empty Tokens</th></tr>")
    for file, stats in results.items():
        html.append(
            f"<tr><td>{file}</td>"
            f"<td>{stats['rows']}</td>"
            f"<td>{stats['avg_nouns']:.2f}</td>"
            f"<td>{stats['avg_adjs']:.2f}</td>"
            f"<td>{stats['avg_tokens']:.2f}</td>"
            f"<td>{stats['empty_pos']}</td>"
            f"<td>{stats['empty_tokens']}</td></tr>"
        )
    html.append("</table>")

    # pre/post Vergleich
    html.append("<h2>Pre/Post Comparison (Top Tokens Overlap)</h2>")
    html.append("<table><tr><th>Pair</th><th>Jaccard Top Tokens</th></tr>")
    pairs = pre_post_pairs(list(results.keys()))
    for pre, post in pairs:
        pre_tokens = [t for t, _ in results[pre]["top_tokens"]]
        post_tokens = [t for t, _ in results[post]["top_tokens"]]
        jac = jaccard(pre_tokens, post_tokens)
        html.append(f"<tr><td>{pre} / {post}</td><td>{jac:.2f}</td></tr>")
    if not pairs:
        html.append("<tr><td colspan='2'>No pre/post pairs detected.</td></tr>")
    html.append("</table>")

    # Detail pro Datei
    for file, stats in results.items():
        html.append(f"<h2>{file}</h2>")

        for label, title in [
            ("top_nouns", "Top Nouns"),
            ("top_adjs", "Top Adjectives"),
            ("top_tokens", "Top Tokens"),
            ("noise_tokens", "Potential Noise Tokens"),
        ]:
            html.append(f"<details><summary>{title}</summary>")
            html.append("<table><tr><th>Token</th><th>Count</th></tr>")
            for token, count in stats[label]:
                cls = "code" if label == "noise_tokens" else ""
                html.append(f"<tr><td class='{cls}'>{token}</td><td>{count}</td></tr>")
            html.append("</table></details>")

    html.append(HTML_FOOTER)
    output_path.write_text("\n".join(html), encoding="utf-8")
    print(f"HTML report saved to: {output_path}")

def main():
    topic_files = sorted([f.name for f in GENERATED.glob("*_topics.csv")])
    if not topic_files:
        print("No topic files found.")
        return

    results = {}
    for file in topic_files:
        print(f"Analyzing {file}...")
        stats = analyze_file(GENERATED / file)
        results[file] = stats

    report_dir = GENERATED / "reports"
    report_dir.mkdir(exist_ok=True)

    output_path = report_dir / "topic_batch_analysis_report.html"
    generate_html_report(results, output_path)

    plot_dir = report_dir / "plots"
    generate_plots(results, plot_dir)

if __name__ == "__main__":
    main()
