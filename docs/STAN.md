# Stan

Aktualizacja: 2026-11-22 06:45, Claude (pkt 6: GUI i kreator z przykładu, zakreślacz w podglądzie, faktura jako przykład, ikony Material; T26, T27, ADR-0026). Dalej: pkt 8 (ostatni test na VM) najpóźniej o 10:00. Następny czat zaczyna od „Plan” niżej.

## Zrobione

- Repozytorium (prywatne): https://github.com/Andrii2203/odwolania2json. Python 3.13.
- `AGENTS.md` (+ `CLAUDE.md`, `GEMINI.md`), ADR-0001..0010, `docs/testy.md` (T1–T10).
- Potok: CLI `input/ -> output/`, klasyfikacja z YAML (`znaczniki`, `wykluczenia`), pola z YAML (`etykiety`, `wzorce`, `format`, `sekcja`, `slownik`, `podzial`), `przetworz_wszystkie()` wspólne dla CLI, GUI i `tools/ocena_f1.py`.
- Klasyfikacja: 180/180 dokumentów treningowych poprawnie, 13/13 obcych dokumentów UZP bez JSON.
- Wynik: dane treningowe (60 spraw) **F1 0.9990**; skany UZP (30) **F1 0.9508** (21.11 rano 0.8696). Uwaga: reguły są dopasowane do obu zbiorów, więc to nie jest ocena na nowych dokumentach (zob. „Otwarte pytania”).
- ADR-0009: jeden mechanizm pól, wszystkie liczby w `config/ustawienia.yaml`; komentarz podaje regułę wyboru i polecenie pomiaru, bez wyników (pkt 8). Pilnuje T5. Ponowny pomiar 21.11 wieczorem: wszystkie 7 liczb z pomiaru (`PROG`, `OKNO_WARTOSCI`, `OKNO_TEKSTU`, `ODSTEP_ETYKIETY`, `DLUGOSC_ID`, `OCR_DPI`, `TOLERANCJA_WIERSZA`) nadal spełnia swoją regułę.
- Progi testów: `MIN_F1 = 0.9985` (T8: przepuszcza jedno błędne pole, blokuje dwa), `MIN_F1_SKANY = 0.96` (T9: obecnie 0.9677 na 3 skanach).
- Porządki: wspólne fragmenty `NIP_Z_ETYKIETA`, `KRS_Z_ETYKIETA`, `REGON_Z_ETYKIETA`, `PESEL_Z_ETYKIETA`, `PRAWNIK`, `PUNKT_ZAMAWIAJACEGO`, `NAGLOWEK_ODWOLUJACEGO`; ścieżki `UZP`, `DANE` tylko w `tools/ocena_f1.py`; `start.bat`/`gui.bat` najpierw Python 3.13.
- OCR (ADR-0007, T9): strona bez tekstu -> `pypdfium2` + RapidOCR, ok. 3,5 s na stronę.
- Skany (21.11 noc), reguły ogólne (nowe układy, prawdopodobnie też w ukrytych PDF cyfrowych): konsorcjum z „(Lider Konsorcjum)” / „(Partner Konsorcjum)” za nazwą; osoba fizyczna „pod firmą”; stopka i pieczęć między „wobec:” a punktem; nazwa w dwóch liniach po „w”; „Szczegóły płatności”; etykieta w dwóch liniach komórki; data „20 04 2026”; `FIRMA` ze skrótem wielkimi („IT”) i „i”; funkcja podpisującego nie jest częścią nazwy; T10: etykieta innego pola nie jest wartością (nagłówek tabeli).
- Skany, łatki OCR (tylko wpisane słowa, nie przyczyna): „odwolania”, „oplata”, „pelnomocnictwa”, „postepowania” bez polskich znaków, „Lódź”, „o” zamiast „0” w BZP, „Ñ”, „·” (`poprawki_ocr`).
- Straże: pre-commit (testy, język polski), hooki Claude (TDD, stop), CI na Windows. Opis w `AGENTS.md`.
- Klucz OVHcloud działa (`chat/completions`). LLM w programie nie jest używany (ADR-0022).
- Badania: `docs/badania/` (`llm-ue.md`, `ocr.md`, `ovh-limity.md`, `podobne-rozwiazania.md`, `gliner2.md`, `wektory-etykiet.md`, `braki-i-ryzyka.md`); kryteria oceny i nasz stan: `docs/kryteria.md`.
- Pomiar na nowych dokumentach (ADR-0011, 21.11 noc): `tools/warianty.py` 4673 warianty dokumentów treningowych, **F1 0.9559**; najsłabsze: etykieta „Odwołujący:” zapisana inaczej (0.755, także „ODWOŁUJĄCY:”), `laczenie_linii` (0.834), „Tytuł przelewu” -> „Tytuł operacji” (0.833), „Zamawiający:” inaczej (0.890), „Data operacji” -> „Data” (0.902). Obce: `tools/pobierz_obce.py` 160 ogłoszeń TED, **0/160 z JSON**.
- Noc 21/22.11: obcy, pusty, uszkodzony PDF -> `{}` (ADR-0013); rachunek z „PL” jak w dokumencie (ADR-0014, 48/60 przelewów ma „PL”); nagłówki stron bez wielkości liter („ODWOŁUJĄCY:” 0.755 -> 1.000); dziennik `--wyjasnij` i tabela w GUI (T12); bramka `utnij` dla nazw (ADR-0015); etykiety banków dla tytułu przelewu („Tytuł operacji” 0.833 -> 0.995); kontekst sprawy (ADR-0016). Warianty **F1 0.9798** (było 0.9559), skany **0.9462** (było 0.9396), treningowe 0.9990 bez zmian.
- Porządki 21.11 (ADR-0009 pkt 9): znaki-reguły z kodu do `ustawienia.yaml` (`obcinane_po_bramce`, `separatory_dziesietne`, `ROZDZIELNIK_CYFR`); bez dubli: `dokument_z_tekstu` i `kontekst_sprawy` w `pipeline.py` wspólne dla CLI, GUI i `tools/warianty.py`; `miara_f1`, `typy_wzorow`, `pole_ogolne` raz, w `tools/ocena_f1.py`. Wyniki bez zmian (treningowe 0.9990, warianty 0.9798, obce 0/160).
- 22.11 rano: test na VM jak UZP i kod wyjścia 0 (T7); inne pisma z akt -> `{}` (T23, ADR-0023); mianownik przez Morfeusz2 (T24, ADR-0024); sklejone linie (T25, ADR-0025). Wyniki: treningowe 0.9990, skany 0.9508, warianty **0.9870**.
- GLiNER2 sprawdzony i odrzucony: F1 0.551 wobec 0.999 reguł, odwołanie 14,8 s (`docs/badania/gliner2.md`).
- Wektory etykiet (etap 6) zmierzone w ślepym teście poza repozytorium (`docs/badania/wektory-etykiet.md`): Test 1 (1 etykieta/pole w `przelew.yaml`, wycięte 46 synonimów) F1 **0.3900 -> 0.6486** (`multilingual-e5-small` CPU ONNX, 0,45 s) i **0.7132** (OVHcloud `bge-m3`); Test 2 (100 nowych ślepych wariantów etykiet, 5 210 dokumentów, zamrożony YAML) F1 **0.9270 -> 0.9624** (`multilingual-e5-small`, czysty czas ONNX 0,98 s) i **0.9634** (OVHcloud `bge-m3`).
- Czas (ten komputer, 16 wątków): cyfrowa sprawa 3 dokumenty 0,4 s; skany ok. 4 s na stronę (odwołanie 5 stron ok. 20 s). JSON zapisywany zaraz po każdym dokumencie. Ryzyko: wiele skanów na słabym komputerze.
- GUI (ADR-0006): `odwolania2json/gui.py`, `gui.bat` (Streamlit, PDF obok JSON).
- 22.11 rano, GUI dla osoby bez przygotowania (ADR-0026): trzy kroki, przyciski „Pokaż na przykładzie” (sprawa UZP, faktura), wartości podświetlone w dokumencie (T27), kreator: nazwa pola i wartość z dokumentu, etykieta i rodzaj same (T26), ikony Material. Dokumenty (README, kryteria, potok, ADR-0006, ADR-0021, AGENTS) zgodne z GUI. Znany błąd kreatora: wartość po przecinku w linii („31-001 Kraków”) i etykieta powtórzona w dwóch sekcjach („Adres:” sprzedawcy i nabywcy) -> „wybierz rodzaj”, a ręczny wybór rodzaju i tak nie dodaje pola.

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

