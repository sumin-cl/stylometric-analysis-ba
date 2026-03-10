@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
set PYTHONPATH=%~dp0src

:menu
cls
echo ========================================
echo   STYLOMETRIC ANALYSIS - LAUNCHER
echo ========================================
echo.
echo  [0]  Komplette Pipeline starten
echo.
echo  --- Extraction ---
echo  [1]  Korpus A extrahieren (Kaggle)
echo  [2]  Korpus B extrahieren (Arctic)
echo.
echo  --- Preprocessing ---
echo  [3]  Preprocessing
echo  [4]  POS-Tagging
echo  [5]  Syntax-Parsing cachen
echo.
echo  --- EDA ---
echo  [6]  Baseline-Analyse
echo.
echo  --- Analysis ---
echo  [7]  MTLD-Analyse
echo  [8]  Entropie-Analyse
echo  [9]  Syntax-Analyse (PTD)
echo  [10] FWR-Analyse (untagged)
echo  [11] FWR-Analyse (tagged)
echo  [12] Syntax-Signifikanz (MWU)
echo.
echo  --- Output ---
echo  [13] Globale Signifikanztests
echo  [14] Visualisierungen
echo.
echo  [q]  Beenden
echo.
set /p choice="Auswahl: "

if "%choice%"=="0"  python src\run_pipeline.py                          & goto done
if "%choice%"=="1"  python src\00_extraction\00_extract_a_kaggle.py    & goto done
if "%choice%"=="2"  python src\00_extraction\00_extract_b_arctic.py    & goto done
if "%choice%"=="3"  python src\01_preprocessing\01_preprocess.py       & goto done
if "%choice%"=="4"  python src\01_preprocessing\01b_pos_tagger.py      & goto done
if "%choice%"=="5"  python src\01_preprocessing\01_parse_and_cache.py  & goto done
if "%choice%"=="6"  python src\02_eda\02_baseline.py                   & goto done
if "%choice%"=="7"  python src\03_analysis\03_mtld_analysis.py         & goto done
if "%choice%"=="8"  python src\03_analysis\03_shannon.py               & goto done
if "%choice%"=="9"  python src\03_analysis\03_ptd_syntax.py            & goto done
if "%choice%"=="10" python src\03_analysis\03_fwr_ratio.py             & goto done
if "%choice%"=="11" python src\03_analysis\03_fwr_ratio_tagged.py      & goto done
if "%choice%"=="12" python src\03_analysis\03_mannwhitney.py           & goto done
if "%choice%"=="13" python src\04_visualization\04_sign_all.py         & goto done
if "%choice%"=="14" python src\04_visualization\04_visualization.py    & goto done
if /i "%choice%"=="q" exit /b

echo Ungueltige Eingabe.
goto menu

:done
echo.
pause
goto menu
