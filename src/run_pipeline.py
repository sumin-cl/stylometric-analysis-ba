# src/run_pipeline.py
import subprocess
import shutil
import datetime
from utils.paths import FINAL, DATA
from pathlib import Path
import os
import sys

os.chdir(Path(__file__).resolve().parent)

STEPS = [
    ("00_extraction/00_extract_a_kaggle.py", "Extrahiere Korpus A"),
    ("00_extraction/00_extract_b_arctic.py", "Extrahiere Korpus B"),
    ("01_preprocessing/01_preprocess.py", "Preprocessing"),
    ("01_preprocessing/01b_pos_tagger.py", "POS-Tagging"),
    ("01_preprocessing/01_parse_and_cache.py", "Syntax-Parsing cachen"),
    ("02_eda/02_baseline.py", "Baseline-EDA"),
    ("03_analysis/03_mtld_analysis.py", "MTLD-Analyse"),
    ("03_analysis/03_shannon.py", "Entropie-Analyse"),
    ("03_analysis/03_ptd_syntax.py", "Syntax-Analyse (PTD)"),
    ("03_analysis/03_fwr_ratio.py", "FWR-Analyse (untagged)"),
    ("03_analysis/03_fwr_ratio_tagged.py", "FWR-Analyse (tagged)"),
    ("03_analysis/03_mannwhitney.py", "Syntax-Signifikanz (MWU)"),
    ("04_visualization/04_sign_all.py", "Globale Signifikanztests"),
    ("04_visualization/04_visualization.py", "Visualisierungen"),
]

def create_final_snapshot():
    """
    Kopiert den gesamten final/-Ordner in einen neuen Snapshot-Ordner
    mit Timestamp unter data/final_snapshots/.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    snapshot_root = DATA / "final_snapshots"
    snapshot_root.mkdir(exist_ok=True)

    target = snapshot_root / timestamp
    shutil.copytree(FINAL, target)

    print(f"\nSnapshot erstellt unter: {target}")

def run_step(script, label):
    print(f"\n=== {label} ===")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent)
    subprocess.run([sys.executable, script], check=True, env=env)

def run_pipeline():
    for script, label in STEPS:
        run_step(script, label)
    print("\n=== PIPELINE ERFOLGREICH ABGESCHLOSSEN ===")

    print("\nErstelle Snapshot…")
    create_final_snapshot()

if __name__ == "__main__":
    run_pipeline()