## Plan (22.11 od 03:30): ocena na maszynie UZP (`data/uzp/VM.md`)

UZP ocenia na swojej maszynie wirtualnej: Ubuntu 24.04, 2 vCPU, 16 GB, bez GPU, Python 3.12, internet jest. Oceniający wgrywa PDF do `/opt/solution/input`, uruchamia komendę z `/opt/solution/RUN.md` (z `sudo`, bez interakcji), zabiera `/opt/solution/output`. Dostęp zespołów odcięty 22.11 o 11:00. README UZP: 150 PDF w 45 min (18 s na PDF). Lokalne modele, które mieszczą się w czasie: 20 pkt.

Wcześniej (do 22.11 03:30) zrobione: formularz VM, instalacja w `/opt/solution` (Python 3.13 przez `uv`, `RUN.md`, `instaluj.sh`, `uruchom.sh`, ADR-0017), straż czasu OCR (ADR-0018, T16, T17, T19), rachunek z kodem kraju (T15), NIP z myślnikami (ADR-0019, T18), TED jako nowy typ i README „jak dodać nowy typ” (T21, ADR-0020), GUI na VM http://20.215.209.150:8080 i kreator typu (ADR-0021, T22), repozytorium publiczne, bez LLM (ADR-0022).

Plan od 22.11 03:30 (połączony nocny plan etapów z planem VM; punkty nocnego planu, które wypadły przy przejściu na VM, wróciły jako 2–4):

