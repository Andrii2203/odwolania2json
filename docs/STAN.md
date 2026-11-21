# Stan

Aktualizacja: 2026-11-21 noc, Claude (skany, porządki liczb, kryteria). Następny czat zaczyna od „Plan” niżej.

## Zrobione

- Repozytorium (prywatne): https://github.com/Andrii2203/odwolania2json. Python 3.13.
- `AGENTS.md` (+ `CLAUDE.md`, `GEMINI.md`), ADR-0001..0010, `docs/testy.md` (T1–T10).
- Potok: CLI `input/ -> output/`, klasyfikacja z YAML (`znaczniki`, `wykluczenia`), pola z YAML (`etykiety`, `wzorce`, `format`, `sekcja`, `slownik`, `podzial`), `przetworz_wszystkie()` wspólne dla CLI, GUI i `tools/ocena_f1.py`.
- Klasyfikacja: 180/180 dokumentów treningowych poprawnie, 13/13 obcych dokumentów UZP bez JSON.
- Wynik: dane treningowe (60 spraw) **F1 0.9990**; skany UZP (30) **F1 0.9396** (rano 0.8696). Uwaga: reguły są dopasowane do obu zbiorów, więc to nie jest ocena na nowych dokumentach (zob. „Otwarte pytania”).
- ADR-0009: jeden mechanizm pól, wszystkie liczby w `config/ustawienia.yaml`; komentarz podaje regułę wyboru i polecenie pomiaru, bez wyników (pkt 8). Pilnuje T5. Ponowny pomiar 21.11 wieczorem: wszystkie 7 liczb z pomiaru (`PROG`, `OKNO_WARTOSCI`, `OKNO_TEKSTU`, `ODSTEP_ETYKIETY`, `DLUGOSC_ID`, `OCR_DPI`, `TOLERANCJA_WIERSZA`) nadal spełnia swoją regułę.
- Progi testów: `MIN_F1 = 0.9985` (T8: przepuszcza jedno błędne pole, blokuje dwa), `MIN_F1_SKANY = 0.96` (T9: obecnie 0.9677 na 3 skanach).
- Porządki: wspólne fragmenty `NIP_Z_ETYKIETA`, `KRS_Z_ETYKIETA`, `REGON_Z_ETYKIETA`, `PESEL_Z_ETYKIETA`, `PRAWNIK`, `PUNKT_ZAMAWIAJACEGO`, `NAGLOWEK_ODWOLUJACEGO`; ścieżki `UZP`, `DANE` tylko w `tools/ocena_f1.py`; `start.bat`/`gui.bat` najpierw Python 3.13.
- OCR (ADR-0007, T9): strona bez tekstu -> `pypdfium2` + RapidOCR, ok. 3,5 s na stronę.
- Skany (21.11 noc), reguły ogólne (nowe układy, prawdopodobnie też w ukrytych PDF cyfrowych): konsorcjum z „(Lider Konsorcjum)” / „(Partner Konsorcjum)” za nazwą; osoba fizyczna „pod firmą”; stopka i pieczęć między „wobec:” a punktem; nazwa w dwóch liniach po „w”; „Szczegóły płatności”; etykieta w dwóch liniach komórki; data „20 04 2026”; `FIRMA` ze skrótem wielkimi („IT”) i „i”; funkcja podpisującego nie jest częścią nazwy; T10: etykieta innego pola nie jest wartością (nagłówek tabeli).
- Skany, łatki OCR (tylko wpisane słowa, nie przyczyna): „odwolania”, „oplata”, „pelnomocnictwa”, „postepowania” bez polskich znaków, „Lódź”, „o” zamiast „0” w BZP, „Ñ”, „·” (`poprawki_ocr`).
- Straże: pre-commit (testy, język polski), hooki Claude (TDD, stop), CI na Windows. Opis w `AGENTS.md`.
- Klucz OVHcloud działa (`chat/completions`). LLM w programie nie jest używany.
- Badania: `docs/badania/` (`llm-ue.md`, `ocr.md`, `ovh-limity.md`, `podobne-rozwiazania.md`); kryteria oceny i nasz stan: `docs/kryteria.md`.
- Pomiar na nowych dokumentach (ADR-0011, 21.11 noc): `tools/warianty.py` 4673 warianty dokumentów treningowych, **F1 0.9559**; najsłabsze: etykieta „Odwołujący:” zapisana inaczej (0.755, także „ODWOŁUJĄCY:”), `laczenie_linii` (0.834), „Tytuł przelewu” -> „Tytuł operacji” (0.833), „Zamawiający:” inaczej (0.890), „Data operacji” -> „Data” (0.902). Obce: `tools/pobierz_obce.py` 160 ogłoszeń TED, **0/160 z JSON**.
- Noc 21/22.11: obcy, pusty, uszkodzony PDF -> `{}` (ADR-0013); rachunek z „PL” jak w dokumencie (ADR-0014, 48/60 przelewów ma „PL”); nagłówki stron bez wielkości liter („ODWOŁUJĄCY:” 0.755 -> 1.000). Warianty **F1 0.9692** (było 0.9559), skany **0.9462** (było 0.9396), treningowe 0.9990 bez zmian.
- GLiNER2 sprawdzony i odrzucony: F1 0.551 wobec 0.999 reguł, odwołanie 14,8 s (`docs/badania/gliner2.md`).
- Czas (ten komputer, 16 wątków): cyfrowa sprawa 3 dokumenty 0,4 s; skany ok. 4 s na stronę (odwołanie 5 stron ok. 20 s). JSON zapisywany zaraz po każdym dokumencie. Ryzyko: wiele skanów na słabym komputerze.
- GUI (ADR-0006): `odwolania2json/gui.py`, `gui.bat` (Streamlit, PDF obok JSON).

