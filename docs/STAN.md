# Stan

Aktualizacja: 2026-11-22 00:45, Claude (nowy plan: ocena na VM UZP). Następny czat zaczyna od „Plan” niżej.

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
- Badania: `docs/badania/` (`llm-ue.md`, `ocr.md`, `ovh-limity.md`, `podobne-rozwiazania.md`, `gliner2.md`, `wektory-etykiet.md`, `braki-i-ryzyka.md`); kryteria oceny i nasz stan: `docs/kryteria.md`.
- Pomiar na nowych dokumentach (ADR-0011, 21.11 noc): `tools/warianty.py` 4673 warianty dokumentów treningowych, **F1 0.9559**; najsłabsze: etykieta „Odwołujący:” zapisana inaczej (0.755, także „ODWOŁUJĄCY:”), `laczenie_linii` (0.834), „Tytuł przelewu” -> „Tytuł operacji” (0.833), „Zamawiający:” inaczej (0.890), „Data operacji” -> „Data” (0.902). Obce: `tools/pobierz_obce.py` 160 ogłoszeń TED, **0/160 z JSON**.
- Noc 21/22.11: obcy, pusty, uszkodzony PDF -> `{}` (ADR-0013); rachunek z „PL” jak w dokumencie (ADR-0014, 48/60 przelewów ma „PL”); nagłówki stron bez wielkości liter („ODWOŁUJĄCY:” 0.755 -> 1.000); dziennik `--wyjasnij` i tabela w GUI (T12); bramka `utnij` dla nazw (ADR-0015); etykiety banków dla tytułu przelewu („Tytuł operacji” 0.833 -> 0.995); kontekst sprawy (ADR-0016). Warianty **F1 0.9798** (było 0.9559), skany **0.9462** (było 0.9396), treningowe 0.9990 bez zmian.
- Porządki 21.11 (ADR-0009 pkt 9): znaki-reguły z kodu do `ustawienia.yaml` (`obcinane_po_bramce`, `separatory_dziesietne`, `ROZDZIELNIK_CYFR`); bez dubli: `dokument_z_tekstu` i `kontekst_sprawy` w `pipeline.py` wspólne dla CLI, GUI i `tools/warianty.py`; `miara_f1`, `typy_wzorow`, `pole_ogolne` raz, w `tools/ocena_f1.py`. Wyniki bez zmian (treningowe 0.9990, warianty 0.9798, obce 0/160).
- GLiNER2 sprawdzony i odrzucony: F1 0.551 wobec 0.999 reguł, odwołanie 14,8 s (`docs/badania/gliner2.md`).
- Wektory etykiet (etap 6) zmierzone w ślepym teście poza repozytorium (`docs/badania/wektory-etykiet.md`): Test 1 (1 etykieta/pole w `przelew.yaml`, wycięte 46 synonimów) F1 **0.3900 -> 0.6486** (`multilingual-e5-small` CPU ONNX, 0,45 s) i **0.7132** (OVHcloud `bge-m3`); Test 2 (100 nowych ślepych wariantów etykiet, 5 210 dokumentów, zamrożony YAML) F1 **0.9270 -> 0.9624** (`multilingual-e5-small`, czysty czas ONNX 0,98 s) i **0.9634** (OVHcloud `bge-m3`).
- Czas (ten komputer, 16 wątków): cyfrowa sprawa 3 dokumenty 0,4 s; skany ok. 4 s na stronę (odwołanie 5 stron ok. 20 s). JSON zapisywany zaraz po każdym dokumencie. Ryzyko: wiele skanów na słabym komputerze.
- GUI (ADR-0006): `odwolania2json/gui.py`, `gui.bat` (Streamlit, PDF obok JSON).

## Nowe od UZP (2026-11-21)

- 22.11 w nocy: `data/uzp/VM.md` (ocena na maszynie UZP, zob. „Plan”); README: 150 PDF w 45 min; zasady punktów za model jeszcze zmieniane („stay tuned”). Discord: rachunek bez spacji, z kodem kraju, jeśli jest (nie tylko PL); lokalny mały model NER (~0,2 mld) dozwolony; jednego PDF z załącznikami w ocenie nie będzie; pytanie bez odpowiedzi: data zlecenia czy księgowania jako `data_operacji`.

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

## Plan (22.11 od 00:45): ocena na maszynie UZP (`data/uzp/VM.md`)

UZP ocenia na swojej maszynie wirtualnej: Ubuntu 24.04, 2 vCPU, 16 GB, bez GPU, Python 3.12, internet jest. Oceniający wgrywa PDF do `/opt/solution/input`, uruchamia komendę z `/opt/solution/RUN.md` (z `sudo`, bez interakcji), zabiera `/opt/solution/output`. Dostęp zespołów odcięty 22.11 o 11:00. README UZP: 150 PDF w 45 min (18 s na PDF). Lokalne modele, które mieszczą się w czasie: 20 pkt.

| # | Kto | Co | Dlaczego |
|---|---|---|---|
| 1 | Użytkownik | Formularz VM (jeden na zespół), od razu | bez maszyny nie ma oceny; czekamy na login i IP |
| 2 | Claude | Linux: Python 3.13 przez `uv` (na VM jest 3.12, UZP wymaga 3.13+), `RUN.md`, skrypt instalacji, modele OCR pobrane przy instalacji, test po `sudo reboot` | komenda musi działać bez nas |
| 3 | Claude | Czas na 2 vCPU: pomiar skanów; straż czasu (liczba w `ustawienia.yaml`): po przekroczeniu reszta bez OCR; ewentualnie OCR tylko pierwszych stron, DPI (`tools/przeglad.py`) | 45 min na 150 PDF, nie wiemy, ile skanów |
| 4 | Claude | Rachunek z dowolnym kodem kraju (IBAN), bez spacji (Discord) | F1 |
| 5 | Claude | Ten sam NIP z myślnikami i bez: jeden mocodawca; inne znane błędy skanów („Otwarte pytania” 5) | F1; skany najbliżej zbioru testowego |
| 6 | Claude | `README.md`, „jak dodać nowy typ” | finał: 50% za konfigurację nowych typów |
| 7 | Claude | GUI: pliki jako jedna sprawa (kontekst), cache, edycja JSON, pobieranie JSON i ZIP | prezentacja, przejrzystość |
| 8 | [Argon] | Prezentacja PDF <= 10 MB wg ADR-0006 | |
| 9 | Użytkownik | Repozytorium publiczne, `.env` poza git, nazwa zespołu jak w drafcie (Discord) | |
| 10 | Claude + Użytkownik | Końcowy test na VM dokładnie jak UZP (czyste `output/`, komenda z `RUN.md`, po restarcie), STAN | |

Odłożone: wektory etykiet (etap 6, `docs/badania/wektory-etykiet.md`): na 2 vCPU z limitem czasu i bez zysku na znanych etykietach ryzyko większe niż zysk; opis w prezentacji. Słownik sjp.pl, Morfeusz.

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
