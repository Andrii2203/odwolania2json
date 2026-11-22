# Odwołania2JSON – kontekst dla AI (Claude i Gemini/Argon)

HackNation 2026, zadanie UZP „Odwołania2JSON”. Termin oddania: niedziela 22.11.2026, 11:00.
Z użytkownikiem rozmawiamy po ukraińsku, na przykładach.
Wszystko, co trafia do repozytorium (kod, dokumentacja, commity), piszemy po polsku, prostym językiem, bez ozdobników.

## Co robimy

Program bierze dokumenty PDF sprawy odwoławczej do KIO i dla każdego zapisuje JSON.

```
input/case1/odwolanie.pdf  ->  output/case1/odwolanie.json
{"OdwolanieKIO": {"miejscowosc": "Kraków", ...}, "Odwolujacy": [{"nip": "9995519382", ...}], ...}
```

Typy: `odwolanie`, `pelnomocnictwo`, `przelew` (potwierdzenie przelewu).
Obcy, pusty albo uszkodzony dokument (np. ogłoszenie TED) daje plik z `{}` (ADR-0013).

## Wymagania UZP

- Python 3.13+, `requirements.txt`, uruchomienie z CLI (`start.bat`; na maszynie UZP `sh instaluj.sh`, potem komenda z `RUN.md`, ADR-0017).
- Ocena na maszynie UZP (`data/uzp/VM.md`): Ubuntu 24.04, 2 vCPU, bez GPU; 150 PDF w 45 min; dostęp do maszyny do 22.11 11:00.
- `input/` i `output/` w katalogu głównym; to samo drzewo katalogów, JSON ma tę samą nazwę co PDF.
- Tylko open source. LLM: wyłącznie model z otwartymi wagami przez API firmy, która w polityce prywatności podaje zakres i miejsce przetwarzania, z serwerem w UE/EOG; hosting przez osobę prywatną zabroniony (ADR-0004). Klucz API oddajemy razem z rozwiązaniem.
- Komputer testowy jest biurowy, bez GPU. Większość dokumentów to cyfrowe PDF, ale zdarzają się skany (ADR-0007, przykłady w `data/uzp/dane/skany/`).
- Brak wartości w dokumencie: `null`. Niczego nie wymyślamy. Imiona i nazwiska w mianowniku („Mateusz Szymański”, nie „Mateusza Szymańskiego”).
- Ocena: F1 na ukrytych sprawach (co najmniej 10). Finał (top 3): 50% F1, 50% dodawanie nowych typów dokumentów przez konfigurację, bez zmiany kodu.
- Pełne warunki: `docs/UZP/` (tylko lokalnie, poza git).

## Jak pracujemy

1. Najpierw gotowe rozwiązanie (open source, najlepiej MIT/BSD/Apache). Jeśli z dużej biblioteki potrzebna jest mała część, piszemy własne.
2. Nie sprawdzamy ręcznie tego, co sprawdza narzędzie: testy (`pytest`), jakość (`tools/ocena_f1.py`).
3. Każda decyzja ma ADR w `docs/adr/` (kontekst, decyzja, konsekwencje; krótko).
4. TDD: opis testu z przykładem w `docs/testy.md`, czerwony test, kod, zielony test. Minimum testów, każdy odpowiada punktowi w `docs/testy.md`.
5. Oszczędzamy tokeny: czytamy tylko potrzebne pliki i fragmenty, bez subagentów, krótkie odpowiedzi.
6. Na koniec sesji aktualizujemy `docs/STAN.md` (zrobione, dalej, pytania).
7. W kodzie bez komentarzy; jeśli komentarz jest konieczny, po polsku. Komunikaty CLI po polsku.
8. Małe commity z krótkim opisem po polsku: `sh tools/zapisz.sh "opis" pliki...` (commit, push i aktualizacja maszyny UZP, jeśli w `.env` są `VM_SSH` i `VM_KLUCZ`).
9. Wszystkie liczby (progi, limity, okna, czasy, DPI) tylko w `config/ustawienia.yaml`, każda z komentarzem, skąd się wzięła: standard albo reguła wyboru z poleceniem `tools/przeglad.py` (bez wyników pomiaru, bo się starzeją). W plikach typów i w kodzie liczb nie ma (test T5, ADR-0009).