## Nowe od UZP (2026-11-21)

- `data/uzp/dane/skany/`: 30 skanów z wzorcami JSON. Według użytkownika na stoisku UZP pokazują te same dane, co na GitHubie, więc skany najlepiej przypominają zbiór testowy.
- Imiona i nazwiska w mianowniku. LLM tylko przez firmę z polityką prywatności, serwery w UE/EOG, bez hostingu prywatnego.
- Punkty LLM (Discord): średnia liczba parametrów wszystkich użytych modeli (MoE: wszystkie parametry): <=8B 20 pkt, 8–14B 18, 14–32B 12, 32–70B 8, 70–150B 4, >150B 0.
- README UZP (21.11 12:14): obcy dokument ma dać „pusty plik .json”. Pracownik UZP na stoisku: pusty plik wejściowy -> klucze z pustymi wartościami (bez wskazania, którego typu).
- README UZP: premiowana „transparentność procesu ekstrakcji danych” i konfiguracja nowych klas bez zmiany kodu.
- Discord UZP (21.11 wieczorem, `docs/UZP/from discord.md`):
  - Obcy dokument (spoza klas): plik JSON z samym `{}`, ta sama nazwa co PDF (`potwierdzenie_przelewu.pdf` -> `potwierdzenie_przelewu.json`).
  - Rachunek: tak jak w dokumencie, z „PL”, jeśli jest. Wzorce bez „PL” to błąd UZP; w zbiorze testowym go nie będzie. Skany: `PL` + 26 cyfr bez spacji.
  - Nazwa firmy: tak jak w dokumencie (nie z CEIDG).
  - Czas: każde rozwiązanie ma ograniczony czas; program może nie skończyć. Liczba dokumentów i limit nieznane (uczestnik pytał o 150 dokumentów w 45 min, ok. 18 s na dokument). Rate limit API nie wpływa na ocenę.
  - Elastyczność: liczy się też konfiguracja reguł rozpoznawania, walidacji i mapowania pól; nowa klasa tylko przez plik konfiguracyjny.
  - Ocena na PDF cyfrowych i na skanach.
  - LLM tylko u firmy z polityką prywatności; hosting LLM przez osobę prywatną (własny komputer) wykluczony. Nie wiadomo, czy dotyczy to małego modelu nie-LLM (GLiNER2, ok. 0,2 mld parametrów) uruchamianego lokalnie jak OCR: zapytać.

## Plan (noc 21/22.11): potok etapów, `docs/potok.md`, ADR-0012

Etapy podłączamy po jednym; po każdym pomiar (`ocena_f1.py`, skany, `warianty.py`, obce) i tabela stanu w `docs/potok.md`.

