# src/cleanup.py
import re
import html

def clean_reddit_text(text):
    """
    Cleaning Pipeline für Reddit-Texte. Wird in 01_preprocess.py verwendet.
    Entfernt HTML-Entitäten, Zero-Width-Spaces, Markdown Formatierungen, URLs und Collectors, 
    Code-Blöcke, Sonderzeichen und normalisiert Zeilenumbrüche.
    Gibt einen bereinigten String zurück.
    """
    if not isinstance(text, str): return ""
    text = html.unescape(html.unescape(text))
    text = text.replace('&#x200B;', '').replace('\u200b', '')
    text = re.sub(r'\*Processing img \S+\.\.\.\*', '', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'\[([^\]]*)\]\([^\)]+\)', r' \1 ', text)
    text = re.sub(r'\[\^?\d+\]:?', '', text)
    text = re.sub(r'\[\s*\.*\s*\]', '', text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = text.replace('\\', '').replace('""', '"') 
    text = re.sub(r'[#*_>\-]{1,}', ' ', text) 
    text = re.sub(r'\s+', ' ', text).strip()
    return text