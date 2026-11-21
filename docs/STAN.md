# Stan

Aktualizacja: 2026-11-21 noc, Claude.

## Zrobione

- Repozytorium (prywatne): https://github.com/Andrii2203/odwolania2json. Python 3.13.
- `AGENTS.md` (+ `CLAUDE.md`, `GEMINI.md`), ADR-0001..0007, `docs/testy.md` (T1, T2, T3).
- Potok: CLI `input/ -> output/`, klasyfikacja z YAML (`znaczniki`, `wykluczenia`), wyciąganie pól z YAML (`pola`: `etykiety` i `format`), `przetworz()` wspólne dla CLI i GUI.
- Klasyfikacja: 180/180 dokumentów treningowych poprawnie, 13/13 obcych dokumentów UZP bez JSON.
- Pola `przelew` regułami: 4 błędy na ok. 360 pól.
- Pola `pelnomocnictwo` wzorcami regex i listami (ADR-0008): 1 błąd (PESEL w jednej sprawie).
- Pola `odwolanie` wzorcami, sekcjami i słownikami (ADR-0010, test T6): 0 błędów na 60 sprawach. Łączny **F1 = 0.9983** (TP 2027, FP 2, FN 5; wcześniej 0.5711).
- Zgłoszenie w HackTribe: szkic zapisany.
- ADR-0009 (też `tools/` i `tests/`, sekcja `narzedzia`; hooki Claude blokują przez JSON, nie kod 2): jeden mechanizm pól (`wzorce`, `etykiety` to skrót), formaty wartości w YAML. Wszystkie liczby w `config/ustawienia.yaml` z pochodzeniem (pomiar `tools/przeglad.py`); pilnuje test T5. Wynik 180 JSON bajt w bajt bez zmian.
- Odporność: błąd w jednym PDF nie zatrzymuje pozostałych (T7, CLI kończy kodem 1). Próg F1 `MIN_F1 = 0.998` w `ustawienia.yaml` pilnuje test T8 (zepsuta reguła NIP daje 0.967, test czerwony).
- Straże: pre-commit (testy, język polski), hooki Claude (TDD, stop), CI na Windows (`.github/workflows/testy.yml`, ostatni przebieg zielony). Opis w `AGENTS.md`.
- Klucz OVHcloud działa (`chat/completions`, test 16 tokenów). `GET /v1/models` z kluczem zwraca 403; to cecha OVH, nie błąd klucza.
- Argon (szczegóły w `docs/badania/`):
  - `llm-ue.md`: OVHcloud, modele `Mistral-Small-3.2-24B-Instruct-2506` i `Qwen3.5-9B`.
  - `ocr.md`: `pypdfium2` + `rapidocr` (PP-OCRv5 latin).
  - `ovh-limity.md`: w OVH nie ma twardego limitu wydatków, tylko alert e-mail; dlatego limit tokenów robimy w programie.
  - GUI (ADR-0006): `odwolania2json/gui.py`, `gui.bat`, `requirements-gui.txt`.
  - Hooki Argona w `.agents/` (tylko lokalnie, poza git).

## Nowe od UZP (Discord, repozytorium, 2026-11-21)

- `data/uzp/dane/skany/`: 30 skanów (po 10 odwołań, pełnomocnictw, przelewów; obok wzorce JSON). Żaden nie ma warstwy tekstu, więc dziś nie dają JSON. OCR (ADR-0007) jest teraz najważniejszy. Układ: `skany/<typ>/<nr>/<nr>.pdf` + `<nr>.json`; `tools/ocena_f1.py` go jeszcze nie liczy.
- Imiona i nazwiska w mianowniku („Mateusz Szymański”, nie „Mateusza Szymańskiego”). W danych treningowych bez problemu; w ukrytych możliwy dopełniacz po „radcy prawnego”, „adwokata”.
- LLM: tylko firma z polityką prywatności (zakres i miejsce przetwarzania), serwery w UE/EOG. Hosting prywatny zabroniony. OVHcloud spełnia (ADR-0004).
- Wzorce spraw 19, 23, 25, 44, 55 poprawione na „Odpowiedzi/wyjaśnienia do SWZ” (jak w słowniku). `przelew.pdf` zamiast `potwierdzenie_przelewu.pdf` w sprawach 01, 02.
- Dane testowe można obejrzeć na stoisku UZP: warto sprawdzić, czy układ odwołań jest taki jak w treningowych.

## Plan

| Kiedy | Kto | Co |
|---|---|---|
| sb noc | Claude | OCR (ADR-0007) na `skany/`, ocena F1 skanów; potem klient LLM (OVHcloud) z limitem tokenów dla pól `null` |
| nd 7:00-9:30 | [Argon] | Prezentacja PDF <= 10 MB wg ADR-0006; `README.md` po polsku |
| nd przed 11:00 | Użytkownik | Repozytorium publiczne (jury musi je otworzyć); `.env` poza git |
| nd 9:30-10:30 | Claude + Użytkownik | Finalny pomiar F1, `start.bat` na czystym katalogu, plik z kluczem dla jury, oddanie |
| nd 11:00 | — | Termin |

## Otwarte pytania

- Jak UZP liczy F1: nie blokuje pracy (ADR-0005).
- Reguły `odwolanie` są dopasowane do 60 spraw treningowych. Jeśli ukryte sprawy mają inny układ, pomoże LLM dla pól z `null` (ADR-0004).
- Commituj test razem z kodem i konfiguracją, które go zazieleniają; inaczej CI na pośrednim commicie jest czerwone.
