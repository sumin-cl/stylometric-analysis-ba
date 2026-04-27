@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
set PYTHONPATH=%~dp0src
for /f "tokens=1,2 delims==" %%a in (.env) do set %%a=%%b

REM ========================================
REM   HAUPTMENUE
REM ========================================

:menu
cls
echo ========================================
echo   STYLOMETRIC ANALYSIS - LAUNCHER
echo ========================================
echo.
echo  Konsole statt .bat:
echo    CMD:        set PYTHONPATH=^<projektpfad^>\src
echo    PowerShell: $env:PYTHONPATH="^<projektpfad^>\src"
echo.
echo  [R]  Reddit Pipeline
echo  [S]  Synthetic Pipeline
echo  [A]  Analysis
echo.
echo  [Q]  Beenden
echo.
set /p choice="Auswahl: "

if /i "%choice%"=="R" goto reddit_menu
if /i "%choice%"=="S" goto synthetic_menu
if /i "%choice%"=="A" goto analysis_menu
if /i "%choice%"=="Q" exit /b

echo Ungueltige Eingabe.
goto menu


REM ========================================
REM   REDDIT PIPELINE
REM ========================================

:reddit_menu
cls
echo ========================================
echo   REDDIT PIPELINE
echo ========================================
echo.
echo  --- Extraction ---
echo  [1]  Extract pre-2022  (Kaggle)
echo  [2]  Extract post-2022 (Arctic)
echo.
echo  --- Preprocessing ---
echo  [3]  Preprocessing
echo  [4]  Downsampling
echo  [5]  POS Tagging
echo  [6]  Syntax Cache
echo.
echo  --- EDA ---
echo  [7]  EDA / Baseline
echo.
echo  [B]  Zurueck
echo.
set /p choice="Auswahl: "

if "%choice%"=="1" python src\00_extraction\00_extract_a_kaggle.py          & goto done_reddit
if "%choice%"=="2" python src\00_extraction\00_extract_b_arctic.py          & goto done_reddit
if "%choice%"=="3" python src\01_preprocessing\01_preprocess.py             & goto done_reddit
if "%choice%"=="4" python src\01_preprocessing\01b_downsampling.py          & goto done_reddit
if "%choice%"=="5" goto pos_menu
if "%choice%"=="6" goto parse_menu
if "%choice%"=="7" python src\02_eda\02_baseline.py                         & goto done_reddit
if /i "%choice%"=="B" goto menu

echo Ungueltige Eingabe.
goto reddit_menu

:pos_menu
cls
echo  POS Tagging --- Sample auswaehlen:
echo  [0] Full Corpus   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\01_preprocessing\01b_pos_tagger.py full            & goto done_reddit
if "%sample%"=="1"      python src\01_preprocessing\01b_pos_tagger.py downsampled 1   & goto done_reddit
if "%sample%"=="2"      python src\01_preprocessing\01b_pos_tagger.py downsampled 2   & goto done_reddit
if "%sample%"=="3"      python src\01_preprocessing\01b_pos_tagger.py downsampled 3   & goto done_reddit
if /i "%sample%"=="all" (
    python src\01_preprocessing\01b_pos_tagger.py downsampled 1
    python src\01_preprocessing\01b_pos_tagger.py downsampled 2
    python src\01_preprocessing\01b_pos_tagger.py downsampled 3
    goto done_reddit
)
echo Ungueltige Eingabe. & goto pos_menu

:parse_menu
cls
echo  Syntax Cache --- Sample auswaehlen:
echo  [0] Full Corpus   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\01_preprocessing\01_parse_and_cache.py full            & goto done_reddit
if "%sample%"=="1"      python src\01_preprocessing\01_parse_and_cache.py downsampled 1   & goto done_reddit
if "%sample%"=="2"      python src\01_preprocessing\01_parse_and_cache.py downsampled 2   & goto done_reddit
if "%sample%"=="3"      python src\01_preprocessing\01_parse_and_cache.py downsampled 3   & goto done_reddit
if /i "%sample%"=="all" (
    python src\01_preprocessing\01_parse_and_cache.py downsampled 1
    python src\01_preprocessing\01_parse_and_cache.py downsampled 2
    python src\01_preprocessing\01_parse_and_cache.py downsampled 3
    goto done_reddit
)
echo Ungueltige Eingabe. & goto parse_menu

