# src/nlp_utils.py
import spacy
import math
import pandas as pd
from collections import Counter
from tqdm import tqdm

try:
    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"]) 
except:
    print("SpaCy Modell nicht gefunden. Bitte: python -m spacy download en_core_web_sm")

def get_flat_tokens(df_series, use_tqdm=True):
    """
    Nimmt eine Pandas-Serie von Texten und gibt eine flache Liste aller Wörter zurück.
    Lowercased.
    """
    if isinstance(df_series, list):
        df_series = pd.Series(df_series)

    iterator = df_series.astype(str)
    if use_tqdm:
        iterator = tqdm(iterator, desc="Tokenisiere Wörter")

    tokens = []
    for text in iterator:
        tokens.extend(text.lower().split())
    return tokens

def get_pos_tags(df_series):
    """
    Nimmt eine Pandas-Serie und gibt eine flache Liste aller POS-Tags zurück.
    """
    print("Extrahiere POS-Tags mit spaCy (das kann kurz dauern)...")
    all_tags = []
    for doc in nlp.pipe(df_series.astype(str), batch_size=100):
        all_tags.extend([token.pos_ for token in doc])
    return all_tags

def downsample_corpora(a, b):
    """
    Lädt zwei Korpora und downsamplet sie auf die Länge des kleineren Version.
    """
    df_a = pd.read_csv(a)
    df_b = pd.read_csv(b)

    size = min(len(df_a), len(df_b))
    df_a = df_a.sample(n=size, random_state=42)
    df_b = df_b.sample(n=size, random_state=42)

    print(f"Downsampled auf {size} Posts pro Korpus.")

    return df_a, df_b, size

def calculate_shannon_entropy(items):
    """
    Berechnet die Shannon-Entropie für eine beliebige Liste (Wörter oder Tags).
    H(X) = - sum(p * log2(p))
    """
    if not items:
        return 0.0
    
    counts = Counter(items)
    total = len(items)
    entropy = 0.0
    
    for count in tqdm(counts.values(), desc="Berechne Entropie"):
        p = count / total
        entropy -= p * math.log2(p)
        
    return entropy

def filter_list_by_reference(target_list, reference_list, min_freq=3):
    """
    Filtert target_list: Behält nur Elemente, die in reference_list 
    mindestens min_freq mal vorkommen.
    Gibt die gefilterte Liste zurück.
    """
    ref_counts = Counter(reference_list)
    valid_vocab = {item for item, count in ref_counts.items() if count >= min_freq}
    
    filtered = [x for x in tqdm(target_list, desc="Filtere Tokens nach Referenzvokabular") if x in valid_vocab]
    return filtered

try:
    nlp_parser = spacy.load("en_core_web_sm", disable=["ner"]) 
except:
    pass

def get_max_tree_depth(sent):
    """
    Berechnet die maximale Tiefe eines Satz-Baumes (Dependency Tree).
    Wurzel = Tiefe 0.
    """
    root = sent.root
    
    def get_depth(token):
        if not list(token.children):
            return 0
        return 1 + max(get_depth(child) for child in token.children)
    
    return get_depth(root)

def analyze_syntax_complexity(df_series):
    """
    Berechnet die durchschnittliche Baumtiefe pro Post.
    Ein Post kann mehrere Sätze haben, daher nehmen wir den Durchschnitt des Posts.
    """
    print("Analysiere Syntax-Bäume (Dependency Parsing)...")
    depths = []

    total = len(df_series)
    for doc in tqdm(nlp_parser.pipe(df_series.astype(str), batch_size=50), total=total):
        sent_depths = [get_max_tree_depth(sent) for sent in doc.sents]
        if sent_depths:
            avg_post_depth = sum(sent_depths) / len(sent_depths)
            depths.append(avg_post_depth)
        else:
            depths.append(0)
            
    return depths

def calculate_fwr_per_doc(df_series):
    """
    Berechnet die FWR (Function Word Ratio) pro Dokument.
    FWR = Funktionswörter / Inhaltswörter
    Gibt eine Liste von Floats zurück.
    """
    print("Berechne Function Word Ratio (FWR)...")
    ratios = []
    
    content_tags = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
    func_tags = {"ADP", "AUX", "CONJ", "CCONJ", "SCONJ", "DET", "PART", "PRON"}

    for doc in tqdm(nlp.pipe(df_series.astype(str), batch_size=100, disable=["parser", "ner"])):
        n_func = 0
        n_content = 0
        
        for token in doc:
            pos = token.pos_
            if pos in content_tags:
                n_content += 1
            elif pos in func_tags:
                n_func += 1
        
        if n_content > 0:
            ratio = n_func / n_content
        else:
            ratio = 0.0 
            
        ratios.append(ratio)
        
    return ratios

import os, json
from datetime import datetime

def save_as_json(filename, metadata, results):
    """
    Speichert Analyse-Ergebnisse als JSON in data/final/results/.
    filename: Name der Datei (z.B. 'entropy_results.json')
    metadata: Dictionary mit Infos (sample_size, corpus_names, etc.)
    results: Dictionary mit den Messwerten
    """
    output_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'final', 'results'))
    os.makedirs(output_dir, exist_ok=True)
    
    full_data = {
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata,
        "results": results
    }
    
    target_path = os.path.join(output_dir, filename)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=4)
    
    print(f"\n[EXPORT] Ergebnisse gesichert in: {target_path}")

def append_to_json(filename, new_results):
    """
    Öffnet eine bestehende JSON-Datei in data/final/results/,
    merged neue Ergebnisse hinein und speichert sie wieder.
    """
    output_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'final', 'results'))
    target_path = os.path.join(output_dir, filename)

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["results"].update(new_results)
    data["results"]["updated_at"] = datetime.now().isoformat()

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[APPEND] Mann-Whitney-U wurde hinzugefügt zu: {target_path}")
