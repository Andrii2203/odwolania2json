# Testy

TDD: najpierw opis tutaj (z przykładem), potem czerwony test, kod i zielony test.
Każdy test to jeden przykład. Testu bez punktu w tym pliku nie piszemy.
Ścieżki do danych UZP są w jednym miejscu: `UZP` (`data/uzp`) i `DANE` (`data/uzp/dane`) w `tools/ocena_f1.py`; testy ich używają.

## T1. Test przekrojowy (walking skeleton): każda sprawa z 3 dokumentów daje 3 JSON

```
input/przyklad_01/odwolanie.pdf              -> output/przyklad_01/odwolanie.json              klucze jak we wzorcu odwolanie.json ("OdwolanieKIO", …)
input/przyklad_01/pelnomocnictwo.pdf         -> output/przyklad_01/pelnomocnictwo.json         klucze jak we wzorcu pelnomocnictwo.json ("mocodawca", …)
input/przyklad_01/przelew.pdf                -> output/przyklad_01/przelew.json                klucze jak we wzorcu przelew.json ("przelew_bankowy")
input/przyklad_03/potwierdzenie_przelewu.pdf -> output/przyklad_03/potwierdzenie_przelewu.json nazwa jak PDF, typ z treści
... i tak dla wszystkich 60 spraw (180 dokumentów)
```

- Dane: `data/uzp/dane/przyklad_*`. Uruchamiamy prawdziwe CLI, tak jak jury.
- Sprawdza: CLI, drzewo katalogów, nazwy plików, klasyfikację każdego dokumentu, kształt JSON. Nazwy PDF w danych UZP się zmieniają (`przelew.pdf`, `potwierdzenie_przelewu.pdf`), więc test nie zna nazw: każdy JSON ma nazwę jednego z PDF sprawy, a zbiory kluczy wyników i wzorców sprawy są równe. Obcy PDF w sprawie (np. ogłoszenie TED w `przyklad_04`) daje plik z `{}` (T2); każdy PDF ma swój JSON.
- Trudny przykład: pełnomocnictwo bez słowa „mocodawca”, ale z „udzielam pełnomocnictwa”, też ma dać `pelnomocnictwo`.
- Test: `tests/test_e2e.py::test_t1_sprawa_trzy_dokumenty`

## T2. Obcy dokument daje plik z `{}`

```
input/negatywne/KIO_KIO 2617-21.pdf (wyrok KIO, podobny do odwołania)  -> output/negatywne/KIO_KIO 2617-21.json: {}
input/negatywne/2025_S 112-383751.pdf (ogłoszenie TED)                -> output/negatywne/2025_S 112-383751.json: {}
... i tak dla wszystkich 13 obcych dokumentów (odpowiedź UZP na Discordzie, ADR-0013)
```

- Dane: `data/uzp/dane/negatywne/*.pdf` (12 plików) i `data/uzp/szablon-aplikacja/input/case1/negatywny przyklad.pdf`.
- Sprawdza: obcy dokument nie dostaje typu, więc nie daje wymyślonych wartości (FP); plik jest, ale pusty: `{}`.
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

- Rachunki porównujemy bez „PL” (`bez_prefiksu` w `config/ustawienia.yaml`): wzorce treningowe nie mają „PL”, a według UZP to błąd wzorców (T11, ADR-0014).

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

## T7. Błąd w jednym dokumencie nie zatrzymuje pozostałych

```
input/przyklad_01/odwolanie.pdf       -> output/przyklad_01/odwolanie.json
input/przyklad_01/pelnomocnictwo.pdf  -> output/przyklad_01/pelnomocnictwo.json
input/przyklad_01/przelew.pdf         -> wyjątek przy wyciąganiu pola: na ekranie „błąd: przyklad_01/przelew.pdf: …”, output/przyklad_01/przelew.json: {}
kod wyjścia CLI: 1 (był błąd), ale dwa pozostałe pliki są zapisane
```

- Dane: `data/uzp/dane/przyklad_01` i kopia `config/` z zepsutym polem `przelew_bankowy.kwota` (`format: liczba` na słowie bez cyfr daje `ValueError`).
- Sprawdza: CLI przetwarza każdy plik osobno (`przetworz_wszystkie`). Jeden nieprzewidziany wyjątek (OCR, LLM, dziwny tekst) nie zabiera jury wszystkich pozostałych JSON.
- Test: `tests/test_e2e.py::test_t7_blad_jednego_dokumentu`

## T8. F1 na danych treningowych nie spada poniżej progu

```
config/ustawienia.yaml: narzedzia.MIN_F1: 0.998   (pomiar 2026-11-21: F1 = 0.9983)
zmiana reguły psuje 2 pola  -> F1 = 0.9976 < 0.998 -> test czerwony, commit zablokowany
```

- Dane: `data/uzp/dane` (60 spraw i obce dokumenty), liczone tak jak `tools/ocena_f1.py` (funkcja `ocena`).
- Sprawdza: żadna zmiana (OCR, LLM, nowe reguły) nie obniża jakości po cichu. Świadome obniżenie progu to zmiana `MIN_F1` z nowym pomiarem w komentarzu.
- Test: `tests/test_e2e.py::test_t8_f1_nie_spada`

## T9. Skan bez warstwy tekstu daje JSON (OCR)

