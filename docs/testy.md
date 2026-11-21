# Testy

TDD: najpierw opis tutaj (z przykładem), potem czerwony test, kod i zielony test.
Każdy test to jeden przykład. Testu bez punktu w tym pliku nie piszemy.

## T1. Test przekrojowy (walking skeleton): każda sprawa z 3 dokumentów daje 3 JSON

```
input/przyklad_01/odwolanie.pdf              -> output/przyklad_01/odwolanie.json              klucze jak we wzorcu odwolanie.json ("OdwolanieKIO", …)
input/przyklad_01/pelnomocnictwo.pdf         -> output/przyklad_01/pelnomocnictwo.json         klucze jak we wzorcu pelnomocnictwo.json ("mocodawca", …)
input/przyklad_01/przelew.pdf                -> output/przyklad_01/przelew.json                klucze jak we wzorcu przelew.json ("przelew_bankowy")
input/przyklad_03/potwierdzenie_przelewu.pdf -> output/przyklad_03/potwierdzenie_przelewu.json nazwa jak PDF, typ z treści
... i tak dla wszystkich 60 spraw (180 dokumentów)
```

- Dane: `data/uzp/dane/przyklad_*`. Uruchamiamy prawdziwe CLI, tak jak jury.
- Sprawdza: CLI, drzewo katalogów, nazwy plików, klasyfikację każdego dokumentu, kształt JSON. Nazwy PDF w danych UZP się zmieniają (`przelew.pdf`, `potwierdzenie_przelewu.pdf`), więc test nie zna nazw: każdy JSON ma nazwę jednego z PDF sprawy, a zbiory kluczy wyników i wzorców sprawy są równe. Obcy PDF w sprawie (np. ogłoszenie TED w `przyklad_04`) nie daje pliku.
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

## T4. Pełnomocnictwo: wszystkie pola jak we wzorcu

```
przyklad_02 (tabela, jeden mocodawca):
  "Mocodawca Hartica Serwis S.A."             -> "nazwa": "Hartica Serwis S.A.", "typ": "osoba_prawna"
  "KRS 9999669444, NIP 9990678035"            -> "krs": "9999669444", "nip": "9990678035"
  "adw. Bartosz Szymanski … adw. Cezary …"    -> dwóch pełnomocników
  "Aleksandra Nowakowicz" nad "Prokurent"     -> podpisujący
przyklad_41 (konsorcjum, dwóch mocodawców):
  "W imieniu Torvex …: Marek Domański"        -> podpisujący pierwszego mocodawcy
  "W imieniu Hydromel …: Agnieszka Kurek, Robert Kurek" -> podpisujący drugiego
przyklad_44 (osoba fizyczna):
  "Ja, niżej podpisany Jarosław Dudek … pod firmą DUDEK-TECH Jarosław Dudek, …"
                                              -> "imie_nazwisko": "Jarosław Dudek", "nazwa": "DUDEK-TECH Jarosław Dudek",
                                                 "krs": null, "typ": "osoba_fizyczna"
```

- Dane: `data/uzp/dane/przyklad_02`, `przyklad_41`, `przyklad_44`; cały JSON równy wzorcowi `pelnomocnictwo.json`.
- Sprawdza: `wzorce`, listy `[]`, `podzial` i `wartosc` z `config/typy/pelnomocnictwo.yaml` (ADR-0008).
- Test: `tests/test_pola.py::test_t4_pelnomocnictwo`

## T5. Liczby tylko w `config/ustawienia.yaml`, każda z pochodzeniem

```
config/typy/przelew.yaml:      wzorce: ['({RACHUNEK})']           -> dobrze, bez cyfr
config/typy/przelew.yaml:      wzorce: ['\d{2}(?:\s?\d{4}){6}']   -> błąd: cyfry w pliku typu
odwolania2json/pola.py:        okno = tekst[start:start + 120]     -> błąd: liczba w kodzie (wolno tylko 0 i 1)
odwolania2json/pola.py:        re.compile(r"\d{4}")                -> błąd: liczba we wzorcu w kodzie
tools/ocena_f1.py:             print(f"F1 = {f1:.3f}")             -> błąd: liczba w formacie f-stringu
tools/hooks/stop.py:           return 2                           -> błąd: kod protokołu; zamiast niego {"decision": "block"}
config/ustawienia.yaml:        # 26 cyfr: standard NRB
                               RACHUNEK: '\d{2}(?:\s?\d{4}){6}'   -> dobrze, komentarz nad linią
config/ustawienia.yaml:        OKNO_TEKSTU: 400                   -> błąd: brak komentarza, skąd 400
```

- Dane: pliki `config/typy/*.yaml`, `config/ustawienia.yaml`, każdy plik `.py` w `odwolania2json/`, `tools/`, `tests/`.
- Sprawdza: nowy typ to sam YAML bez liczb; liczby nie są rozsiane po kodzie, także w formatach f-stringów i we wzorcach regex w kodzie; każda liczba ma zapisane pochodzenie (komentarz w tej samej linii albo w linii nad nią).
- Test: `tests/test_konfiguracja.py::test_t5_liczby_w_jednym_pliku`

## T6. Odwołanie: wszystkie pola jak we wzorcu

```
przyklad_01 (najpierw Odwołujący, bez daty w nagłówku):
  "Zamawiający w dniu 20 marca 2026 roku unieważniił postępowanie."
                                     -> "czynnosc_dzien": "2026-03-20", "czynnosc_powod_id": 9,
                                        "czynnosc_opis": "Decyzja o unieważnieniu postępowania", "data": null
  "Odwołujący: … NIP: 9999284065", "Zamawiający: … NIP: 9997518659"
                                     -> NIP-y trafiają do właściwej strony
  "reprezentowana przez: r. pr. Aleksandra Marciniak, r. pr. Jolanta Zajkowski"
                                     -> "przez-pelnomocnika": 1, "imie_nazwisko": "Aleksandra Marciniak" (tylko pierwszy)
przyklad_03 (najpierw Zamawiający):
  "Bydgoszcz, dnia 2 marca 2026 roku" -> "miejscowosc": "Bydgoszcz", "data": "2026-03-02"
przyklad_41 (konsorcjum, dwa podmioty po stronie Odwołującego):
  "1) Lider Konsorcjum: Torvex Budownictwo sp. z o.o." -> tylko lider w "Odwolujacy"
  "polegających na: 1) odrzuceniu oferty … z dnia 4 sierpnia 2026 r."
                                     -> "czynnosc_powod_id": 1, "czynnosc_dzien": "2026-08-04"
  "Unii Europejskiej nr 2026/S 142-999327" -> "numer_ted": "999327-2026"
```

- Dane: `data/uzp/dane/przyklad_01`, `przyklad_03`, `przyklad_41`; cały JSON równy wzorcowi `odwolanie.json`.
- Sprawdza: `sekcja`, `slownik`, szablon `wartosc` z grup nazwanych, fragmenty typu (`wzorce` w pliku typu), pierwsze trafienie w tekście dla pola bez `[]` (ADR-0010).
- Test: `tests/test_pola.py::test_t6_odwolanie`

## Pomiar jakości (to nie jest test)

`tools/ocena_f1.py` przepuszcza wszystkie 60 spraw treningowych przez CLI i liczy F1 według ADR-0003. Przykładowy wynik:

```
Dokumenty: 180 | typ poprawny: 180/180
F1 = 0.412  (TP 900 | FP 120 | FN 2450)
Najgorsze pola (FN+FP):
  odwolanie   Odwolujacy[].nip   FN 58  FP 0
```

To kompas: każda zmiana ekstrakcji powinna podnosić F1.
