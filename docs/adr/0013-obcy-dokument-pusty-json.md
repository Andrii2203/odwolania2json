# ADR-0013: Obcy, pusty i uszkodzony dokument daje plik z `{}`

Status: przyjęte, 2026-11-21; zmienia ADR-0002 w części „obcy dokument nie daje pliku”

## Kontekst

UZP na Discordzie (21.11 wieczorem): dla dokumentu spoza klas oczekiwany jest plik JSON z samym `{}`, nazwa jak PDF. O pustym i uszkodzonym PDF UZP nic nie mówi.

## Decyzja

1. Każdy PDF z `input/` ma swój plik w `output/`.
2. Nieznany typ: `{}`.
3. Błąd przetwarzania (uszkodzony PDF, wyjątek w regule): `{}`, komunikat „błąd: …” na ekranie, kod wyjścia 1 jak dotąd (T7).
4. Pusty PDF (bez tekstu i obrazu) nie ma typu, więc też `{}`.

## Konsekwencje

- T1, T2, T7 sprawdzają plik `{}`.
- `tools/ocena_f1.py` bez zmian: `{}` nie ma wartości, więc nie zmienia F1.
