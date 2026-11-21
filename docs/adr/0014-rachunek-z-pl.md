# ADR-0014: Numer rachunku jak w dokumencie, z „PL”

Status: przyjęte, 2026-11-21

## Kontekst

Wzorce treningowe mają rachunek bez „PL” (26 cyfr), wzorce skanów z „PL”. UZP na Discordzie (21.11): numer ma być taki, jak w dokumencie; brak „PL” we wzorcach to błąd, którego nie będzie w zbiorze testowym. W 48 z 60 przelewów treningowych przed numerem stoi „PL”.

## Decyzja

1. `RACHUNEK` w `config/ustawienia.yaml` łapie też „PL” przed numerem; nowy format `bez_spacji` usuwa tylko odstępy: `PL 62 2170 …` -> `PL62217000089152501756617062`.
2. Bez „PL” w dokumencie: same 26 cyfr, jak dotąd.
3. `tools/ocena_f1.py`, `tools/warianty.py` i T3 porównują pola z `bez_prefiksu` bez „PL” po obu stronach, bo wzorce treningowe są tu błędne. Nowy T11 sprawdza „PL” w wyniku.

## Konsekwencje

- F1 treningowe bez zmian (0.9990); na zbiorze testowym zyskujemy do dwóch pól na przelew z „PL”.
- Jeśli UZP poprawi wzorce w repozytorium, `bez_prefiksu` można usunąć.
