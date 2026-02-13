# src/nlp_utils.py
import spacy
import math
import pandas as pd
from collections import Counter
from tqdm import tqdm

try:
    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"]) # Wir brauchen nur den Tagger
except:
    print("SpaCy Modell nicht gefunden. Bitte: python -m spacy download en_core_web_sm")

def get_flat_tokens(df_series):
    """
    Nimmt eine Pandas-Serie von Texten und gibt eine flache Liste aller Wörter zurück.
    Lowercased.
    """
    return " ".join(df_series.astype(str)).lower().split()

def get_pos_tags(df_series):
    """
    Nimmt eine Pandas-Serie und gibt eine flache Liste aller POS-Tags zurück.
    """
    print("Extrahiere POS-Tags mit spaCy (das kann kurz dauern)...")
    all_tags = []
    # nlp.pipe verarbeitet Texte schneller
    for doc in nlp.pipe(df_series.astype(str), batch_size=100):
        # pos_ gibt grobe Tags (NOUN), tag_ gibt feine (NN, NNS)
        # Für Entropie ist pos_ (Universal POS Tags) meist besser vergleichbar.
        all_tags.extend([token.pos_ for token in doc])
    return all_tags

def downsample_corpora(a, b):
    df_a = pd.read_csv(a)
    df_b = pd.read_csv(b)

    # Downsampling für fairen Vergleich
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
    
    for count in counts.values():
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
    
    filtered = [x for x in target_list if x in valid_vocab]
    return filtered

# Für Tree Depth brauchen wir einen Parser
try:
    nlp_parser = spacy.load("en_core_web_sm", disable=["ner"]) # NER brauchen wir nicht
except:
    pass

def get_max_tree_depth(sent):
    """
    Berechnet die maximale Tiefe eines Satz-Baumes (Dependency Tree).
    Wurzel = Tiefe 0.
    """
    # Root finden
    root = sent.root
    
    # Rekursive Funktion zur Tiefenmessung
    def get_depth(token):
        if not list(token.children):
            return 0
        return 1 + max(get_depth(child) for child in token.children)
    
    return get_depth(root)

def analyze_syntax_complexity(df_series):
    """
    Berechnet die durchschnittliche Baumtiefe pro Post.
    """
    print("Analysiere Syntax-Bäume (Dependency Parsing)...")
    depths = []
    
    # nlp.pipe mit tqdm für Fortschrittsbalken
    # batch_size=50 ist gut für Parsing
    total = len(df_series)
    for doc in tqdm(nlp_parser.pipe(df_series.astype(str), batch_size=50), total=total):
        # Ein Post kann mehrere Sätze haben, daher nehmen wir den Durchschnitt des Posts.
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
    
    # Definition der Tags (Universal POS Tags)
    # Content: NOUN, VERB, ADJ, ADV, PROPN (Eigennamen)
    content_tags = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
    # Function: Alles andere, was Struktur baut
    func_tags = {"ADP", "AUX", "CONJ", "CCONJ", "SCONJ", "DET", "PART", "PRON"}

    # Wir brauchen nur den Tagger, keinen Parser für diese Analyse
    for doc in tqdm(nlp.pipe(df_series.astype(str), batch_size=100, disable=["parser", "ner"])):
        n_func = 0
        n_content = 0
        
        for token in doc:
            pos = token.pos_
            if pos in content_tags:
                n_content += 1
            elif pos in func_tags:
                n_func += 1
        
        # Berechnung pro Post
        if n_content > 0:
            ratio = n_func / n_content
        else:
            # Fallback für leere Posts
            ratio = 0.0 
            
        ratios.append(ratio)
        
    return ratios