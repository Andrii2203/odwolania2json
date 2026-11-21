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

- Dane: `data/uzp/dane/*`. Uruchamiamy prawdziwe CLI, tak jak jury.
- Sprawdza: CLI, drzewo katalogów, nazwy plików, klasyfikację każdego dokumentu, kształt JSON.
- Trudny przykład: pełnomocnictwo bez słowa „mocodawca”, ale z „udzielam pełnomocnictwa”, też ma dać `pelnomocnictwo`.
- Test: `tests/test_e2e.py::test_t1_sprawa_trzy_dokumenty`

## T2. Obcy dokument nie daje pliku

```
input/case1/negatywny przyklad.pdf (ogłoszenie TED) -> w output/ nie ma żadnego JSON
```

- Dane: `data/uzp/szablon-aplikacja/input/case1/negatywny przyklad.pdf` (tak jest w szablonie UZP: nie ma dla niego wyjściowego JSON).
- Test: `tests/test_e2e.py::test_t2_obcy_dokument`

## Pomiar jakości (to nie jest test)

`tools/ocena_f1.py` przepuszcza wszystkie 60 spraw treningowych przez CLI i liczy F1 według ADR-0003. Przykładowy wynik:

```
Dokumenty: 180 | typ poprawny: 180/180
F1 = 0.412  (TP 900 | FP 120 | FN 2450)
Najgorsze pola (FN+FP):
  odwolanie   Odwolujacy[].nip   FN 58  FP 0
```

To kompas: każda zmiana ekstrakcji powinna podnosić F1.
