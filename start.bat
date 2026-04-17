@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
set PYTHONPATH=%~dp0src
for /f "tokens=1,2 delims==" %%a in (.env) do set %%a=%%b

:menu
cls
echo ========================================
echo   STYLOMETRIC ANALYSIS - LAUNCHER
echo ========================================
echo.
echo  [0]  Komplette Pipeline starten (to be reimplemented)
echo.
echo  --- Extraction ---
echo  [1]  Korpus A extrahieren (Kaggle)
echo  [2]  Korpus B extrahieren (Arctic)
echo.
echo  --- Preprocessing ---
echo  [3]  Preprocessing
echo  [4,4a,b,c]  POS-Tagging
echo  [5,5a,b,c]  Syntax-Parsing cachen
echo.
echo  --- Synthetic Corpus Generation ---
echo  [6] Topic Extraction (Cleaned Full Corpus)
echo  [6a,b,c] Topic Extraction (Downsampled)
echo  [66,6aa,bb,cc] LLM-Korpus Generierung (Not implemented yet!)
echo  [6h]  Topic Validation (HTML Report, auto)
echo  [6hm] Topic Validation (HTML Report, manuell)
echo  [6bat]  Topic Batch Analysis (HTML + Plots)
echo  - Prompt Generation -
echo  [61a] Generate Prompts (Style A)
echo  [61b] Generate Prompts (Style B)
echo  [61c] Generate Prompts (Style C)
echo  - LLM Corpus Generation -
echo.
echo  --- EDA ---
echo  [6x]  Baseline-Analyse
echo.
echo  --- Analysis ---
echo  [7]  MTLD-Analyse (Full Corpus)
echo  [7a] MTLD-Analyse (Sample 1)
echo  [7b] MTLD-Analyse (Sample 2)
echo  [7c] MTLD-Analyse (Sample 3)
echo  [8,8a,b,c]  Entropie-Analyse
echo  [9,9a,b,c]  Syntax-Analyse (PTD)
echo  [10,10a,b,c] FWR-Analyse (untagged)
echo  [11,11a,b,c] FWR-Analyse (tagged)
echo  [12] Syntax-Signifikanz (MWU)
echo.
echo  --- Output ---
echo  [13] Globale Signifikanztests
echo  [14] Visualisierungen
echo.
echo  [15] Downsampling
echo.
echo  [groq] Groq-Test
echo.
echo  [q]  Beenden
echo.
set /p choice="Auswahl: "

if "%choice%"=="0"  python src\run_pipeline.py                          & goto done
if "%choice%"=="1"  python src\00_extraction\00_extract_a_kaggle.py    & goto done
if "%choice%"=="2"  python src\00_extraction\00_extract_b_arctic.py    & goto done
if "%choice%"=="3"  python src\01_preprocessing\01_preprocess.py       & goto done
if "%choice%"=="4"  python src\01_preprocessing\01b_pos_tagger.py full     & goto done
if "%choice%"=="4a"  python src\01_preprocessing\01b_pos_tagger.py downsampled 1     & goto done
if "%choice%"=="4b"  python src\01_preprocessing\01b_pos_tagger.py downsampled 2     & goto done
if "%choice%"=="4c"  python src\01_preprocessing\01b_pos_tagger.py downsampled 3     & goto done
if "%choice%"=="5"  python src\01_preprocessing\01_parse_and_cache.py full & goto done
if "%choice%"=="5a"  python src\01_preprocessing\01_parse_and_cache.py downsampled 1 & goto done
if "%choice%"=="5b"  python src\01_preprocessing\01_parse_and_cache.py downsampled 2 & goto done
if "%choice%"=="5c"  python src\01_preprocessing\01_parse_and_cache.py downsampled 3 & goto done
if "%choice%"=="6"  python src\02_generation\02_topic_extraction.py full                  & goto done
if "%choice%"=="6a"  python src\02_generation\02_topic_extraction.py downsampled 1                  & goto done
if "%choice%"=="6b"  python src\02_generation\02_topic_extraction.py downsampled 2                  & goto done
if "%choice%"=="6c"  python src\02_generation\02_topic_extraction.py downsampled 3                  & goto done
if "%choice%"=="6v" (
    set /p fname="Dateiname im GENERATED-Ordner: "
    python src\02_generation\topic_validation.py %fname%
    goto done
)
if "%choice%"=="6h" (
    echo Sammle Topic-Dateien...
    setlocal enabledelayedexpansion

    set files=
    for %%f in (data\final\02_generation\*.csv) do (
        echo %%f | findstr /i "_topics.csv" >nul
        if not errorlevel 1 (
            set files=!files! %%f
        )
    )

    if "%files%"=="" (
        echo Keine Topic-Dateien gefunden.
        goto done
    )

    echo Erzeuge HTML-Report...
    python src\02_generation\topic_validation_html.py %files%
    endlocal
    goto done
)
if "%choice%"=="6hm" (
    set /p files="Dateinamen (mit Leerzeichen getrennt): "
    python src\02_generation\topic_validation_html.py %files%
    goto done
)
if "%choice%"=="6bat" (
    echo Starte Topic Batch Analysis...
    python src\02_generation\topic_batch_analysis.py
    goto done
)
if "%choice%"=="61a" (
    set /p count="Wie viele Prompts generieren? "
    python src\02_generation\02b_prompt_template_generator.py A %count%
    goto done
)

