# Stan

Aktualizacja: 2026-11-21, Argon.

## Zrobione
- Repozytorium (prywatne): https://github.com/Andrii2203/odwolania2json. Python 3.13.
- `AGENTS.md` (+ `CLAUDE.md`, `GEMINI.md`), ADR-0001..0007, `docs/testy.md`.
- Walking skeleton: CLI `input/ -> output/`, klasyfikacja z YAML, `process()` wspolna dla CLI i GUI. Testy T1, T2 zielone.
- Kompas `tools/ocena_f1.py`: typ poprawny 180/180, **F1 = 0.000** (pola jeszcze puste).
- Hooki `.agents/hooks.json` + `.agents/guard.py` (`PreToolUse` i `Stop`): blokada `search_web` (wymuszenie czytania pelnych stron zrodlowych), blokada czesciowego czytania samych naglowkow w `read_file`, blokada zapisu cyrylicy do plikow repozytorium (wszystko na GitHub wylacznie po polsku), kontrola TDD (`docs/testy.md` przed `tests/`) oraz automatyczny `pytest` przy `Stop`.
- Badanie LLM w UE (`docs/badania/llm-ue.md`) na podstawie pelnych oficjalnych katalogow i kart modeli:
  - Porownano Mistral AI, Scaleway, OVHcloud, IONOS.
  - Zweryfikowano licencje lokalnych modeli na Hugging Face: **`Qwen/Qwen3.5-4B`** ma licencje **Apache 2.0**, a **`google/gemma-4-E4B-it`** rowniez ma licencje **Apache 2.0**. Zaden z 4 dostawcow nie hostuje wariantu 4B/E4B w serverless API, ale OVHcloud i IONOS hostuja bezposrednio **`Qwen3.5-9B`** (Apache 2.0, $0.11-$0.12 / $0.17-$0.18), a OVHcloud hostuje **`gemma-4-26b-a4b`** (Apache 2.0, $0.10 / $0.41) oraz **`Mistral-Small-3.2-24B-Instruct-2506`** (Apache 2.0, $0.10 / $0.31). W samym Mistral AI modele Small 3.1/3.2 sa juz wycofane, a aktywnym modelem Apache 2.0 jest **`Mistral Small 4` (`mistral-small-2603`)** ($0.15 / $0.60) oraz **`Ministral 3 8B` (`ministral-8b-2512`)** ($0.15 / $0.15).
- Badanie OCR na CPU (`docs/badania/ocr.md`) na podstawie pelnych metadanych PyPI JSON API oraz `default_models.yaml` z GitHub:
  - `pypdfium2 5.15.2` (BSD-3-Clause / Apache-2.0, wheel 3,99 MB) + `rapidocr 3.10.0` (Apache-2.0, wheel 26,02 MB) + `onnxruntime 1.32.0` (MIT, wheel 15,92 MB). Wsparcie dla polskiego w PP-OCRv5 (`latin_PP-OCRv5_rec_mobile`) oraz w PP-OCRv6 (`multi_PP-OCRv6_rec_small`, jawny kod `pl` na liscie `ppocrv6_langs`).
- Badanie limitów wydatków, monitoringu zużycia i unieważniania kluczy w OVHcloud (`docs/badania/ovh-limity.md`) na podstawie oficjalnej dokumentacji `help.ovhcloud.com` i repozytorium `ovh/docs`:
  - Brak twardego limitu blokującego API (hard cap); zabezpieczenia: alert progowy e-mail w `Public Cloud -> Settings -> Billing -> Current usage -> Estimation of my next invoice`, data wygaśnięcia klucza (`Expiration`) przy tworzeniu w `AI -> AI Endpoints -> API keys` oraz sztywny limit 400 RPM na projekt i model.
  - Podgląd kredytu startowego 200 USD i jego ważności w `Settings -> Credit & Vouchers`, bieżącego zużycia tokenów w `AI -> AI Endpoints -> Metrics`, a zbiorczego zużycia w `Settings -> Billing -> Current usage`.
  - Natychmiastowe unieważnienie klucza: `AI -> AI Endpoints -> API keys -> Delete` (zwraca `403 Forbidden`); po ocenie jury możliwość usunięcia projektu (`Settings -> Project settings -> Delete project`) i odpięcia karty (`My payment methods -> Delete this payment method`).