```
skany/potwierdzenia/0001/0001.pdf   (1 strona, sam obraz; pypdf daje 0 znaków)
  -> OCR -> typ przelew, "kwota": 7500.0, "data_operacji": "2026-09-11", "numer_transakcji": "CEN9057564440515"
skany/pelnomocnictwa/0001/0001.pdf  -> typ pelnomocnictwo
skany/odwolania/0001/0001.pdf       (5 stron) -> typ odwolanie
3 typy poprawne, F1 tych 3 dokumentów >= narzedzia.MIN_F1_SKANY
```

- Dane: `data/uzp/dane/skany/<typ>/0001/` (PDF i wzorzec JSON), pierwszy skan każdego typu. Wszystkie 30 skanów to ok. 4 min (OCR ok. 3,5 s na stronę), za długo na każdy commit. Pełny pomiar: `tools/ocena_f1.py --dane data/uzp/dane/skany/potwierdzenia data/uzp/dane/skany/pelnomocnictwa data/uzp/dane/skany/odwolania`.
- Sprawdza: strona z tekstem krótszym niż `MIN_ZNAKOW_STRONY` idzie do OCR (`pypdfium2` + RapidOCR, ADR-0007); ramki OCR składane w wiersze mimo przekrzywienia skanu; typ i pola z tych samych reguł YAML co dla PDF cyfrowych; litery bez polskich znaków (`warianty_liter`) w klasyfikacji i wzorcach; `sekcja` przy jednym wzorcu (lista pełnomocników bez tytułów).
- Test: `tests/test_e2e.py::test_t9_skany`

## T10. Etykieta innego pola nie jest wartością

```
Data Opis Kwota                              <- wiersz nagłówków tabeli (skany UZP, potwierdzenia/0002)
Data operacji 2026-04-09
Tytuł: opłata skarbowa od pełnomocnictwa
-> przelew_bankowy.tytul = "opłata skarbowa od pełnomocnictwa"   (nie "Kwota")
```

- Sprawdza: wartość równa etykiecie innego pola typu (albo słowu z listy `stop`) jest pomijana, wygrywa następne trafienie.
- Test: `tests/test_pola.py::test_t10_etykieta_nie_jest_wartoscia`

## T11. Rachunek jak w dokumencie, z „PL”, jeśli jest

```
"Z rachunku: PL 62 2170 0008 9152 5017 5661 7062"  -> z_rachunku  = "PL62217000089152501756617062"
"Na rachunek: 68 4382 2304 9992 2952 6283 4736"    -> na_rachunek = "68438223049992295262834736"
```

- Źródło: UZP na Discordzie (21.11): numer taki, jak w dokumencie; wzorce bez „PL” to błąd, którego nie będzie w zbiorze testowym. Wzorce skanów mają `PL` + 26 cyfr bez spacji.
- Test: `tests/test_pola.py::test_t11_rachunek_z_pl`

## T12. `--wyjasnij`: dla każdego pola reguła i fragment tekstu, JSON bez zmian

```
python -m odwolania2json --wyjasnij  (input/przyklad_01/przelew.pdf)
przyklad_01/przelew.pdf → przelew
  przelew_bankowy.kwota = 200.0
      reguła: etykieta „kwota”, wzorzec „({KWOTA})”
      tekst:  „Kwota 200,00 PLN”
  ...
  puste: (brak)
output/przyklad_01/przelew.json  -> taki sam jak bez --wyjasnij
```

- Źródło: UZP premiuje „transparentność procesu ekstrakcji”; dziennik służy też do szukania błędów (ADR-0012, etap 10).
- Test: `tests/test_e2e.py::test_t12_wyjasnij`

## Pomiar jakości (to nie jest test)

`tools/ocena_f1.py` przepuszcza wszystkie 60 spraw treningowych przez CLI i liczy F1 według ADR-0003. Przykładowy wynik:

```
Dokumenty: 180 | typ poprawny: 180/180
F1 = 0.412  (TP 900 | FP 120 | FN 2450)
Najgorsze pola (FN+FP):
  odwolanie   Odwolujacy[].nip   FN 58  FP 0
```

To kompas: każda zmiana ekstrakcji powinna podnosić F1. Dolną granicę pilnuje test T8.

### Pomiar na wariantach i obcych dokumentach (ADR-0011)

`tools/warianty.py` zmienia tekst dokumentów treningowych i od razu zmienia wzorzec JSON, bo wiemy, co wstawiliśmy. Każda rodzina zmian ma osobne F1:

```
przed:  "Odwołujący:\nBelmoria Rozwiązania S.A.\n... NIP: 9999284065"
wartosci:        NIP: 9999284065 -> NIP: 4170385529, w JSON też 4170385529
braki:           NIP: 9999284065 -> NIP: brak, w JSON null
nazwy:           Belmoria -> Rlaombie (litery w innej kolejności), w JSON też
daty:            wszystkie daty z JSON przesunięte o tyle samo dni, w tekście w tym samym zapisie
etykieta:        "Odwołujący:" -> "ODWOŁUJĄCY:", JSON bez zmian
bloki:           blok Odwołującego przed blokiem Zamawiającego, JSON bez zmian
laczenie_linii:  część końców linii -> spacja, JSON bez zmian
lamanie_linii:   linie zawinięte do połowy najdłuższej, JSON bez zmian

Warianty: 4673 | F1 razem = 0.9559
  F1 0.7550  warianty 60  zły typ 0  etykieta ^Odwołujący: -> ODWOŁUJĄCY:
```

`tools/pobierz_obce.py` pobiera polskie ogłoszenia TED do `data/obce/ted`; `tools/ocena_f1.py --dane data/obce` liczy, ile z nich dostało JSON (ma być 0).
