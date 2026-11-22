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
- Python 3.13+. Zależności: `requirements.txt` (pypdf, pypdfium2, RapidOCR, onnxruntime, PyYAML, Morfeusz2 ze słownikiem SGJP; licencje BSD, Apache, MIT).

## Jak to działa

Potok etapów (szczegóły: `docs/potok.md`):

1. **Tekst.** Strona z tekstem: `pypdf`. Strona bez tekstu (skan): render (`pypdfium2`) i OCR (RapidOCR, lokalnie na CPU), ramki składane w wiersze. Do OCR idą 3 pierwsze strony i ostatnia.
2. **Klasyfikacja.** Typ ma `znaczniki`; wygrywa typ z największą częścią znaczników w tekście, jeśli przekracza próg. `wykluczenia` odrzucają obce dokumenty (np. ogłoszenia TED). Brak typu: `{}`.
3. **Pola.** Dla każdego pola: etykiety, wzorzec wartości, sekcja dokumentu, format (data ISO, kwota, cyfry, tekst, imię i nazwisko w mianowniku przez Morfeusz2), słownik (słowo -> id).
4. **Bramka.** Wartość kończy się przed następną etykietą, adresem, numerem z etykietą, e-mailem (`utnij`, `stop`).
5. **Kontekst sprawy.** Puste pole może dostać wartość z innego dokumentu tej samej sprawy, ale tylko jeśli ta wartość jest w tekście tego dokumentu.
6. **Zapis.** JSON zaraz po każdym dokumencie. Limit czasu: po `CZAS_OCR_S` nowe skany nie idą do OCR, więc program kończy się w czasie.

Bez LLM i bez wysyłania danych poza komputer. Jedyny model to OCR (RapidOCR, PP-OCRv6 small, ok. 32 MB), uruchamiany lokalnie.

Wszystkie reguły są w `config/`: `config/typy/*.yaml` (jeden plik na typ dokumentu) i `config/ustawienia.yaml` (wspólne wzorce, słowniki i wszystkie liczby, każda z komentarzem, skąd się wzięła). W kodzie nie ma żadnej reguły dla konkretnego typu ani liczby.

## Jak dodać nowy typ dokumentu

Nowy typ to jeden plik YAML. Kod się nie zmienia. Pliku nie trzeba pisać ręcznie:

**Kreator w GUI** (zakładka „Kreator nowego typu”): wgraj przykładowy PDF, wpisz nazwę typu i słowa, po których go rozpoznać, a w tabeli pola: nazwę pola JSON (np. `Nabywca.nazwa`), etykietę z dokumentu (np. „Oficjalna nazwa”) i rodzaj z listy (data, kwota, NIP, rachunek, nazwa firmy, tekst do końca linii, ...). Kreator od razu pokazuje JSON z przykładu i skąd każda wartość, a plik typu daje do pobrania: wystarczy zapisać go w `config/typy/`. Lista rodzajów jest w `config/ustawienia.yaml` (`kreator.rodzaje`).

**Ręcznie**, gdy potrzeba więcej (pole bez etykiety, sekcja dokumentu, lista): gotowy przykład na prawdziwych dokumentach: [`docs/przyklady/ogloszenie_ted.yaml`](docs/przyklady/ogloszenie_ted.yaml), ogłoszenie w Dzienniku Urzędowym UE (TED).

1. Skopiuj plik do `config/typy/` (albo do kopii `config/` i uruchom z `--config <katalog>`).
2. `znaczniki`: słowa, po których program pozna typ (lista w nawiasach = wystarczy jeden wariant).
3. `szablon`: kształt JSON, który ma powstać.
4. Dla każdego pola z szablonu w `pola`:
   - `etykiety`: jak pole jest podpisane w dokumencie (wielkość liter i odstępy bez znaczenia);
   - `wzorce`: jak wygląda wartość; gotowe fragmenty z `config/ustawienia.yaml`: `{DATA}`, `{KWOTA}`, `{RACHUNEK}`, `{NIP_Z_ETYKIETA}`, `{FIRMA}`, `{OSOBA}`, `{SYGNATURA}`, `{TEKST}`; własne fragmenty typu w `wzorce` pliku typu;
   - opcjonalnie: `format` (`data`, `liczba`, `cyfry`, `tekst`, `bez_spacji`, `mianownik`), `sekcja` (w której części dokumentu szukać), `utnij` (gdzie wartość się kończy), `slownik`, `kontekst` (pole z innego dokumentu sprawy).
   - w typie opcjonalnie `nowa_linia`: wzorce miejsc, w których przed wyciąganiem pól wstawiana jest nowa linia (nagłówek w środku linii, ADR-0025).