- GUI wg ADR-0006 (`odwolania2json/gui.py`, `gui.bat`, `requirements-gui.txt`): Streamlit + `pypdfium2`, podgląd stron PDF po lewej i wyniku `process()` (`st.json` lub „Nieznany typ dokumentu”) po prawej.

## Plan
| Kiedy | Kto | Co |
|---|---|---|
| sb do 20:00 | Uzytkownik | Szkic zgloszenia w HackTribe (link do repozytorium wyzej) |
| sb wieczor | Claude | Ekstrakcja pol regulami: `przelew` -> `pelnomocnictwo` -> `odwolanie` |
| sb wieczor | [Argon] | ~~Badanie LLM w UE -> `docs/badania/llm-ue.md`~~ (gotowe) |
| sb wieczor | [Argon] | ~~Badanie OCR -> `docs/badania/ocr.md`~~ (gotowe) |
| sb teraz | [Argon] | ~~Limity wydatków OVH -> `docs/badania/ovh-limity.md`~~ (gotowe) |
| sb teraz | [Argon] | ~~GUI wg ADR-0006~~ (gotowe) |
| sb noc | Claude | LLM dla pol, ktorych nie biora reguly (ADR-0004); OCR (ADR-0007) |
| nd 7:00-9:30 | [Argon] | Prezentacja PDF <= 10 MB wg ADR-0006; `README.md` po polsku |
| nd 9:30-10:30 | Claude + Uzytkownik | Finalny pomiar F1, sprawdzenie `start.bat` na czystym katalogu, oddanie |
| nd 11:00 | — | Deadline |

### [Argon] Limity wydatków OVH
Użytkownik podpiął kartę i nie chce żadnych opłat z karty. Sprawdź w oficjalnej dokumentacji OVHcloud:
1. Czy da się ustawić twardy limit wydatków albo alert dla projektu Public Cloud i AI Endpoints. Kroki w panelu.
2. Gdzie widać zużycie i pozostały kredyt startowy.
3. Jak unieważnić klucz API po hackathonie.

Z linkami do źródeł. Wynik: `docs/badania/ovh-limity.md`.

### [Argon] GUI (ADR-0006)
- Pliki: `odwolania2json/gui.py`, `gui.bat`, `requirements-gui.txt`. Innych plików nie zmieniaj.
- `gui.bat`: jak `start.bat` (tworzy `.venv`, jeśli nie ma), instaluje `requirements.txt` i `requirements-gui.txt`, uruchamia `streamlit run odwolania2json/gui.py`.
- Ekran: wgranie jednego lub kilku PDF. Po lewej strony PDF jako obrazy (`pypdfium2`), po prawej typ dokumentu i JSON (`st.json`). Dla obcego dokumentu komunikat „Nieznany typ dokumentu”.
- Logika tylko przez `load_types()` i `process()` z `odwolania2json/pipeline.py`. Bez własnej ekstrakcji.
- Teksty w GUI po polsku, w kodzie bez komentarzy.
- Commit: `git add` wskazanych plików, `git commit -m "krótki opis po polsku"`, `git push`. Hook pre-commit sprawdzi testy i język.

## Otwarte pytania
- Jak UZP liczy F1 — nie blokuje pracy (ADR-0005).
- Lokalne przebiegi: `E:\call to ai\tools\llama.cpp\llama-server.exe` + `models\brain\Qwen3.5-4B-Q8_0.gguf` na RTX 5060 (ADR-0004).
