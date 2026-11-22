# Za co są punkty i co mamy (2026-11-22, 05:40)

Źródła: `data/uzp/README.md` (UZP), Regulamin i „Pełna treść zadania” (`docs/UZP/`), FAQ 1.0, Discord.

Dokumenty UZP różnią się w finale: Regulamin (§ 2) i README: F1 50%, elastyczność 50%; „Pełna treść zadania” (pkt 8): F1 50%, elastyczność 30%, architektura i jakość techniczna 20% (przejrzystość, modułowość, utrzymanie, dokumentacja). Regulamin: ocena finału na podstawie opisu architektury, kodu i prezentacji; rozwiązania zewnętrzne trzeba wskazać w prezentacji.

## Ocena

| Etap | Co | Waga | Mamy |
|---|---|---|---|
| Preselekcja | F1 na ukrytym zbiorze testowym (co najmniej 10 spraw) | 100% | treningowe 0.9990 i skany 0.9508 (reguły do nich dopasowane); warianty dokumentów 0.9870 (`tools/warianty.py`, ADR-0011), najbliżej oceny na nowych dokumentach |
| Finał (top 3) | F1 | 50% | jak wyżej |
| Finał | Elastyczność: nowe typy i pola przez konfigurację, bez zmiany kodu | 50% | nowy typ = plik YAML; przykład na prawdziwych dokumentach: ogłoszenie TED (`docs/przyklady/ogloszenie_ted.yaml`, ADR-0020), F1 0.9902 na 188 ogłoszeniach, których reguły nie widziały, przełącznik w GUI; kreator nowego typu w GUI bez wyrażeń regularnych: nazwa pola i wartość skopiowana z przykładowego PDF, etykietę i rodzaj kreator znajduje sam i sprawdza na przykładzie, plik YAML do pobrania albo od razu do użycia w GUI (ADR-0021, ADR-0026, T26); GUI dla jury: http://20.215.209.150:8080; w YAML także reguły walidacji (`format`, `utnij`) i mapowanie z innych dokumentów sprawy (`kontekst`); UZP (Discord) liczy też konfigurację reguł rozpoznawania, walidacji i mapowania pól; instrukcja „Jak dodać nowy typ dokumentu” w `README.md` |
| ? | Punkty za model (README UZP: zasady jeszcze zmieniane; „modele wyłącznie lokalnie, w oczekiwanym czasie: 20 pkt”) | ? | LLM nie używamy (GLiNER2 sprawdzony i odrzucony, `docs/badania/gliner2.md`); pytanie do UZP: ile punktów bez LLM i do której części oceny to wchodzi |
| dodatkowo | GUI: wgranie PDF, analiza, podgląd JSON obok dokumentu | plus | `gui.bat` / `gui.sh`, Streamlit: pliki jako jedna sprawa, widok obok siebie, odczytane wartości podświetlone w dokumencie (T27), tabela „Skąd te wartości”, ręczna poprawka JSON, pobieranie JSON i ZIP; przyciski „Pokaż na przykładzie” (ADR-0026) |
| premiowane | Transparentność procesu ekstrakcji | plus | dziennik: dla każdego pola reguła z YAML i fragment tekstu (`--wyjasnij`, GUI, T12); w GUI etykieta i wartość podświetlone na stronie dokumentu, numer jak wiersz dziennika (T27); bramka i kontekst sprawy też w dzienniku |

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
| Imiona i nazwiska w mianowniku | tak: `format: mianownik` (Morfeusz2, słownik SGJP), „Mateuszowi Szymańskiemu” -> „Mateusz Szymański” (T24, ADR-0024) |
| Obcy dokument: plik JSON z `{}` (Discord UZP) | tak, także pusty i uszkodzony PDF (T2, T7, ADR-0013) oraz inne pisma z akt: odpowiedź na odwołanie, przystąpienie, SWZ, umowa, faktura (T23, ADR-0023) |
| LLM tylko przez API firmy z polityką prywatności, serwer w UE/EOG; klucz w zgłoszeniu | nie używamy LLM (ADR-0022) |
| Rachunek jak w dokumencie, z kodem kraju, bez spacji (Discord UZP) | tak (T11, T15, ADR-0014) |
| 150 PDF w 45 min na maszynie UZP (2 vCPU, `data/uzp/VM.md`) | na maszynie UZP 226 PDF (w tym 30 skanów) w 5 min 36 s; test jak UZP (z `sudo`, po restarcie): 52 PDF w 104 s, kod wyjścia 0; JSON zaraz po każdym dokumencie, limit OCR, 3 pierwsze strony skanu i ostatnia (ADR-0018) |

## Zgłoszenie

| Co | Mamy |
|---|---|
| Tytuł projektu | Odwołania2JSON |
| Link do GitHub (działający prototyp) | repozytorium publiczne; rozwiązanie zainstalowane na maszynie UZP (`/opt/solution`, ADR-0017) |
| Opcjonalnie: dokumentacja techniczna z opisem LLM | `README.md` (bez LLM; OCR lokalnie), ADR, `docs/` |
| Opcjonalnie: wyniki własnych testów jakości | tabela „Jakość” w `README.md`; `tools/ocena_f1.py`, `tools/warianty.py`; obce TED: 250/250 dają `{}` |

## Po wygranej (Regulamin § 3)

W 7 dni: umowa przeniesienia praw; kod, instrukcja uruchomienia, konfiguracja Docker Compose, opis architektury, opis konfiguracji ekstrakcji klasy dokumentów i dodania nowej klasy. Docker Compose jeszcze nie mamy.
