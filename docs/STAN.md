# Stan

Aktualizacja: 2026-11-21 wieczór, Claude (OCR, T9).

## Zrobione

- Repozytorium (prywatne): https://github.com/Andrii2203/odwolania2json. Python 3.13.
- `AGENTS.md` (+ `CLAUDE.md`, `GEMINI.md`), ADR-0001..0010, `docs/testy.md` (T1–T9).
- Potok: CLI `input/ -> output/`, klasyfikacja z YAML (`znaczniki`, `wykluczenia`), pola z YAML (`etykiety`, `wzorce`, `format`, `sekcja`, `slownik`, `podzial`), `przetworz_wszystkie()` wspólne dla CLI, GUI i `tools/ocena_f1.py`.
- Klasyfikacja: 180/180 dokumentów treningowych poprawnie, 13/13 obcych dokumentów UZP bez JSON.
- Pola `przelew` regułami: 4 błędy na ok. 360 pól.
- Pola `pelnomocnictwo` wzorcami regex i listami (ADR-0008): 1 błąd (PESEL w jednej sprawie).
- Pola `odwolanie` wzorcami, sekcjami i słownikami (ADR-0010, test T6): 0 błędów na 60 sprawach. Łączny F1 wtedy 0.9983 (wcześniej 0.5711); teraz **0.9990** (po regułach dla skanów).
- Zgłoszenie w HackTribe: szkic zapisany.
- ADR-0009 (też `tools/` i `tests/`, sekcja `narzedzia`; hooki Claude blokują przez JSON, nie kod 2): jeden mechanizm pól (`wzorce`, `etykiety` to skrót), formaty wartości w YAML. Wszystkie liczby w `config/ustawienia.yaml` z pochodzeniem (pomiar `tools/przeglad.py`); pilnuje test T5. Wynik 180 JSON bajt w bajt bez zmian.
- OCR (ADR-0007, test T9): strona z tekstem krótszym niż `MIN_ZNAKOW_STRONY` idzie przez `pypdfium2` i RapidOCR (modele w wheel, bez sieci). Skany UZP: F1 0 -> **0.8696** (30 dokumentów, 30/30 typów, 150 DPI), ok. 3,5 s na stronę. Nowe reguły (układ skanów, `warianty_liter`, `poprawki_ocr`, `sekcja` przy wzorcu, PESEL) podniosły też dane treningowe do **0.9990**.
- Odporność: błąd w jednym PDF nie zatrzymuje pozostałych (T7, CLI kończy kodem 1). Próg F1 `MIN_F1 = 0.9985` w `ustawienia.yaml` pilnuje test T8: przepuszcza jedno błędne pole, blokuje dwa (zepsuta reguła NIP daje 0.967, test czerwony).
- Porządki (wieczór 21.11): komentarze liczb bez wyników pomiaru, tylko reguła wyboru i polecenie (ADR-0009 pkt 8); ponowny pomiar `tools/przeglad.py`: wszystkie 5 liczb nadal spełnia swoją regułę. Wspólne fragmenty `NIP_Z_ETYKIETA`, `KRS_Z_ETYKIETA`, `REGON_Z_ETYKIETA`, `PESEL_Z_ETYKIETA`, `PRAWNIK`, `PUNKT_ZAMAWIAJACEGO`, `NAGLOWEK_ODWOLUJACEGO`; ścieżki `UZP`, `DANE` tylko w `tools/ocena_f1.py`; `start.bat`/`gui.bat` najpierw Python 3.13. Wynik 210 JSON bajt w bajt bez zmian.
- Straże: pre-commit (testy, język polski), hooki Claude (TDD, stop), CI na Windows (`.github/workflows/testy.yml`, ostatni przebieg zielony). Opis w `AGENTS.md`.
- Klucz OVHcloud działa (`chat/completions`, test 16 tokenów). `GET /v1/models` z kluczem zwraca 403; to cecha OVH, nie błąd klucza.
- Argon (szczegóły w `docs/badania/`):
  - `llm-ue.md`: OVHcloud, modele `Mistral-Small-3.2-24B-Instruct-2506` i `Qwen3.5-9B`.
  - `ocr.md`: `pypdfium2` + `rapidocr` (PP-OCRv5 latin).
  - `ovh-limity.md`: w OVH nie ma twardego limitu wydatków, tylko alert e-mail; dlatego limit tokenów robimy w programie.
  - GUI (ADR-0006): `odwolania2json/gui.py`, `gui.bat`, `requirements-gui.txt`.
  - Hooki Argona w `.agents/` (tylko lokalnie, poza git).

## Nowe od UZP (Discord, repozytorium, 2026-11-21)

- `data/uzp/dane/skany/`: 30 skanów (po 10 odwołań, pełnomocnictw, przelewów; obok wzorce JSON), bez warstwy tekstu. Liczy je `tools/ocena_f1.py --dane …` (polecenie w `AGENTS.md`). Najwięcej błędów: pełnomocnictwa (inne układy niż w treningowych), tytuły przelewów, punkty odwołań zasłonięte pieczęcią.
- Imiona i nazwiska w mianowniku („Mateusz Szymański”, nie „Mateusza Szymańskiego”). W danych treningowych bez problemu; w ukrytych możliwy dopełniacz po „radcy prawnego”, „adwokata”.
- LLM: tylko firma z polityką prywatności (zakres i miejsce przetwarzania), serwery w UE/EOG. Hosting prywatny zabroniony. OVHcloud spełnia (ADR-0004).
- Wzorce spraw 19, 23, 25, 44, 55 poprawione na „Odpowiedzi/wyjaśnienia do SWZ” (jak w słowniku). `przelew.pdf` zamiast `potwierdzenie_przelewu.pdf` w sprawach 01, 02.
- Dane testowe można obejrzeć na stoisku UZP: warto sprawdzić, czy układ odwołań jest taki jak w treningowych.

## Plan

| Kiedy | Kto | Co |
|---|---|---|
| sb noc | Claude | Skany: podpisujący i nazwa mocodawcy, tytuły przelewów; potem klient LLM (OVHcloud) z limitem tokenów dla pól `null` |
| nd 7:00-9:30 | [Argon] | Prezentacja PDF <= 10 MB wg ADR-0006; `README.md` po polsku |
| nd przed 11:00 | Użytkownik | Repozytorium publiczne (jury musi je otworzyć); `.env` poza git |
| nd 9:30-10:30 | Claude + Użytkownik | Finalny pomiar F1, `start.bat` na czystym katalogu, plik z kluczem dla jury, oddanie |
| nd 11:00 | — | Termin |

## Otwarte pytania

- Jak UZP liczy F1: nie blokuje pracy (ADR-0005).
- Wzorce UZP niespójne: w skanach `z_rachunku` z „PL” („PL62217…”), w treningowych bez „PL”. Trzymamy się treningowych (cyfry); w skanach to 1 pole na przelew z „PL”.
- Reguły `odwolanie` są dopasowane do 60 spraw treningowych. Jeśli ukryte sprawy mają inny układ, pomoże LLM dla pól z `null` (ADR-0004).
- Commituj test razem z kodem i konfiguracją, które go zazieleniają; inaczej CI na pośrednim commicie jest czerwone.
- CI klonuje najnowsze dane UZP, więc zmiana danych u UZP może zaczerwienić CI bez naszej zmiany (tak było przy `11a810c`: `przelew.pdf`). Wtedy: `git -C data/uzp pull`, testy lokalnie, poprawka.
