# Za co są punkty i co mamy (2026-11-22, 03:00)

Źródła: `data/uzp/README.md` (UZP), FAQ 1.0 i Discord (`docs/UZP/`).

## Ocena

| Etap | Co | Waga | Mamy |
|---|---|---|---|
| Preselekcja | F1 na ukrytym zbiorze testowym (co najmniej 10 spraw) | 100% | treningowe 0.9990 i skany 0.9508 (reguły do nich dopasowane); warianty dokumentów 0.9798 (`tools/warianty.py`, ADR-0011), najbliżej oceny na nowych dokumentach |
| Finał (top 3) | F1 | 50% | jak wyżej |
| Finał | Elastyczność: nowe typy i pola przez konfigurację, bez zmiany kodu | 50% | nowy typ = plik YAML; przykład na prawdziwych dokumentach: ogłoszenie TED (`docs/przyklady/ogloszenie_ted.yaml`, ADR-0020), F1 0.9902 na 188 ogłoszeniach, których reguły nie widziały, przełącznik i edycja YAML w GUI; kreator nowego typu w GUI bez wyrażeń regularnych (ADR-0021); GUI dla jury: http://20.215.209.150:8080; w YAML także reguły walidacji (`format`, `utnij`) i mapowanie z innych dokumentów sprawy (`kontekst`); UZP (Discord) liczy też konfigurację reguł rozpoznawania, walidacji i mapowania pól; brak instrukcji i przykładu dla jury |
| ? | Punkty za model (README UZP: zasady jeszcze zmieniane; „modele wyłącznie lokalnie, w oczekiwanym czasie: 20 pkt”) | ? | LLM nie używamy (GLiNER2 sprawdzony i odrzucony, `docs/badania/gliner2.md`); pytanie do UZP: ile punktów bez LLM i do której części oceny to wchodzi |
| dodatkowo | GUI: wgranie PDF, analiza, podgląd JSON obok dokumentu | plus | `gui.bat` / `gui.sh`, Streamlit: pliki jako jedna sprawa, widok obok siebie, tabela „Skąd każda wartość”, ręczna poprawka JSON, pobieranie JSON i ZIP |
| premiowane | Transparentność procesu ekstrakcji | plus | dziennik: dla każdego pola reguła z YAML i fragment tekstu (`--wyjasnij`, GUI, T12); bramka i kontekst sprawy też w dzienniku |

## Wymagania (muszą być)

| Wymaganie | Mamy |
|---|---|
| Python 3.13+, `requirements.txt` | tak |
| Tylko open source, bez GPU | tak |
| CLI / `start.bat`, `input/` -> `output/`, te same nazwy | tak |
| Instrukcja uruchomienia CLI | `README.md`, `RUN.md` |
| Klasyfikacja po treści, nie po nazwie pliku | tak (T1) |
| PDF z tekstem i skany (OCR) | tak (T9) |
| Brak wartości: `null`, niczego nie wymyślamy | tak |
| Imiona i nazwiska w mianowniku | tak w danych treningowych; odmiany (np. „Mateuszowi Szymańskiemu”) nie zamieniamy jeszcze na mianownik: plan, pkt 7 w `STAN.md` |
| Obcy dokument: plik JSON z `{}` (Discord UZP) | tak, także pusty i uszkodzony PDF (T2, T7, ADR-0013) |
| LLM tylko przez API firmy z polityką prywatności, serwer w UE/EOG; klucz w zgłoszeniu | nie używamy LLM (ADR-0022) |
| Rachunek jak w dokumencie, z kodem kraju, bez spacji (Discord UZP) | tak (T11, T15, ADR-0014) |
| 150 PDF w 45 min na maszynie UZP (2 vCPU, `data/uzp/VM.md`) | na maszynie UZP 226 PDF (w tym 30 skanów) w 5 min 36 s; JSON zaraz po każdym dokumencie, limit OCR, 3 pierwsze strony skanu i ostatnia (ADR-0018) |

## Zgłoszenie

| Co | Mamy |
|---|---|
| Tytuł projektu | Odwołania2JSON |
| Link do GitHub (działający prototyp) | repozytorium publiczne; rozwiązanie zainstalowane na maszynie UZP (`/opt/solution`, ADR-0017) |
| Opcjonalnie: dokumentacja techniczna z opisem LLM | `README.md` (bez LLM; OCR lokalnie), ADR, `docs/` |
| Opcjonalnie: wyniki własnych testów jakości | tabela „Jakość” w `README.md`; `tools/ocena_f1.py`, `tools/warianty.py`; obce TED: 250/250 dają `{}` |
