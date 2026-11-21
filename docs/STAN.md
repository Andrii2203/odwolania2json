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
- GUI (ADR-0006): `odwolania2json/gui.py`, `gui.bat` (Streamlit, PDF obok JSON).

## Nowe od UZP (2026-11-21)

- `data/uzp/dane/skany/`: 30 skanów z wzorcami JSON. Według użytkownika na stoisku UZP pokazują te same dane, co na GitHubie, więc skany najlepiej przypominają zbiór testowy.
- Imiona i nazwiska w mianowniku. LLM tylko przez firmę z polityką prywatności, serwery w UE/EOG, bez hostingu prywatnego.
- Punkty LLM (Discord): średnia liczba parametrów wszystkich użytych modeli (MoE: wszystkie parametry): <=8B 20 pkt, 8–14B 18, 14–32B 12, 32–70B 8, 70–150B 4, >150B 0.
- README UZP (21.11 12:14): obcy dokument ma dać „pusty plik .json”. Pracownik UZP na stoisku: pusty plik wejściowy -> klucze z pustymi wartościami (bez wskazania, którego typu).
- README UZP: premiowana „transparentność procesu ekstrakcji danych” i konfiguracja nowych klas bez zmiany kodu.

## Plan (wszystko dziś w nocy, nowy czat)

Kolejność według użytkownika: najpierw pomiar na dużej liczbie plików, potem decyzja o LLM i pustym JSON.

| # | Kto | Co |
|---|---|---|
| 1 | Claude | **Zrobione (a), (b) TED; zostaje (b) faktury/wyroki KIO/BZP i (c) pusty/uszkodzony PDF.** Pomiar na dużej liczbie plików (narzędzie w `tools/`, ADR, opis w `docs/testy.md` jako pomiar). (a) Warianty dokumentów treningowych: podmiana wartości (nazwy, NIP, daty, kwoty), etykiet („NIP:” -> „NIP Odwołującego:”), kolejności bloków, podziału linii; poprawny JSON znany, bo wiemy, co wstawiliśmy. Setki–tysiące wariantów, na poziomie tekstu (szybko) i kilka jako PDF. (b) Kilkaset publicznych obcych PDF (wyroki KIO, TED, BZP, faktury): żaden nie dostaje typu. (c) Pusty PDF, PDF bez tekstu i obrazu, PDF uszkodzony. Wynik: F1 na wariantach i lista najsłabszych reguł |
| 2 | Claude + Użytkownik | Decyzja o LLM po wynikach z 1: jeśli F1 na wariantach dużo niższe niż 0.999, LLM jeden model <=8B (np. `ministral-8b-2512` Mistral AI albo `Olala-v1.0-mini-7A1B` OVH) tylko dla pól `null`, wartość przyjęta tylko gdy jest dosłownie w tekście |
| 3 | Claude | Pusty JSON dla obcego i pustego dokumentu (format z pytania 1 niżej); zmiana T2, ADR |
| 4 | Claude | `README.md` po polsku: instalacja, `start.bat`, GUI, pomiar jakości, opis rozwiązania (bez LLM / z LLM) |
| 5 | Claude | Transparentność: `--wyjasnij` (dla każdego pola fragment tekstu i nazwa reguły, jak `--debug` w invoice2data) i podgląd w GUI; nie w `output/`, żeby nie mylić oceny |
| 6 | Claude | Słownik polski dla OCR (sjp.pl, CC BY 4.0) zamiast łatek słów w `poprawki_ocr`; sprawdzić licencję i zmierzyć na skanach |
| 7 | Claude | Instrukcja „jak dodać nowy typ” z przykładem (np. faktura) dla finału |
| 8 | [Argon] | Prezentacja PDF <= 10 MB wg ADR-0006 |
| 9 | Użytkownik | Repozytorium publiczne przed 11:00; `.env` poza git |
| 10 | Claude + Użytkownik | Finalny pomiar F1, `start.bat` na czystym katalogu, oddanie; termin nd 11:00 |

## Otwarte pytania

1. Pusty JSON: jaki plik dla obcego dokumentu i dla pustego PDF? Kandydaci: `{}`, plik 0 bajtów, szablon jednego typu z `null` (którego? najbliższego wg znaczników?), wszystkie trzy szablony z `null`. Przy F1 liczonym tylko z niepustych wartości (`tools/ocena_f1.py`) wynik jest ten sam, ale UZP może sprawdzać format. Najlepiej przykład pliku od UZP; bez odpowiedzi: `{}`.
2. Ile punktów LLM, jeśli rozwiązanie w ogóle nie używa LLM? Do której części oceny wchodzą te punkty (preselekcja to 100% F1)?
3. Brak nietkniętego zbioru: reguły dopasowane do danych treningowych i skanów. Uczciwa ocena na nowych dokumentach to skany przed dopasowaniem: 0.8696. Dlatego pomiar z planu, pkt 1.
4. Wzorce UZP niespójne: w skanach `z_rachunku` z „PL”, w treningowych bez. Trzymamy się treningowych.
5. Znane błędy skanów bez reguły (kontekst): kancelaria brana za mocodawcę; ten sam NIP z myślnikami i bez daje drugiego mocodawcę; kilku Zamawiających listą numerowaną („Zamawiający wspólnie …: 1) … 2) …”); podpisujący powtarzany; nazwa kancelarii z przecinkiem.
6. Jak UZP liczy F1: nie blokuje pracy (ADR-0005).

## Uwagi do pracy

- Szybkie próby reguł na skanach: raz zapisać tekst OCR 30 skanów do plików (ok. 4 min), potem oceniać reguły na tym tekście (sekundy). W tym czacie robił to skrypt w katalogu tymczasowym; warto przenieść do `tools/`.
- `tools/przeglad.py` kopiuje `config/` przy każdej wartości: nie zmieniać `config/` w trakcie pomiaru (albo mierzyć na kopii repozytorium, `git worktree`).
- Commituj test razem z kodem i konfiguracją, które go zazieleniają; inaczej CI na pośrednim commicie jest czerwone.
- CI klonuje najnowsze dane UZP: zmiana danych u UZP może zaczerwienić CI. Wtedy `git -C data/uzp pull`, testy lokalnie, poprawka.
