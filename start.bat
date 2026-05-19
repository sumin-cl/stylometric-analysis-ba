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
echo  [R]  Reddit Pipeline      (Corpus A + B)
echo  [S]  Synthetic Pipeline   (Corpus C, LLM)
echo  [A]  Analysis             (MTLD/Shannon/FWR/PTD + LLM-Vergleich)
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
REM   REDDIT PIPELINE  (Corpus A + B)
REM ========================================

:reddit_menu
cls
echo ========================================
echo   REDDIT PIPELINE  (Corpus A + B)
echo ========================================
echo.
echo  --- Extraction ---
echo  [1]  Extract pre-2022   (Kaggle)
echo  [2]  Extract post-2022  (Arctic)
echo.
echo  --- Preprocessing ---
echo  [3]  Preprocessing      (raw -^> cleaned, full)
echo  [4]  Filter             (cleaned -^> filtered, Default 100-400 Tokens)
echo  [5]  Sampling           (filtered -^> 3x n=500, Seeds 42/43/44)
echo  [6]  POS Tagging
echo  [7]  Syntax Cache       (Parse Tree Depths)
echo.
echo  --- EDA ---
echo  [8]  Baseline
echo  [9]  Laengenverteilung  (Histogramm)
echo.
echo  [B]  Zurueck
echo.
set /p choice="Auswahl: "

if "%choice%"=="1" python src\00_extraction\00_extract_a_kaggle.py          & goto done_reddit
if "%choice%"=="2" python src\00_extraction\00_extract_b_arctic.py          & goto done_reddit
if "%choice%"=="3" python src\01_preprocessing\01_preprocess.py             & goto done_reddit
if "%choice%"=="4" goto filter_menu
if "%choice%"=="5" python src\01_preprocessing\01c_sampling.py              & goto done_reddit
if "%choice%"=="6" goto pos_menu
if "%choice%"=="7" goto parse_menu
if "%choice%"=="8" python src\02_eda\02_baseline.py                         & goto done_reddit
if "%choice%"=="9" python src\02_eda\02_eda_length.py                       & goto done_reddit
if /i "%choice%"=="B" goto menu

echo Ungueltige Eingabe.
goto reddit_menu

:filter_menu
cls
echo  Filter --- Token-Fenster:
echo  [d] Default (100-400)   [c] Custom (eingeben)
echo.
set /p fchoice="Auswahl: "
if /i "%fchoice%"=="d" python src\01_preprocessing\01b_filter.py            & goto done_reddit
if /i "%fchoice%"=="c" (
    set /p minTok="min Tokens: "
    set /p maxTok="max Tokens: "
    python src\01_preprocessing\01b_filter.py %minTok% %maxTok%
    goto done_reddit
)
echo Ungueltige Eingabe. & goto filter_menu

:pos_menu
cls
echo  POS Tagging --- Quelle auswaehlen:
echo  [0] Full Corpus (teuer)   [F] Filtered   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle Samples
echo.
set /p sample="Auswahl: "
if "%sample%"=="0"      python src\01_preprocessing\01b_pos_tagger.py full              & goto done_reddit
if /i "%sample%"=="F"   python src\01_preprocessing\01b_pos_tagger.py filtered          & goto done_reddit
if "%sample%"=="1"      python src\01_preprocessing\01b_pos_tagger.py downsampled 1     & goto done_reddit
if "%sample%"=="2"      python src\01_preprocessing\01b_pos_tagger.py downsampled 2     & goto done_reddit
if "%sample%"=="3"      python src\01_preprocessing\01b_pos_tagger.py downsampled 3     & goto done_reddit
if /i "%sample%"=="all" (
    python src\01_preprocessing\01b_pos_tagger.py downsampled 1
    python src\01_preprocessing\01b_pos_tagger.py downsampled 2
    python src\01_preprocessing\01b_pos_tagger.py downsampled 3
    goto done_reddit
)
echo Ungueltige Eingabe. & goto pos_menu

:parse_menu
cls
echo  Syntax Cache --- Quelle auswaehlen:
echo  [0] Full Corpus (sehr teuer)   [F] Filtered   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle Samples
echo.
set /p sample="Auswahl: "
if "%sample%"=="0"      python src\01_preprocessing\01_parse_and_cache.py full          & goto done_reddit
if /i "%sample%"=="F"   python src\01_preprocessing\01_parse_and_cache.py filtered      & goto done_reddit
if "%sample%"=="1"      python src\01_preprocessing\01_parse_and_cache.py downsampled 1 & goto done_reddit
if "%sample%"=="2"      python src\01_preprocessing\01_parse_and_cache.py downsampled 2 & goto done_reddit
if "%sample%"=="3"      python src\01_preprocessing\01_parse_and_cache.py downsampled 3 & goto done_reddit
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
REM   SYNTHETIC PIPELINE  (Corpus C, LLM)
REM ========================================

