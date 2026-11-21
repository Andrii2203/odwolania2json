# Za co są punkty i co mamy (2026-11-21)

Źródła: `data/uzp/README.md` (UZP), FAQ 1.0 i Discord (`docs/UZP/`).

## Ocena

| Etap | Co | Waga | Mamy |
|---|---|---|---|
| Preselekcja | F1 na ukrytym zbiorze testowym (co najmniej 10 spraw) | 100% | treningowe 0.9990 (reguły dopasowane do nich), skany ok. 0.94 (też już dopasowane); brak nietkniętego zbioru do uczciwej oceny |
| Finał (top 3) | F1 | 50% | jak wyżej |
| Finał | Elastyczność: nowe typy i pola przez konfigurację, bez zmiany kodu | 50% | nowy typ = plik YAML; brak instrukcji i przykładu dla jury |
| ? | Punkty LLM wg średniej liczby parametrów: <=8B 20, 8–14B 18, 14–32B 12, 32–70B 8, 70–150B 4, >150B 0 | ? | LLM nie używamy; pytanie do UZP: ile punktów bez LLM i do której części oceny to wchodzi |
| dodatkowo | GUI: wgranie PDF, analiza, podgląd JSON obok dokumentu | plus | `gui.bat`, Streamlit, widok obok siebie |
| premiowane | Transparentność procesu ekstrakcji | plus | brak: nie widać, skąd wzięła się wartość |

## Wymagania (muszą być)

| Wymaganie | Mamy |
|---|---|
| Python 3.13+, `requirements.txt` | tak |
| Tylko open source, bez GPU | tak |
| CLI / `start.bat`, `input/` -> `output/`, te same nazwy | tak |
| Instrukcja uruchomienia CLI | brak `README.md` |
| Klasyfikacja po treści, nie po nazwie pliku | tak (T1) |
| PDF z tekstem i skany (OCR) | tak (T9) |
| Brak wartości: `null`, niczego nie wymyślamy | tak |
| Imiona i nazwiska w mianowniku | tak w danych; dopełniacz po „radcy prawnego” możliwy w ukrytych |
| Obcy dokument: „pusty plik .json” (README UZP od 21.11 12:14) | brak: nie tworzymy pliku (T2). Na stoisku: klucze z pustymi wartościami. Pytanie: klucze którego typu? |
| LLM tylko przez API firmy z polityką prywatności, serwer w UE/EOG; klucz w zgłoszeniu | nie używamy LLM |

## Zgłoszenie

| Co | Mamy |
|---|---|
| Tytuł projektu | Odwołania2JSON |
| Link do GitHub (działający prototyp) | repozytorium prywatne, trzeba upublicznić przed 11:00 |
| Opcjonalnie: dokumentacja techniczna z opisem LLM | ADR, `docs/`; brak jednego opisu dla jury |
| Opcjonalnie: wyniki własnych testów jakości | `tools/ocena_f1.py`; brak raportu |
