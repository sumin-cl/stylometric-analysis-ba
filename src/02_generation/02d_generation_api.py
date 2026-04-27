import json
import time
from pathlib import Path
from openai import OpenAI

from utils.paths import GENERATED

# ---------------------------------------------------------
# OpenAI Client
# ---------------------------------------------------------

client = OpenAI()  # API-Key muss als ENV gesetzt sein: setx OPENAI_API_KEY=...

# ---------------------------------------------------------
# Load prompts
# ---------------------------------------------------------

def load_prompts(path):
    prompts = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                prompts.append(json.loads(line))
            except:
                pass
    return prompts

# ---------------------------------------------------------
# Generate synthetic text for one prompt
# ---------------------------------------------------------

def generate_text(prompt):
    """Send a prompt to GPT-4o-mini and return the generated text."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant generating synthetic Reddit-style or academic-style text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.9
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return None


# ---------------------------------------------------------
# Main generation loop
# ---------------------------------------------------------

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python 02d_generation_api.py <prompt_jsonl_path>")
        return

    prompt_path = Path(sys.argv[1])
    if not prompt_path.exists():
        print(f"File not found: {prompt_path}")
        return

    prompts = load_prompts(prompt_path)
    print(f"Loaded {len(prompts)} prompts.")

    out_dir = GENERATED / "synthetic_corpus"
    out_dir.mkdir(exist_ok=True)

    out_path = out_dir / f"{prompt_path.stem}_synthetic.jsonl"

    with open(out_path, "w", encoding="utf-8") as out:
        for i, item in enumerate(prompts, start=1):
            text = generate_text(item["prompt"])

            if text is None:
                print("Retrying after 3 seconds...")
                time.sleep(3)
                text = generate_text(item["prompt"])

            if text is None:
                print(f"Skipping prompt {i} due to repeated errors.")
                continue

            out.write(json.dumps({
                "style": item["style"],
                "seeds": item["seeds"],
                "prompt": item["prompt"],
                "synthetic_text": text
            }) + "\n")

            if i % 10 == 0:
                print(f"{i}/{len(prompts)} generated...")

            time.sleep(0.3)  # sanfte Rate-Limit-Entlastung

    print(f"Saved synthetic corpus to: {out_path}")


if __name__ == "__main__":
    main()
