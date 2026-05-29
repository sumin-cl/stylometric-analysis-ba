# 04_parsed

Gecachte Dependency-Parse-Tree-Tiefen (spaCy, en_core_web_sm).
Pro Post wird die durchschnittliche maximale Baumtiefe aller Sätze
gespeichert. Format: JSON-Array von Floats.

## Unterordner

### `filtered/`
Syntaxtiefen der gefilterten Vollkorpora (für LLM-Vergleich).
Erzeugt von `01_parse_and_cache.py llm`.

| Datei | Beschreibung |
|---|---|
| `corpus_b_filtered_parsed_depths.json` | Post-2022 Reddit, gefiltert |
| `corpus_c_filtered_parsed_depths.json` | LLM-generiert, gefiltert |

### `samples/`
Syntaxtiefen der Samples (für Reddit A vs B Analyse).
Erzeugt von `01_parse_and_cache.py`.
Namensschema: `sample{N}_{pre/post}_n500_parsed_depths.json`

## Hinweis
Parsing ist rechenintensiv — daher werden die Tiefen gecacht
und nicht bei jeder Analyse neu berechnet.