:synthetic_menu
cls
echo ========================================
echo   SYNTHETIC PIPELINE  (Corpus C, LLM)
echo ========================================
echo.
echo  --- Generation ---
echo  [1]  Topic Extraction
echo  [2]  Topic Validation   (HTML Report / Batch Analysis)
echo  [3]  Prompts generieren (Style B)
echo  [4]  LLM Korpus generieren  (OpenAI API)
echo.
echo  --- Preprocessing  (parallel zur Reddit-Pipeline) ---
echo  [5]  Extract C  (JSONL -^> corpus_c_raw.csv)
echo  [6]  Preprocessing C  (raw -^> cleaned)
echo  [7]  Filter C  (Default 100-400 Tokens)
echo  [8]  POS Tagging C
echo  [9]  Syntax Cache C
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
if "%choice%"=="5" python src\00_extraction\00_extract_c_from_jsonl.py      & goto done_synthetic
if "%choice%"=="6" python src\01_preprocessing\01_preprocess.py llm         & goto done_synthetic
if "%choice%"=="7" python src\01_preprocessing\01b_filter.py llm            & goto done_synthetic
if "%choice%"=="8" python src\01_preprocessing\01b_pos_tagger.py llm        & goto done_synthetic
if "%choice%"=="9" python src\01_preprocessing\01_parse_and_cache.py llm    & goto done_synthetic
if /i "%choice%"=="B" goto menu

echo Ungueltige Eingabe.
goto synthetic_menu