:done_reddit
echo.
pause
goto reddit_menu


REM ========================================
REM   SYNTHETIC PIPELINE
REM ========================================

:synthetic_menu
cls
echo ========================================
echo   SYNTHETIC PIPELINE
echo ========================================
echo.
echo  [1]  Topic Extraction
echo  [2]  Topic Validation (HTML Report)
echo  [3]  Prompts generieren  (Style B)
echo  [4]  LLM Korpus generieren
echo  [5]  Preprocessing LLM-Output
echo.
echo  Hinweis: OpenAI API Key erforderlich fuer [4].
echo    CMD:        set OPENAI_API_KEY=dein-key
echo    PowerShell: $env:OPENAI_API_KEY="dein-key"
echo.
echo  [B]  Zurueck
echo.
set /p choice="Auswahl: "

if "%choice%"=="1" goto topic_menu
if "%choice%"=="2" goto validation_menu
if "%choice%"=="3" goto prompt_gen
if "%choice%"=="4" goto llm_gen
if "%choice%"=="5" python src\01_preprocessing\01_preprocess.py llm         & goto done_synthetic
if /i "%choice%"=="B" goto menu

echo Ungueltige Eingabe.
goto synthetic_menu

:topic_menu
cls
echo  Topic Extraction --- Sample auswaehlen:
echo  [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="1"      python src\02_generation\02_topic_extraction.py downsampled 1   & goto done_synthetic
if "%sample%"=="2"      python src\02_generation\02_topic_extraction.py downsampled 2   & goto done_synthetic
if "%sample%"=="3"      python src\02_generation\02_topic_extraction.py downsampled 3   & goto done_synthetic
if /i "%sample%"=="all" (
    python src\02_generation\02_topic_extraction.py downsampled 1
    python src\02_generation\02_topic_extraction.py downsampled 2
    python src\02_generation\02_topic_extraction.py downsampled 3
    goto done_synthetic
)
echo Ungueltige Eingabe. & goto topic_menu

:validation_menu
cls
echo  Topic Validation
echo  [1]  Auto   (alle Topic-Dateien)
echo  [2]  Manuell (Dateinamen eingeben)
echo  [3]  Batch Analysis (HTML + Plots)
echo.
set /p vchoice="Auswahl: "
if "%vchoice%"=="1" (
    setlocal enabledelayedexpansion
    set files=
    for %%f in (data\final\02_generation\*_topics.csv) do (
        set files=!files! %%f
    )
    python src\02_generation\topic_validation_html.py !files!
    endlocal
    goto done_synthetic
)
if "%vchoice%"=="2" (
    set /p files="Dateinamen (Leerzeichen-getrennt): "
    python src\02_generation\topic_validation_html.py %files%
    goto done_synthetic
)
if "%vchoice%"=="3" python src\02_generation\topic_batch_analysis.py        & goto done_synthetic
echo Ungueltige Eingabe. & goto validation_menu

:prompt_gen
cls
set /p count="Wie viele Prompts generieren? (empfohlen: 550): "
python src\02_generation\02b_prompt_template_generator.py B %count%
goto done_synthetic

:llm_gen
cls
set /p count="Prompt-Anzahl der Datei (z.B. 550): "
set PROMPT_PATH=%~dp0data\final\02_generation\prompts\prompts_style_B_%count%.jsonl
if not exist "%PROMPT_PATH%" (
    echo.
    echo [FEHLER] Datei nicht gefunden:
    echo   %PROMPT_PATH%
    echo Bitte zuerst Prompts generieren ^(Option 3^).
    pause
    goto synthetic_menu
)
echo Starte Generierung mit: %PROMPT_PATH%
echo.
python src\02_generation\02d_generation_api.py "%PROMPT_PATH%"
goto done_synthetic

:done_synthetic
echo.
pause
goto synthetic_menu


REM ========================================
REM   ANALYSIS
REM ========================================

:analysis_menu
cls
echo ========================================
echo   ANALYSIS
echo ========================================
echo.
echo  [1]  MTLD
echo  [2]  Shannon Entropy
echo  [3]  PTD  (Syntax)
echo  [4]  FWR  (untagged)
echo  [5]  FWR  (tagged)
echo  [6]  Mann-Whitney  (Syntax-Signifikanz)
echo  [7]  Globale Signifikanztests
echo  [8]  Visualisierungen
echo.
echo  [B]  Zurueck
echo.
set /p choice="Auswahl: "

if "%choice%"=="1" goto mtld_menu
if "%choice%"=="2" goto shannon_menu
if "%choice%"=="3" goto ptd_menu
if "%choice%"=="4" goto fwr_menu
if "%choice%"=="5" goto fwr_tagged_menu
if "%choice%"=="6" python src\03_analysis\03_mannwhitney.py                 & goto done_analysis
if "%choice%"=="7" python src\04_visualization\04_sign_all.py               & goto done_analysis
if "%choice%"=="8" python src\04_visualization\04_visualization.py          & goto done_analysis
if /i "%choice%"=="B" goto menu

echo Ungueltige Eingabe.
goto analysis_menu

:mtld_menu
cls
echo  MTLD --- Sample auswaehlen:
echo  [0] Full Corpus   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_mtld_analysis.py full            & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_mtld_analysis.py downsampled 1   & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_mtld_analysis.py downsampled 2   & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_mtld_analysis.py downsampled 3   & goto done_analysis
if /i "%sample%"=="all" (
    python src\03_analysis\03_mtld_analysis.py downsampled 1
    python src\03_analysis\03_mtld_analysis.py downsampled 2
    python src\03_analysis\03_mtld_analysis.py downsampled 3
    goto done_analysis
)
echo Ungueltige Eingabe. & goto mtld_menu

:shannon_menu
cls
echo  Shannon Entropy --- Sample auswaehlen:
echo  [0] Full Corpus   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_shannon.py full            & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_shannon.py downsampled 1   & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_shannon.py downsampled 2   & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_shannon.py downsampled 3   & goto done_analysis
if /i "%sample%"=="all" (
    python src\03_analysis\03_shannon.py downsampled 1
    python src\03_analysis\03_shannon.py downsampled 2
    python src\03_analysis\03_shannon.py downsampled 3
    goto done_analysis
)
echo Ungueltige Eingabe. & goto shannon_menu

:ptd_menu
cls
echo  PTD-Analyse --- Sample auswaehlen:
echo  [0] Full Corpus   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_ptd_syntax.py full            & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_ptd_syntax.py downsampled 1   & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_ptd_syntax.py downsampled 2   & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_ptd_syntax.py downsampled 3   & goto done_analysis
if /i "%sample%"=="all" (
    python src\03_analysis\03_ptd_syntax.py downsampled 1
    python src\03_analysis\03_ptd_syntax.py downsampled 2
    python src\03_analysis\03_ptd_syntax.py downsampled 3
    goto done_analysis
)
echo Ungueltige Eingabe. & goto ptd_menu

:fwr_menu
cls
echo  FWR-Analyse (untagged) --- Sample auswaehlen:
echo  [0] Full Corpus   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_fwr_ratio.py full            & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_fwr_ratio.py downsampled 1   & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_fwr_ratio.py downsampled 2   & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_fwr_ratio.py downsampled 3   & goto done_analysis
if /i "%sample%"=="all" (
    python src\03_analysis\03_fwr_ratio.py downsampled 1
    python src\03_analysis\03_fwr_ratio.py downsampled 2
    python src\03_analysis\03_fwr_ratio.py downsampled 3
    goto done_analysis
)
echo Ungueltige Eingabe. & goto fwr_menu

:fwr_tagged_menu
cls
echo  FWR-Analyse (tagged) --- Sample auswaehlen:
echo  [0] Full Corpus   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_fwr_ratio_tagged.py full            & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_fwr_ratio_tagged.py downsampled 1   & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_fwr_ratio_tagged.py downsampled 2   & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_fwr_ratio_tagged.py downsampled 3   & goto done_analysis
if /i "%sample%"=="all" (
    python src\03_analysis\03_fwr_ratio_tagged.py downsampled 1
    python src\03_analysis\03_fwr_ratio_tagged.py downsampled 2
    python src\03_analysis\03_fwr_ratio_tagged.py downsampled 3
    goto done_analysis
)
echo Ungueltige Eingabe. & goto fwr_tagged_menu

:done_analysis
echo.
pause
goto analysis_menu