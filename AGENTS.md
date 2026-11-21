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
Obcy dokument (np. ogłoszenie TED) nie daje pliku.

## Wymagania UZP

- Python 3.13+, `requirements.txt`, uruchomienie z CLI (`start.bat`).
- `input/` i `output/` w katalogu głównym; to samo drzewo katalogów, JSON ma tę samą nazwę co PDF.
- Tylko open source. LLM: wyłącznie model z otwartymi wagami przez API dostawcy, którego firma i serwer są w UE (ADR-0004). Klucz API oddajemy razem z rozwiązaniem.
- Komputer testowy jest biurowy, bez GPU. Większość dokumentów to cyfrowe PDF, ale zdarzają się skany (ADR-0007).
- Brak wartości w dokumencie: `null`. Niczego nie wymyślamy.
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
8. Małe commity z krótkim opisem po polsku, push po każdym.

## Mapa

| Ścieżka | Co |
|---|---|
| `odwolania2json/` | kod; CLI: `python -m odwolania2json` |
| `config/typy/*.yaml` | typ dokumentu: `znaczniki` (klasyfikacja), `szablon` (kształt JSON). Nowy typ to nowy plik YAML |
| `tests/` | testy z `docs/testy.md` |
| `tools/ocena_f1.py` | F1 na 60 sprawach treningowych (ADR-0003) |
| `data/uzp/` | klon https://github.com/Urzad-Zamowien-Publicznych/hacknation-2026 (poza git) |
| `docs/adr/`, `docs/badania/`, `docs/testy.md`, `docs/STAN.md` | decyzje, badania, testy, stan |

## Polecenia (Windows)

```
py -3.13 -m venv .venv && .venv\Scripts\pip install -r requirements-dev.txt
git clone https://github.com/Urzad-Zamowien-Publicznych/hacknation-2026 data/uzp
start.bat                                  # input\ -> output\
.venv\Scripts\python -m pytest -q          # testy
.venv\Scripts\python tools\ocena_f1.py     # F1 i najgorsze pola
```

## Role

- Claude: architektura, potok przetwarzania, trudne pola, ADR.
- Gemini (Argon): zadania oznaczone `[Argon]` w `docs/STAN.md`. Zmienia tylko pliki wskazane w zadaniu. ADR i testy tylko po zgodzie użytkownika.