| # | Kto | Etap | Co |
|---|---|---|---|
| 1 | Claude | **zrobione** 2 | Sekcje bez wielkości liter („ODWOŁUJĄCY:” gubi wszystkie pola Odwołującego, F1 wariantu 0.755); przeniesienia wyrazów |
| 2 | Claude | **zrobione** 10 | Dziennik „skąd każda wartość” (etap, reguła, fragment tekstu), `--wyjasnij`, podgląd w GUI; potrzebny do szukania błędów w kolejnych etapach |
| 3 | Claude | **częściowo** (nazwy: `utnij`, ADR-0015) 5 | Bramka: stopy w środku linii (adres „ul.”, kod pocztowy, „KRS:”, „NIP:”, e-mail), reguły w YAML; cel: `laczenie_linii` (0.834) |
| 4 | Claude | **zrobione** (ADR-0016) 8 | Kontekst sprawy: wartości z innych dokumentów sprawy jako kandydaci, tylko jeśli są w tekście |
| 0a | Claude | **zrobione** 0, 10 | Obcy, pusty i uszkodzony PDF -> plik z `{}` (Discord UZP); zmiana T2, ADR. Robimy najpierw: pewny wpływ na ocenę |
| 0b | Claude | **zrobione** 9 | Rachunek z „PL”, jeśli jest w dokumencie (Discord UZP); `tools/ocena_f1.py` porównuje rachunek bez „PL”, bo wzorce treningowe są tu błędne; ADR. Robimy najpierw |
| 0c | Claude | **zrobione** | Czas: zmierzyć sekundy na dokument (cyfrowy, skan, z GLiNER2); JSON zapisywany zaraz po każdym dokumencie |
| 6 | Claude | 1 | Słownik sjp.pl (CC BY 4.0) zamiast łatek `poprawki_ocr`; pomiar na skanach |
| 7 | Claude | 9 | Mianownik (Morfeusz2, BSD-2: sprawdzić wheel dla Python 3.13), duplikaty NIP z myślnikami i bez |
| 8 | Claude + Użytkownik | 6, 7 | Decyzja: wektory etykiet i/lub LLM dla pól, które nadal są puste (po pomiarze 1–7); nowe zamiany etykiet w `warianty`, których reguły nie widziały |
| 9 | Claude | | Obce dokumenty poza TED (faktury, wyroki KIO, BZP); `README.md`; instrukcja „jak dodać nowy typ” (finał) |
| 10 | [Argon] | | Prezentacja PDF <= 10 MB wg ADR-0006 |
| 11 | Użytkownik | | Repozytorium publiczne przed 11:00; `.env` poza git; zapytać UZP o lokalny model embeddingów |
| 12 | Claude + Użytkownik | | Finalny pomiar F1, `start.bat` na czystym katalogu, oddanie; termin nd 11:00 |

## Otwarte pytania

1. ~~Pusty JSON~~: odpowiedź UZP: plik z `{}` dla obcego dokumentu. Pusty i uszkodzony PDF traktujemy tak samo.
2. Ile punktów LLM, jeśli rozwiązanie w ogóle nie używa LLM? Do której części oceny wchodzą te punkty (preselekcja to 100% F1)?
3. Brak nietkniętego zbioru: reguły dopasowane do danych treningowych i skanów. Uczciwa ocena na nowych dokumentach to skany przed dopasowaniem: 0.8696. Dlatego pomiar z planu, pkt 1.
4. ~~Rachunek z „PL” czy bez~~: odpowiedź UZP: jak w dokumencie, z „PL”. Wzorce treningowe bez „PL” są błędne.
5. Znane błędy skanów bez reguły (kontekst): kancelaria brana za mocodawcę; ten sam NIP z myślnikami i bez daje drugiego mocodawcę; kilku Zamawiających listą numerowaną („Zamawiający wspólnie …: 1) … 2) …”); podpisujący powtarzany; nazwa kancelarii z przecinkiem.
6. Jak UZP liczy F1: nie blokuje pracy (ADR-0005).

## Uwagi do pracy

- Szybkie próby reguł na skanach: raz zapisać tekst OCR 30 skanów do plików (ok. 4 min), potem oceniać reguły na tym tekście (sekundy). W tym czacie robił to skrypt w katalogu tymczasowym; warto przenieść do `tools/`.
- `tools/przeglad.py` kopiuje `config/` przy każdej wartości: nie zmieniać `config/` w trakcie pomiaru (albo mierzyć na kopii repozytorium, `git worktree`).
- Commituj test razem z kodem i konfiguracją, które go zazieleniają; inaczej CI na pośrednim commicie jest czerwone.
- CI klonuje najnowsze dane UZP: zmiana danych u UZP może zaczerwienić CI. Wtedy `git -C data/uzp pull`, testy lokalnie, poprawka.