| # | Kto | Co | Dlaczego |
|---|---|---|---|
| 1 | Claude + Użytkownik | **zrobione 22.11 03:55** (52 PDF: 10 spraw, 6 skanów, 14 obcych z pustym i uszkodzonym; po `sudo reboot`, z `sudo`: 52/52 JSON, obce `{}`, F1 0.9974, 104 s; GUI wstaje samo; poprawiony kod wyjścia, T7) Test na VM dokładnie jak UZP (`data/uzp/VM.md`, wymaganie 4): kilka PDF w `input/`, czyste `output/`, komenda z `RUN.md` z `sudo` (użytkownik), sprawdzenie JSON, to samo po `sudo reboot`; na koniec `input/` i `output/` puste. Powtórzyć po ostatniej zmianie | bez tego nie ma oceny |
| 2 | Claude | **zrobione** (T23, ADR-0023: odpowiedź na odwołanie, przystąpienie, SWZ, umowa, faktura, wezwanie -> `{}`; 476 prawdziwych bez zmian) Obce dokumenty poza TED (nocny plan, pkt 9): wyroki KIO, faktury, ogłoszenia BZP -> `{}` | wyrok KIO ma „Odwołujący”, „Zamawiający”, „odwołanie”: ryzyko JSON zamiast `{}` |
| 3 | Claude | **zrobione** (T24, ADR-0024: `format: mianownik`, Morfeusz2 BSD; „adwokatowi”, „radcy prawnemu”; F1 bez zmian) Mianownik imion i nazwisk (nocny plan, pkt 7): reguły albo Morfeusz2 | wymaganie UZP; w danych treningowych odmian nie ma, F1 tego nie pokazuje |
| 4 | Claude | **zrobione** (T25, ADR-0025: podpisujący i nagłówki stron w sklejonych liniach, `nowa_linia`; warianty 0.9798 -> 0.9870, treningowe 0.9990 i skany 0.9508 bez zmian) Bramka w środku linii (nocny plan, pkt 3): adres, „KRS:”, e-mail za wartością | `laczenie_linii` 0.851, najsłabszy wariant |
| 5 | Claude | **zrobione** Dokumenty zgodne ze stanem (`docs/kryteria.md`: nieaktualne „brak instrukcji dla jury”, „plan, pkt 7”), STAN | porządek |
| 6 | Claude | **zrobione 22.11 05:30, czeka na uwagi użytkownika** (T26, ADR-0026: trzy kroki, przyciski „Pokaż na przykładzie”, nazwa typu i status zwykłymi słowami, szczegóły w zwiniętych blokach; kreator: nazwa pola + wartość z dokumentu, etykietę i rodzaj znajduje sam i sprawdza na przykładzie; typ z kreatora od razu w pierwszej zakładce; GUI na VM uruchomione ponownie) GUI przyjazne dla użytkownika. Przykład sprawy tylko, gdy jest `data/uzp` (na VM nie ma) | prezentacja |
| 7 | [Argon] | Prezentacja PDF <= 10 MB wg ADR-0006; Regulamin: wskazać rozwiązania zewnętrzne (RapidOCR, pypdfium2, pypdf, Morfeusz2, Streamlit, PyYAML, uv) | |
| 8 | Claude | Ostatni test na VM jak UZP po ostatniej zmianie kodu (pkt 1), `input/` i `output/` puste; dostęp do VM do 11:00 | |

Uwagi 22.11 w nocy: na 2 rdzeniach z 2 wątkami OCR odwołanie (5 stron) 23 s, pełnomocnictwo i przelew ok. 4 s; z 16 wątkami na 2 rdzeniach 3 min (stąd wątki = rdzenie). CI Ubuntu 4 vCPU: 226 PDF UZP w 3 min 56 s. `.PDF` wielkimi (T20). Analiza Argona: `docs/badania/braki-i-ryzyka.md` (dalej do rozważenia: etykieta „w dniu” dla `data_operacji`, GUI na VM jako usługa na porcie 8080).

Decyzje użytkownika 22.11 w nocy: kreatora typu nie rozbudowujemy (kilka przykładów, wykrywanie etykiet z dokumentu, podpowiedzi w polach); znane słabe strony: puste pola bez przykładów, „wspólne wykluczenia” to żargon, nie wiadomo, co wpisać w tabeli. LLM nie używamy (ADR-0022).

Odłożone: wektory etykiet (etap 6, `docs/badania/wektory-etykiet.md`): na 2 vCPU z limitem czasu i bez zysku na znanych etykietach ryzyko większe niż zysk; opis w prezentacji. Słownik sjp.pl, Morfeusz. Przybliżone dopasowanie etykiet OCR (`RapidFuzz`, hipoteza 7 w `docs/badania/hipotezy-70-podejsc.md`, plik poza git): zmienia ekstrakcję tuż przed oddaniem, ryzyko dla F1.

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