if "%choice%"=="61b" (
    set /p count="Wie viele Prompts generieren? "
    python src\02_generation\02b_prompt_template_generator.py B %count%
    goto done
)

if "%choice%"=="61c" (
    set /p count="Wie viele Prompts generieren? "
    python src\02_generation\02b_prompt_template_generator.py C %count%
    goto done
)
if "%choice%"=="66"  python src\02_generation\02_topic_extraction.py downsampled 1                  & goto done
if "%choice%"=="6aa"  python src\02_generation\02_topic_extraction.py downsampled 1                  & goto done
if "%choice%"=="6bb"  python src\02_generation\02_topic_extraction.py downsampled 2                  & goto done
if "%choice%"=="6cc"  python src\02_generation\02_topic_extraction.py downsampled 3                  & goto done
if "%choice%"=="6x"  python src\02_eda\02_baseline.py                   & goto done
if "%choice%"=="7"  python src\03_analysis\03_mtld_analysis.py full        & goto done
if "%choice%"=="7a" python src\03_analysis\03_mtld_analysis.py downsampled 1 & goto done
if "%choice%"=="7b" python src\03_analysis\03_mtld_analysis.py downsampled 2 & goto done
if "%choice%"=="7c" python src\03_analysis\03_mtld_analysis.py downsampled 3 & goto done
if "%choice%"=="8"  python src\03_analysis\03_shannon.py full              & goto done
if "%choice%"=="8a"  python src\03_analysis\03_shannon.py downsampled 1              & goto done
if "%choice%"=="8b"  python src\03_analysis\03_shannon.py downsampled 2              & goto done
if "%choice%"=="8c"  python src\03_analysis\03_shannon.py downsampled 3              & goto done
if "%choice%"=="9"  python src\03_analysis\03_ptd_syntax.py full           & goto done
if "%choice%"=="9a"  python src\03_analysis\03_ptd_syntax.py downsampled 1           & goto done
if "%choice%"=="9b"  python src\03_analysis\03_ptd_syntax.py downsampled 2           & goto done
if "%choice%"=="9c"  python src\03_analysis\03_ptd_syntax.py downsampled 3           & goto done
if "%choice%"=="10" python src\03_analysis\03_fwr_ratio.py full            & goto done
if "%choice%"=="10a" python src\03_analysis\03_fwr_ratio.py downsampled 1            & goto done
if "%choice%"=="10b" python src\03_analysis\03_fwr_ratio.py downsampled 2             & goto done
if "%choice%"=="10c" python src\03_analysis\03_fwr_ratio.py downsampled 3             & goto done
if "%choice%"=="11" python src\03_analysis\03_fwr_ratio_tagged.py full     & goto done
if "%choice%"=="11a" python src\03_analysis\03_fwr_ratio_tagged.py downsampled 1     & goto done
if "%choice%"=="11b" python src\03_analysis\03_fwr_ratio_tagged.py downsampled 2     & goto done
if "%choice%"=="11c" python src\03_analysis\03_fwr_ratio_tagged.py downsampled 3     & goto done
if "%choice%"=="12" python src\03_analysis\03_mannwhitney.py           & goto done
if "%choice%"=="13" python src\04_visualization\04_sign_all.py         & goto done
if "%choice%"=="14" python src\04_visualization\04_visualization.py    & goto done
if "%choice%"=="15" python src\01_preprocessing\01b_downsampling.py    & goto done
if "%choice%"=="groq" python test_groq.py    & goto done
if /i "%choice%"=="q" exit /b

echo Ungueltige Eingabe.
goto menu

:done
echo.
pause
goto menu