## Automatyczne straże

| Kiedy | Co sprawdza | Gdzie |
|---|---|---|
| każdy commit (każdy wykonawca) | testy zielone, w tym F1 nie niższe niż `MIN_F1` (T8); brak cyrylicy | `.githooks/pre-commit` |
| Claude edytuje `tests/` | czy najpierw zmieniono `docs/testy.md` | `tools/hooks/straz_testow.py` |
| Claude kończy turę | testy zielone przy zmianach w kodzie; wysyła zaległe commity | `tools/hooks/stop.py` |
| push na GitHub | testy i F1 na czystym Windows z Pythonem 3.13; instalacja, testy i uruchomienie jak na maszynie UZP (Ubuntu 24.04, ADR-0017) | `.github/workflows/testy.yml` |

## Mapa

| Ścieżka | Co |
|---|---|
| `odwolania2json/` | kod; CLI: `python -m odwolania2json` |
| `config/typy/*.yaml` | typ dokumentu: `znaczniki` (klasyfikacja), `szablon` (kształt JSON), `pola` (`etykiety`, `wzorce` z opcjonalnymi `wartosc` i `sekcja`, `format`, `sekcja`, `slownik`, `podzial`, `utnij`), `wzorce` (fragmenty typu), `kontekst` (pole z innego dokumentu sprawy). Nowy typ to nowy plik YAML |
| `docs/przyklady/` | przykład nowego typu na prawdziwych dokumentach (`ogloszenie_ted.yaml`, T21, ADR-0020); poza `config/typy/`, bo w ocenie UZP TED to `{}`. Dane: `tools/pobierz_obce.py` -> `data/przyklad_ted/{rozwoj,pomiar}` |
| `config/ustawienia.yaml` | wszystkie liczby, wspólne wzorce, słowniki; dla OCR `warianty_liter` (ł pasuje też do l) i `poprawki_ocr` |
| `odwolania2json/ocr.py` | strona bez tekstu: render (`pypdfium2`), RapidOCR, ramki w wiersze (ADR-0007) |
| `tests/` | testy z `docs/testy.md` |
| `tools/ocena_f1.py` | F1 na 60 sprawach treningowych (ADR-0003) |
| `tools/warianty.py`, `tools/pobierz_obce.py` | F1 na wariantach dokumentów; obce PDF z TED do `data/obce` (ADR-0011) |
| `tools/przeglad.py` | F1 dla kilku wartości jednej liczby z `config/ustawienia.yaml` (pochodzenie liczb) |
| `data/uzp/` | klon https://github.com/Urzad-Zamowien-Publicznych/hacknation-2026 (poza git) |
| `docs/potok.md` | etapy potoku, zasady i stan każdego etapu (ADR-0012) |
| `docs/adr/`, `docs/badania/`, `docs/testy.md`, `docs/STAN.md`, `docs/kryteria.md` | decyzje, badania, testy, stan, za co punkty UZP i co mamy |

## Polecenia (Windows)

```
py -3.13 -m venv .venv && .venv\Scripts\pip install -r requirements-dev.txt
git clone https://github.com/Urzad-Zamowien-Publicznych/hacknation-2026 data/uzp
start.bat                                  # input\ -> output\
.venv\Scripts\python -m pytest -q          # testy
.venv\Scripts\python tools\ocena_f1.py     # F1 i najgorsze pola
.venv\Scripts\python tools\ocena_f1.py --dane data\uzp\dane\skany\potwierdzenia data\uzp\dane\skany\pelnomocnictwa data\uzp\dane\skany\odwolania   # skany, ok. 4 min
.venv\Scripts\python tools\warianty.py --przyklady   # F1 na wariantach, ok. 40 s
.venv\Scripts\python tools\pobierz_obce.py && .venv\Scripts\python tools\ocena_f1.py --dane data\obce   # obce: ma być 0 z JSON
.venv\Scripts\python tools\przeglad.py OKNO_WARTOSCI 60 120 240   # F1 dla kilku wartości
```

## Role

- Claude: architektura, potok przetwarzania, trudne pola, ADR.
- Gemini (Argon): zadania oznaczone `[Argon]` w `docs/STAN.md`. Zmienia tylko pliki wskazane w zadaniu. ADR i testy tylko po zgodzie użytkownika.
