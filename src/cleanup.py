# src/cleanup.py
import re
import html

def clean_reddit_text(text):
    if not isinstance(text, str): return ""
    # 1. Double Unescape
    text = html.unescape(html.unescape(text))
    # 2. Garbage Removal
    text = text.replace('&#x200B;', '').replace('\u200b', '')
    text = re.sub(r'\*Processing img \S+\.\.\.\*', '', text)
    # 3. Code-Blöcke & Inline Code
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', '', text)
    # 4. Markdown Links & Artefakte
    text = re.sub(r'\[([^\]]*)\]\([^\)]+\)', r' \1 ', text)
    text = re.sub(r'\[\^?\d+\]:?', '', text)
    text = re.sub(r'\[\s*\.*\s*\]', '', text)
    # 5. URLs & Collector
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = text.replace('\\', '').replace('""', '"') # Doppelzeichen
    text = re.sub(r'[#*_>\-]{1,}', ' ', text) # Header (#), Bold/Italic (* oder _), Listen-Marker (-)
    text = re.sub(r'\s+', ' ', text).strip() # Whitespace
    return text