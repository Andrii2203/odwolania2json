# Odwołania2JSON

HackNation 2026, zadanie Urzędu Zamówień Publicznych. Program czyta dokumenty PDF sprawy odwoławczej do KIO i dla każdego zapisuje plik JSON.

```
input/sprawa1/odwolanie.pdf        ->  output/sprawa1/odwolanie.json
input/sprawa1/pelnomocnictwo.pdf   ->  output/sprawa1/pelnomocnictwo.json
input/sprawa1/przelew.pdf          ->  output/sprawa1/przelew.json
input/sprawa1/ogloszenie_TED.pdf   ->  output/sprawa1/ogloszenie_TED.json   ({} : dokument spoza klas)
```

Typy: odwołanie, pełnomocnictwo, potwierdzenie przelewu. Brak wartości w dokumencie: `null`. Niczego nie wymyślamy: każda wartość pochodzi z tekstu dokumentu.

## Uruchomienie

| Gdzie | Instalacja (raz) | Uruchomienie |
|---|---|---|
| Linux (maszyna UZP) | `sh instaluj.sh` | `sh uruchom.sh` (komenda z `RUN.md`) |
| Windows | `start.bat` instaluje sam | `start.bat` |
| Podgląd (GUI) | `gui.bat` | przeglądarka: PDF obok JSON i skąd każda wartość |

- Wejście: wszystkie PDF z `input/` (także w podkatalogach, także `.PDF`). Wynik: `output/` z tym samym drzewem katalogów.
- `--wyjasnij`: dla każdego pola reguła z konfiguracji i fragment tekstu, z którego pochodzi wartość.
- Python 3.13+. Zależności: `requirements.txt` (pypdf, pypdfium2, RapidOCR, onnxruntime, PyYAML; licencje BSD, Apache, MIT).

## Jak to działa

Potok etapów (szczegóły: `docs/potok.md`):

1. **Tekst.** Strona z tekstem: `pypdf`. Strona bez tekstu (skan): render (`pypdfium2`) i OCR (RapidOCR, lokalnie na CPU), ramki składane w wiersze. Do OCR idą 3 pierwsze strony i ostatnia.
2. **Klasyfikacja.** Typ ma `znaczniki`; wygrywa typ z największą częścią znaczników w tekście, jeśli przekracza próg. `wykluczenia` odrzucają obce dokumenty (np. ogłoszenia TED). Brak typu: `{}`.
3. **Pola.** Dla każdego pola: etykiety, wzorzec wartości, sekcja dokumentu, format (data ISO, kwota, cyfry, tekst), słownik (słowo -> id).
4. **Bramka.** Wartość kończy się przed następną etykietą, adresem, numerem z etykietą, e-mailem (`utnij`, `stop`).
5. **Kontekst sprawy.** Puste pole może dostać wartość z innego dokumentu tej samej sprawy, ale tylko jeśli ta wartość jest w tekście tego dokumentu.
6. **Zapis.** JSON zaraz po każdym dokumencie. Limit czasu: po `CZAS_OCR_S` nowe skany nie idą do OCR, więc program kończy się w czasie.

Bez LLM i bez wysyłania danych poza komputer. Jedyny model to OCR (RapidOCR, PP-OCRv6 small, ok. 32 MB), uruchamiany lokalnie.

Wszystkie reguły są w `config/`: `config/typy/*.yaml` (jeden plik na typ dokumentu) i `config/ustawienia.yaml` (wspólne wzorce, słowniki i wszystkie liczby, każda z komentarzem, skąd się wzięła). W kodzie nie ma żadnej reguły dla konkretnego typu ani liczby.

## Jak dodać nowy typ dokumentu

Nowy typ to jeden plik YAML. Kod się nie zmienia. Gotowy przykład: [`docs/przyklady/wezwanie.yaml`](docs/przyklady/wezwanie.yaml) (wezwanie wykonawcy do uzupełnienia dokumentów).

1. Skopiuj przykład do `config/typy/wezwanie.yaml`.
2. Wpisz `znaczniki`: słowa, po których program pozna typ (lista w nawiasach = wystarczy jeden wariant).
3. Wpisz `szablon`: kształt JSON, który ma powstać.
4. Dla każdego pola z szablonu wpisz w `pola`:
   - `etykiety`: jak pole jest podpisane w dokumencie (wielkość liter i odstępy bez znaczenia);
   - `wzorce`: jak wygląda wartość; gotowe fragmenty z `config/ustawienia.yaml`: `{DATA}`, `{KWOTA}`, `{RACHUNEK}`, `{NIP_Z_ETYKIETA}`, `{FIRMA}`, `{OSOBA}`, `{SYGNATURA}`, `{TEKST}`;
   - opcjonalnie: `format` (`data`, `liczba`, `cyfry`, `tekst`, `bez_spacji`), `utnij` (gdzie wartość się kończy), `sekcja` (w której części dokumentu szukać), `slownik`, `kontekst` (pole z innego dokumentu sprawy).
5. Uruchom: `start.bat` albo `sh uruchom.sh`. Sprawdź, skąd wzięła się każda wartość: `--wyjasnij` albo GUI.

```yaml
typ: wezwanie
znaczniki: [wezwanie, uzupełnieni, wykonawc, [postępowani, zamówieni]]
szablon:
  Wezwanie: {data: null, miejscowosc: null, numer_postepowania: null, termin: null}
  Wykonawca: {nazwa: null, nip: null}
pola:
  Wezwanie.numer_postepowania:
    etykiety: [znak sprawy, numer postępowania, nr postępowania]
    wzorce: ['({SYGNATURA})']
  Wezwanie.termin:
    etykiety: [w terminie do dnia, w terminie do]
    wzorce: ['({DATA})']
    format: data
  Wykonawca.nip:
    wzorce: ['{NIP_Z_ETYKIETA}']
    format: cyfry
```

Wynik dla „Gdańsk, dnia 12 maja 2026 r. … Znak sprawy: ZP.271.4.2026 … w terminie do dnia 19 maja 2026 r.”:

```json
{"Wezwanie": {"data": "2026-05-12", "miejscowosc": "Gdańsk", "numer_postepowania": "ZP.271.4.2026", "termin": "2026-05-19"},
 "Wykonawca": {"nazwa": "Budex Serwis sp. z o.o.", "nip": "9991234567"}}
```

Ten przykład sprawdza test T21 (`tests/test_konfiguracja.py`).

## Jakość

Miara: F1 po polach JSON, tak jak u UZP (`tools/ocena_f1.py`, `docs/testy.md`).

| Zbiór | F1 |
|---|---|
| 60 spraw treningowych UZP (180 dokumentów) | 0.9990 |
| 30 skanów UZP | 0.9508 |
| 4673 warianty dokumentów treningowych (inne wartości, daty, etykiety, łamanie linii; `tools/warianty.py`) | 0.9798 |
| 160 obcych dokumentów (ogłoszenia TED) | 0 z 160 dostaje JSON z danymi |

Czas: 226 PDF z danych UZP (w tym 30 skanów) w ok. 4 min na Ubuntu 24.04 z 4 vCPU (CI). Dokument cyfrowy to ułamek sekundy, strona skanu kilka sekund.

## Dla zespołu

- `AGENTS.md`: zasady pracy; `docs/adr/`: decyzje; `docs/testy.md`: testy z przykładami; `docs/STAN.md`: stan i plan.
- Testy: `.venv\Scripts\python -m pytest -q`. Hook przed commitem i CI (Windows i Ubuntu) pilnują testów i F1.
