# Za co są punkty i co mamy (2026-11-22, noc)

Źródła: `data/uzp/README.md` (UZP), FAQ 1.0 i Discord (`docs/UZP/`).

## Ocena

| Etap | Co | Waga | Mamy |
|---|---|---|---|
| Preselekcja | F1 na ukrytym zbiorze testowym (co najmniej 10 spraw) | 100% | treningowe 0.9990 i skany 0.9462 (reguły do nich dopasowane); warianty dokumentów 0.9798 (`tools/warianty.py`, ADR-0011), najbliżej oceny na nowych dokumentach |
| Finał (top 3) | F1 | 50% | jak wyżej |
| Finał | Elastyczność: nowe typy i pola przez konfigurację, bez zmiany kodu | 50% | nowy typ = plik YAML; w YAML także reguły walidacji (`format`, `utnij`) i mapowanie z innych dokumentów sprawy (`kontekst`); UZP (Discord) liczy też konfigurację reguł rozpoznawania, walidacji i mapowania pól; brak instrukcji i przykładu dla jury |
| ? | Punkty LLM wg średniej liczby parametrów: <=8B 20, 8–14B 18, 14–32B 12, 32–70B 8, 70–150B 4, >150B 0 | ? | LLM nie używamy (GLiNER2 sprawdzony i odrzucony, `docs/badania/gliner2.md`); pytanie do UZP: ile punktów bez LLM i do której części oceny to wchodzi |
| dodatkowo | GUI: wgranie PDF, analiza, podgląd JSON obok dokumentu | plus | `gui.bat`, Streamlit, widok obok siebie; tabela „Skąd każda wartość” |
| premiowane | Transparentność procesu ekstrakcji | plus | dziennik: dla każdego pola reguła z YAML i fragment tekstu (`--wyjasnij`, GUI, T12); bramka i kontekst sprawy też w dzienniku |

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
| Imiona i nazwiska w mianowniku | tak w danych treningowych; odmiany (np. „Mateuszowi Szymańskiemu”) nie zamieniamy jeszcze na mianownik: plan, pkt 7 w `STAN.md` |
| Obcy dokument: plik JSON z `{}` (Discord UZP) | tak, także pusty i uszkodzony PDF (T2, T7, ADR-0013) |
| LLM tylko przez API firmy z polityką prywatności, serwer w UE/EOG; klucz w zgłoszeniu | nie używamy LLM |
| Rachunek jak w dokumencie, z „PL” (Discord UZP) | tak (T11, ADR-0014) |
| Ograniczony czas na rozwiązanie (Discord UZP) | cyfrowa sprawa 0,4 s, skan ok. 4 s na stronę; JSON zapisywany po każdej sprawie |

## Zgłoszenie

| Co | Mamy |
|---|---|
| Tytuł projektu | Odwołania2JSON |
| Link do GitHub (działający prototyp) | repozytorium prywatne, trzeba upublicznić przed 11:00 |
| Opcjonalnie: dokumentacja techniczna z opisem LLM | ADR, `docs/`; brak jednego opisu dla jury |
| Opcjonalnie: wyniki własnych testów jakości | `tools/ocena_f1.py`, `tools/warianty.py`, obce TED 0/160; brak jednego raportu |
