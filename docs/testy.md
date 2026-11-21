# Testy

TDD: najpierw opis tutaj (z przykładem), potem czerwony test, kod i zielony test.
Każdy test to jeden przykład. Testu bez punktu w tym pliku nie piszemy.

## T1. Test przekrojowy (walking skeleton): każda sprawa z 3 dokumentów daje 3 JSON

```
input/przyklad_01/odwolanie.pdf              -> output/przyklad_01/odwolanie.json              ma klucz "OdwolanieKIO"
input/przyklad_01/pelnomocnictwo.pdf         -> output/przyklad_01/pelnomocnictwo.json         ma klucz "mocodawca"
input/przyklad_01/potwierdzenie_przelewu.pdf -> output/przyklad_01/potwierdzenie_przelewu.json ma klucz "przelew_bankowy"
... i tak dla wszystkich 60 spraw (180 dokumentów)
```

- Dane: `data/uzp/dane/przyklad_*`. Uruchamiamy prawdziwe CLI, tak jak jury.
- Sprawdza: CLI, drzewo katalogów, nazwy plików, klasyfikację każdego dokumentu, kształt JSON.
- Trudny przykład: pełnomocnictwo bez słowa „mocodawca”, ale z „udzielam pełnomocnictwa”, też ma dać `pelnomocnictwo`.
- Test: `tests/test_e2e.py::test_t1_sprawa_trzy_dokumenty`

## T2. Obcy dokument nie daje pliku

```
input/negatywne/KIO_KIO 2617-21.pdf (wyrok KIO, podobny do odwołania)  -> brak JSON
input/negatywne/2025_S 112-383751.pdf (ogłoszenie TED)                -> brak JSON
... i tak dla wszystkich 13 obcych dokumentów
```

- Dane: `data/uzp/dane/negatywne/*.pdf` (12 plików) i `data/uzp/szablon-aplikacja/input/case1/negatywny przyklad.pdf`.
- Sprawdza: obcy dokument nie dostaje typu, więc nie daje pliku pełnego wymyślonych wartości (FP).
- Test: `tests/test_e2e.py::test_t2_obcy_dokument`

## T3. Przelew: wszystkie pola jak we wzorcu

```
przyklad_42 (etykieta w jednej linii, wartość w następnej):
  "Rachunek zleceniodawcy  PL55 9947 7458 …" -> "z_rachunku": "55994774587693681405727867"
  "Kwota  34,00 PLN"                        -> "kwota": 34.0
  "Data operacji  2026-06-30"                -> "data_operacji": "2026-06-30"
  tytuł w dwóch liniach                      -> jedna linia, jak we wzorcu
przyklad_17 (etykieta i wartość w jednej linii, kropki):
  "WARTOŚĆ ........ 200,00 zł"               -> "kwota": 200.0
  "DATA TRANSAKCJI ........ 11-10-2026"      -> "data_operacji": "2026-10-11"
```

- Dane: `data/uzp/dane/przyklad_17` i `przyklad_42`, cały JSON musi być równy wzorcowi `przelew.json`.
- Sprawdza: etykiety i formaty pól z `config/typy/przelew.yaml`.
- Test: `tests/test_pola.py::test_t3_przelew`

## Pomiar jakości (to nie jest test)

`tools/ocena_f1.py` przepuszcza wszystkie 60 spraw treningowych przez CLI i liczy F1 według ADR-0003. Przykładowy wynik:

```
Dokumenty: 180 | typ poprawny: 180/180
F1 = 0.412  (TP 900 | FP 120 | FN 2450)
Najgorsze pola (FN+FP):
  odwolanie   Odwolujacy[].nip   FN 58  FP 0
```

To kompas: każda zmiana ekstrakcji powinna podnosić F1.
