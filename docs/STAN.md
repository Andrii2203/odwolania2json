# Stan

Aktualizacja: 2026-11-21 wieczór, Claude.

## Zrobione

- Repozytorium (prywatne): https://github.com/Andrii2203/odwolania2json. Python 3.13.
- `AGENTS.md` (+ `CLAUDE.md`, `GEMINI.md`), ADR-0001..0007, `docs/testy.md` (T1, T2, T3).
- Potok: CLI `input/ -> output/`, klasyfikacja z YAML (`znaczniki`, `wykluczenia`), wyciąganie pól z YAML (`pola`: `etykiety` i `format`), `process()` wspólne dla CLI i GUI.
- Klasyfikacja: 180/180 dokumentów treningowych poprawnie, 13/13 obcych dokumentów UZP bez JSON.
- Pola `przelew` regułami: 4 błędy na ok. 360 pól.
- Pola `pelnomocnictwo` wzorcami regex i listami (ADR-0008): 1 błąd (PESEL w jednej sprawie). Łączny **F1 = 0.571** (`odwolanie` jeszcze puste).
- Zgłoszenie w HackTribe: szkic zapisany.
- ADR-0009 (też `tools/` i `tests/`, sekcja `narzedzia`; hooki Claude blokują przez JSON, nie kod 2): jeden mechanizm pól (`wzorce`, `etykiety` to skrót), formaty wartości w YAML. Wszystkie liczby w `config/ustawienia.yaml` z pochodzeniem (pomiar `tools/przeglad.py`); pilnuje test T5. Wynik 180 JSON bajt w bajt bez zmian.
- Straże: pre-commit (testy, język polski), hooki Claude (TDD, stop), CI na Windows (`.github/workflows/testy.yml`, ostatni przebieg zielony). Opis w `AGENTS.md`.
- Klucz OVHcloud działa (`chat/completions`, test 16 tokenów). `GET /v1/models` z kluczem zwraca 403; to cecha OVH, nie błąd klucza.
- Argon (szczegóły w `docs/badania/`):
  - `llm-ue.md`: OVHcloud, modele `Mistral-Small-3.2-24B-Instruct-2506` i `Qwen3.5-9B`.
  - `ocr.md`: `pypdfium2` + `rapidocr` (PP-OCRv5 latin).
  - `ovh-limity.md`: w OVH nie ma twardego limitu wydatków, tylko alert e-mail; dlatego limit tokenów robimy w programie.
  - GUI (ADR-0006): `odwolania2json/gui.py`, `gui.bat`, `requirements-gui.txt`.
  - Hooki Argona w `.agents/` (tylko lokalnie, poza git).

## Plan

| Kiedy | Kto | Co |
|---|---|---|
| sb wieczór | Claude | Pola `odwolanie` wzorcami (ADR-0008, fragmenty `{NIP}`, `{KRS}` gotowe); słownik `data/uzp/.../czynnosc_powod_id` |
| sb noc | Claude | Klient LLM (OVHcloud) z limitem tokenów w `config/ustawienia.yaml`; wybór modelu pomiarem F1; OCR (ADR-0007) |
| nd 7:00-9:30 | [Argon] | Prezentacja PDF <= 10 MB wg ADR-0006; `README.md` po polsku |
| nd przed 11:00 | Użytkownik | Repozytorium publiczne (jury musi je otworzyć); `.env` poza git |
| nd 9:30-10:30 | Claude + Użytkownik | Finalny pomiar F1, `start.bat` na czystym katalogu, plik z kluczem dla jury, oddanie |
| nd 11:00 | — | Termin |

## Otwarte pytania

- Jak UZP liczy F1: nie blokuje pracy (ADR-0005).
- Commituj test razem z kodem i konfiguracją, które go zazieleniają; inaczej CI na pośrednim commicie jest czerwone.
