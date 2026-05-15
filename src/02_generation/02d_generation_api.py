"""
Generiert synthetischen Korpus C ueber die OpenAI Chat Completions API.

Features:
- Modellwahl via --model (default gpt-4o)
- Cost-Estimate mit Confirm-Prompt vor Lauf-Start
- Resume-Mode: bereits generierte Prompts werden uebersprungen
- Metadaten (model, temperature, max_tokens, timestamp) pro Eintrag

Verwendung:
    python 02d_generation_api.py <prompt_jsonl_path>
    python 02d_generation_api.py <prompt_jsonl_path> --model gpt-4o
    python 02d_generation_api.py <prompt_jsonl_path> --model gpt-4o-mini --temperature 0.7
    python 02d_generation_api.py <prompt_jsonl_path> --yes   # Confirm-Prompt skippen

OPENAI_API_KEY muss als ENV gesetzt sein.
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

from utils.paths import GENERATED_CORPUS

# ---------------------------------------------------------
# OpenAI Pricing (USD per 1M tokens) — Stand Mai 2026
# Quelle: https://openai.com/api/pricing/  (bitte vor groessen Laeufen verifizieren)
# ---------------------------------------------------------

PRICING = {
    "gpt-4o":         {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":    {"input": 0.15,  "output": 0.60},
    "gpt-4.1":        {"input": 2.00,  "output": 8.00},
    "gpt-4.1-mini":   {"input": 0.40,  "output": 1.60},
    "gpt-5.4":        {"input": 2.50,  "output": 15.00},
    "gpt-5.5":        {"input": 5.00,  "output": 30.00},
}
PRICING_DATE = "2026-05-12"

# ---------------------------------------------------------
# Token counting: tiktoken if available, sonst Schaetzung
# ---------------------------------------------------------

def get_token_counter(model):
    """Liefert eine count_tokens(text)-Funktion. Nutzt tiktoken wenn vorhanden,
    sonst eine Approximation (~1.3 Tokens pro Wort)."""
    try:
        import tiktoken
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")  # Fallback fuer neuere Modelle
        return lambda text: len(enc.encode(text)), "tiktoken"
    except ImportError:
        return lambda text: int(len(text.split()) * 1.3), "approx"


def estimate_cost(prompts, model, max_output_tokens, sample_for_input=50):
    """
    Schaetzt die Gesamtkosten:
    - Input: genaue Token-Counts ueber alle Prompts (oder Stichprobe wenn n > sample_for_input * 10)
    - Output: max_output_tokens pro Prompt als Worst-Case-Annahme
    """
    if model not in PRICING:
        return None, f"Modell '{model}' nicht im PRICING-Dict. Edit PRICING in 02d_generation_api.py oder verifiziere Preise auf openai.com."

    count_tokens, method = get_token_counter(model)

    # System-Prompt aus generate_text — muss mitgezaehlt werden!
    system_msg = "You are a helpful assistant generating synthetic Reddit-style or academic-style text."
    system_tokens = count_tokens(system_msg)

    n = len(prompts)
    # Bei n > 500: Stichprobe nehmen statt alle zaehlen
    if n > 500:
        sample = prompts[:sample_for_input]
        avg_prompt_tokens = sum(count_tokens(p["prompt"]) for p in sample) / len(sample)
        total_input_tokens = int(n * (system_tokens + avg_prompt_tokens))
        sampling_note = f" (Input geschaetzt auf Basis von {sample_for_input} Prompts)"
    else:
        total_input_tokens = sum(system_tokens + count_tokens(p["prompt"]) for p in prompts)
        sampling_note = ""

    # Output: Worst-Case Annahme = jeder Prompt nutzt max_output_tokens voll aus
    total_output_tokens = n * max_output_tokens

    rates = PRICING[model]
    cost_input  = total_input_tokens  / 1_000_000 * rates["input"]
    cost_output = total_output_tokens / 1_000_000 * rates["output"]
    cost_total  = cost_input + cost_output

    summary = (
        f"\n=== COST-ESTIMATE ===\n"
        f"Modell:               {model}\n"
        f"Token-Counter:        {method}\n"
        f"Prompts:              {n}\n"
        f"Input Tokens (sum):   {total_input_tokens:>10,d}{sampling_note}\n"
        f"Output Tokens (max):  {total_output_tokens:>10,d}  (worst case: max_tokens={max_output_tokens} voll ausgeschoepft)\n"
        f"Pricing (per 1M):     in ${rates['input']:.2f}  out ${rates['output']:.2f}  (Stand {PRICING_DATE})\n"
        f"Cost Input:           ${cost_input:>7.3f}\n"
        f"Cost Output (max):    ${cost_output:>7.3f}\n"
        f"GESAMT (worst case):  ${cost_total:>7.3f}\n"
        f"\n  Realistische Kosten meist 50-70% des Worst-Case, da Outputs selten max_tokens voll ausschoepfen."
        f"\n  Verifiziere aktuelle Preise auf openai.com/api/pricing bevor du groessere Laeufe startest."
    )
    return cost_total, summary

# ---------------------------------------------------------
# Prompts laden
# ---------------------------------------------------------

def load_prompts(path):
    prompts = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                prompts.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return prompts


def load_already_done(out_path):
    """Liest existierendes Output-File und liefert Set der bereits verarbeiteten Prompts."""
    if not out_path.exists():
        return set()
    done = set()
    with open(out_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                done.add(json.loads(line)["prompt"])
            except (json.JSONDecodeError, KeyError):
                pass
    return done

# ---------------------------------------------------------
# Generation
# ---------------------------------------------------------

def generate_text(client, prompt, model, temperature, max_tokens):
    """Sendet einen Prompt an die API und liefert den generierten Text."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant generating synthetic Reddit-style or academic-style text."},
                {"role": "user",   "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"  [API-Fehler] {e}")
        return None

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic LLM corpus via OpenAI API.")
    parser.add_argument("prompt_path", type=Path, help="Path to prompts JSONL file")
    parser.add_argument("--model",       default="gpt-4o", help="Model name (default: gpt-4o)")
    parser.add_argument("--temperature", type=float, default=0.9, help="Sampling temperature (default: 0.9)")
    parser.add_argument("--max-tokens",  type=int,   default=500, help="Max output tokens (default: 500)")
    parser.add_argument("--sleep",       type=float, default=0.3, help="Sleep between requests (default: 0.3s)")
    parser.add_argument("--yes", "-y",   action="store_true", help="Skip cost-estimate confirmation")
    args = parser.parse_args()

    if not args.prompt_path.exists():
        print(f"File not found: {args.prompt_path}")
        sys.exit(1)

    prompts = load_prompts(args.prompt_path)
    print(f"Loaded {len(prompts)} prompts from {args.prompt_path.name}")

    # ─── Cost-Estimate ─────────────────────────────────────
    cost_total, summary = estimate_cost(prompts, args.model, args.max_tokens)
    print(summary)

    if not args.yes and cost_total is not None:
        try:
            answer = input("\nFortfahren? [y/N] ").strip().lower()
        except KeyboardInterrupt:
            print("\nAbgebrochen.")
            sys.exit(0)
        if answer not in ("y", "yes", "j", "ja"):
            print("Abgebrochen.")
            sys.exit(0)

    # ─── Output-Pfad + Resume ──────────────────────────────
    out_dir = GENERATED_CORPUS
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.prompt_path.stem}_synthetic.jsonl"

    done = load_already_done(out_path)
    if done:
        print(f"\n[RESUME] {len(done)} Prompts bereits in {out_path.name}, werden uebersprungen.")
    todo = [p for p in prompts if p["prompt"] not in done]
    print(f"Zu verarbeiten: {len(todo)} Prompts.\n")

    if not todo:
        print("Nichts zu tun.")
        return

    # ─── Run ───────────────────────────────────────────────
    client = OpenAI()  # API-Key aus ENV
    successes, failures = 0, 0

    with open(out_path, "a", encoding="utf-8") as out:
        for i, item in enumerate(todo, start=1):
            text = generate_text(client, item["prompt"], args.model, args.temperature, args.max_tokens)

            if text is None:
                print(f"  Retry nach 3s...")
                time.sleep(3)
                text = generate_text(client, item["prompt"], args.model, args.temperature, args.max_tokens)

            if text is None:
                print(f"  [SKIP] Prompt {i} nach wiederholten Fehlern.")
                failures += 1
                continue

            out.write(json.dumps({
                "style":          item["style"],
                "seeds":          item["seeds"],
                "prompt":         item["prompt"],
                "synthetic_text": text,
                "model":          args.model,
                "temperature":    args.temperature,
                "max_tokens":     args.max_tokens,
                "timestamp":      datetime.now(timezone.utc).isoformat(),
            }) + "\n")
            out.flush()  # incremental persist gegen Crash-Datenverlust
            successes += 1

            if i % 25 == 0:
                print(f"  {i}/{len(todo)} generiert  (Erfolg: {successes}, Fehler: {failures})")

            time.sleep(args.sleep)

    print(f"\n=== FERTIG ===")
    print(f"Erfolg:  {successes}")
    print(f"Fehler:  {failures}")
    print(f"Gespeichert: {out_path}")


if __name__ == "__main__":
    main()