5. Uruchom i sprawdź, skąd wzięła się każda wartość: `--wyjasnij` w CLI albo tabela w GUI. W GUI przykład TED włącza się przełącznikiem w panelu bocznym.

Fragment przykładu:

```yaml
typ: ogloszenie_ted
znaczniki: [see the notice, oficjalna nazwa, nabywca, numer rejestracyjny, role tej organizacji]
wspolne_wykluczenia: false        # wspólne wykluczenia (wyrok KIO, TED) tego typu nie dotyczą
szablon:
  OgloszenieTED: {numer: null, data_publikacji: null, cpv: null}
  Nabywca: {nazwa: null, numer_rejestracyjny: null, miejscowosc: null}
pola:
  OgloszenieTED.data_publikacji:
    wzorce: ['OJ\s+S\s+\S+\s+({DATA})']
    format: data
  OgloszenieTED.cpv:
    etykiety: [główna klasyfikacja (cpv)]
    wzorce: [':[ \t]*(\d+)']
  Nabywca.miejscowosc:
    etykiety: [miejscowość]
    wzorce: [':{WARTOSC}']
    sekcja: '{ORGANIZACJA_NABYWCY}'   # blok organizacji z rolą „Nabywca”
```

Wynik dla ogłoszenia 100-2026:

```json
{"OgloszenieTED": {"numer": "100-2026", "data_publikacji": "2026-01-02", "cpv": "24111900"},
 "Nabywca": {"nazwa": "Miejskie Przedsiębiorstwo Wodociągów i Kanalizacji w m. st. Warszawie S.A.",
             "numer_rejestracyjny": "5250005662", "miejscowosc": "Warszawa"}}
```

Jak sprawdziliśmy, że to działa: 250 prawdziwych ogłoszeń z API TED; poprawne wartości z danych TED (nie z naszego odczytu PDF). Reguły pisane na 62 ogłoszeniach, pomiar na pozostałych 188, których reguły nie widziały: typ rozpoznany 188/188, **F1 0.9902**. Przykład nie leży w `config/typy/`, bo w ocenie UZP ogłoszenie TED to dokument spoza klas: z domyślną konfiguracją wszystkie 250 dają `{}`. Test T21 (`tests/test_konfiguracja.py`) sprawdza oba przypadki.

## Jakość

Miara: F1 po polach JSON, tak jak u UZP (`tools/ocena_f1.py`, `docs/testy.md`).

| Zbiór | F1 |
|---|---|
| 60 spraw treningowych UZP (180 dokumentów) | 0.9990 |
| 30 skanów UZP | 0.9508 |
| 4673 warianty dokumentów treningowych (inne wartości, daty, etykiety, łamanie i sklejanie linii; `tools/warianty.py`) | 0.9870 |
| Nowy typ z samego YAML: 188 ogłoszeń TED, których reguły nie widziały | 0.9902 |
| 250 obcych dokumentów (ogłoszenia TED) | wszystkie dają `{}` |

Czas: 226 PDF z danych UZP (w tym 30 skanów) w ok. 4 min na Ubuntu 24.04 z 4 vCPU (CI). Dokument cyfrowy to ułamek sekundy, strona skanu kilka sekund.

## Dla zespołu

- `AGENTS.md`: zasady pracy; `docs/adr/`: decyzje; `docs/testy.md`: testy z przykładami; `docs/STAN.md`: stan i plan.
- Testy: `.venv\Scripts\python -m pytest -q`. Hook przed commitem i CI (Windows i Ubuntu) pilnują testów i F1.