:topic_menu
cls
echo  Topic Extraction --- Sample auswaehlen:
echo  [F] Filtered (Reddit-Korpora gesamt)   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle Samples
echo.
set /p sample="Sample: "
if /i "%sample%"=="F"   python src\02_generation\02_topic_extraction.py filtered          & goto done_synthetic
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
echo  [1]  Auto    (alle Topic-Dateien)
echo  [2]  Manuell (Dateinamen eingeben)
echo  [3]  Batch Analysis (HTML + Plots)
echo.
set /p vchoice="Auswahl: "
if "%vchoice%"=="1" (
    setlocal enabledelayedexpansion
    set files=
    for %%f in (data\final\02_generation\topics\*_topics.csv) do (
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
set /p count="Wie viele Prompts generieren? (Ziel: ~1650): "
python src\02_generation\02b_prompt_template_generator.py B %count%
goto done_synthetic

:llm_gen
cls
set /p count="Prompt-Anzahl der Datei (z.B. 1650): "
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
echo  --- Reddit-Samples (A vs B) ---
echo  [1]  MTLD
echo  [2]  Shannon Entropy
echo  [3]  PTD  (Syntax)
echo  [4]  FWR  (untagged)
echo  [5]  FWR  (tagged)
echo.
echo  --- LLM (B vs C) ---
echo  [L1] MTLD            (B-Samples vs Corpus C)
echo  [L2] Shannon         (B-Samples vs Corpus C)
echo  [L3] PTD             (B-Samples vs Corpus C)
echo  [L4] FWR  (tagged)   (B-Samples vs Corpus C)
echo  [L5] FWR  (untagged) (B-Samples vs Corpus C)
echo.
echo  --- Globale Signifikanz / Visualisierung ---
echo  [7]  Globale Signifikanztests
echo  [8]  Visualisierungen
echo.
echo  Hinweis: MWU/Effektgroesse ist jetzt in jede Metrik (1-5, L1-L4) integriert.
echo.
echo  [B]  Zurueck
echo.
set /p choice="Auswahl: "

if "%choice%"=="1"  goto mtld_menu
if "%choice%"=="2"  goto shannon_menu
if "%choice%"=="3"  goto ptd_menu
if "%choice%"=="4"  goto fwr_menu
if "%choice%"=="5"  goto fwr_tagged_menu
if /i "%choice%"=="L1" python src\03_analysis\03_mtld_analysis.py    llm    & goto done_analysis
if /i "%choice%"=="L2" python src\03_analysis\03_shannon.py          llm    & goto done_analysis
if /i "%choice%"=="L3" python src\03_analysis\03_ptd_syntax.py       llm    & goto done_analysis
if /i "%choice%"=="L4" python src\03_analysis\03_fwr_ratio_tagged.py llm    & goto done_analysis
if /i "%choice%"=="L5" python src\03_analysis\03_fwr_ratio.py        llm    & goto done_analysis
if "%choice%"=="7"  goto sigreport_menu
if "%choice%"=="8"  goto viz_menu
if /i "%choice%"=="B" goto menu

echo Ungueltige Eingabe.
goto analysis_menu

:mtld_menu
cls
echo  MTLD --- Sample auswaehlen:
echo  [0] Full Corpus   [F] Filtered   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_mtld_analysis.py full              & goto done_analysis
if /i "%sample%"=="F"   python src\03_analysis\03_mtld_analysis.py filtered          & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_mtld_analysis.py downsampled 1     & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_mtld_analysis.py downsampled 2     & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_mtld_analysis.py downsampled 3     & goto done_analysis
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
echo  [0] Full Corpus   [F] Filtered   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_shannon.py full              & goto done_analysis
if /i "%sample%"=="F"   python src\03_analysis\03_shannon.py filtered          & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_shannon.py downsampled 1     & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_shannon.py downsampled 2     & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_shannon.py downsampled 3     & goto done_analysis
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
echo  [0] Full Corpus   [F] Filtered   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_ptd_syntax.py full              & goto done_analysis
if /i "%sample%"=="F"   python src\03_analysis\03_ptd_syntax.py filtered          & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_ptd_syntax.py downsampled 1     & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_ptd_syntax.py downsampled 2     & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_ptd_syntax.py downsampled 3     & goto done_analysis
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
echo  [0] Full Corpus   [F] Filtered   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_fwr_ratio.py full              & goto done_analysis
if /i "%sample%"=="F"   python src\03_analysis\03_fwr_ratio.py filtered          & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_fwr_ratio.py downsampled 1     & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_fwr_ratio.py downsampled 2     & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_fwr_ratio.py downsampled 3     & goto done_analysis
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
echo  [0] Full Corpus   [F] Filtered   [1] Sample 1   [2] Sample 2   [3] Sample 3   [all] Alle
echo.
set /p sample="Sample: "
if "%sample%"=="0"      python src\03_analysis\03_fwr_ratio_tagged.py full              & goto done_analysis
if /i "%sample%"=="F"   python src\03_analysis\03_fwr_ratio_tagged.py filtered          & goto done_analysis
if "%sample%"=="1"      python src\03_analysis\03_fwr_ratio_tagged.py downsampled 1     & goto done_analysis
if "%sample%"=="2"      python src\03_analysis\03_fwr_ratio_tagged.py downsampled 2     & goto done_analysis
if "%sample%"=="3"      python src\03_analysis\03_fwr_ratio_tagged.py downsampled 3     & goto done_analysis
if /i "%sample%"=="all" (
    python src\03_analysis\03_fwr_ratio_tagged.py downsampled 1
    python src\03_analysis\03_fwr_ratio_tagged.py downsampled 2
    python src\03_analysis\03_fwr_ratio_tagged.py downsampled 3
    goto done_analysis
)
echo Ungueltige Eingabe. & goto fwr_tagged_menu

:sigreport_menu
cls
echo  Signifikanz-Report aggregieren:
echo  [F] Full        -- mit spaCy-Lauf fuer FWR untagged, ca. 5-8 min
echo  [Q] Quick       -- ohne FWR-untagged-Levene/KS, ca. 1 min
echo.
echo  [B] Zurueck
echo.
set /p sigmode="Mode: "
if /i "%sigmode%"=="B" goto analysis_menu
if /i "%sigmode%"=="F" python src\04_visualization\04_sign_all.py            & goto done_analysis
if /i "%sigmode%"=="Q" python src\04_visualization\04_sign_all.py --quick    & goto done_analysis
echo Ungueltige Eingabe. & goto sigreport_menu

:viz_menu
cls
echo  Visualisierungen --- Plot auswaehlen:
echo  [all] Alle Plots
echo  [1]   Effect Sizes  -- ^|r_rb^| pro Metrik, A-vs-B und B-vs-C
echo  [2]   PTD           -- Violin der Baumtiefen
echo  [3]   MTLD          -- Chunks raw vs vocab-aligned
echo  [4]   Shannon       -- Per-post Entropie WORD + POS
echo  [5]   FWR           -- Means untagged + tagged
echo  [6]   Length        -- Token-Laengen nach Filter
echo.
echo  [B]   Zurueck
echo.
set /p plot="Plot: "
if /i "%plot%"=="B"   goto analysis_menu
if /i "%plot%"=="all" python src\04_visualization\04_visualization.py            & goto done_analysis
if "%plot%"=="1"      python src\04_visualization\04_visualization.py effects   & goto done_analysis
if "%plot%"=="2"      python src\04_visualization\04_visualization.py ptd       & goto done_analysis
if "%plot%"=="3"      python src\04_visualization\04_visualization.py mtld      & goto done_analysis
if "%plot%"=="4"      python src\04_visualization\04_visualization.py shannon   & goto done_analysis
if "%plot%"=="5"      python src\04_visualization\04_visualization.py fwr       & goto done_analysis
if "%plot%"=="6"      python src\04_visualization\04_visualization.py length    & goto done_analysis
echo Ungueltige Eingabe. & goto viz_menu

:done_analysis
echo.
pause
goto analysis_menu