Zur dynamischen Token-Range-Idee: methodisch ein wirklich starker Punkt. Bei mehreren Subreddits wäre per-corpus-Adaptation sauberer als ein fixes Fenster für alle. Mögliche Umsetzung später wäre: 02_baseline.py legt für jedes Korpus Median/IQR ab, 01b_filter.py liest die JSON, defaultet auf z.B. p10–p90 oder Median±IQR. Häng's dir in info/notes.txt als Future Work, sonst geht's verloren.

Wie funktioniert Shannon:
# Erst:
python src\01_preprocessing\01b_pos_tagger.py filtered

# Dann (schnell, lädt POS-Tags aus tagged file):
python src\03_analysis\03_shannon.py filtered

# Reihenfolge umgekehrt → läuft auch durch, aber langsamer (spaCy live)

FWR: 
python src\03_analysis\03_fwr_ratio.py filtered
python src\03_analysis\03_fwr_ratio_tagged.py filtered

PTD:
python src\01_preprocessing\01_parse_and_cache.py filtered  # erst!
python src\03_analysis\03_ptd_syntax.py filtered

