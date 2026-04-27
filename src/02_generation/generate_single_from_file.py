# FOR TESTING ONLY
import json
from openai import OpenAI

client = OpenAI()  # liest OPENAI_API_KEY automatisch

from utils.paths import GENERATED

# Deine einzige Datei
JSONL_PATH = GENERATED / "prompts/prompts_style_B_1.jsonl"

# ---------------------------------------------------------
# Prompt laden
# ---------------------------------------------------------
with open(JSONL_PATH, "r", encoding="utf-8") as f:
    line = f.readline().strip()

item = json.loads(line)
prompt = item["prompt"]

print("\n--- Prompt loaded from file ---\n")
print(prompt)
print("\nGenerating synthetic text...\n")

# ---------------------------------------------------------
# LLM-Aufruf
# ---------------------------------------------------------
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You generate synthetic Reddit-style or academic-style text."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=350,
    temperature=0.9
)

print("\n--- GENERATED TEXT ---\n")
print(response.choices[0].message.content)
print("\n-----------------------\n")

# ---------------------------------------------------------
# Speichern
# ---------------------------------------------------------
filename = f"output_{prompt.replace(' ', '_')}.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(response.choices[0].message.content.strip())