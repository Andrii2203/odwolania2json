# ADR-0002: Potok przetwarzania i typy dokumentów w konfiguracji

Status: przyjęte, 2026-11-21

## Kontekst

Trzeba sklasyfikować PDF, wyodrębnić pola i zapisać JSON. W finale 50% oceny to możliwość dodania nowego typu dokumentu bez zmiany kodu.

## Decyzja

```
PDF -> tekst -> typ -> pola -> JSON
```

Przykład: `potwierdzenie_przelewu.pdf` -> tekst „POLECENIE PRZELEWU … Kwota 200,00 zł” -> typ `przelew` (znalezione 2 z 2 znaczników) -> `kwota: 200.0` -> `output/case1/potwierdzenie_przelewu.json`.

1. Tekst: `pypdf` (BSD, lekka, bez modeli). Skany: ADR-0007.
2. Typ: `config/typy/<typ>.yaml` zawiera listę `znaczniki`. Znacznik to słowo albo lista synonimów (wystarczy jeden z nich). Tekst i znaczniki porównujemy bez wielkości liter i spacji, więc „P E Ł N O M O C N I C T W O” też jest znajdowane. Wynik to odsetek znalezionych znaczników. Wybieramy typ z najwyższym wynikiem, jeśli jest co najmniej równy `prog`; w przeciwnym razie dokument jest obcy i plik nie powstaje. Lista `wykluczenia`: jeśli w tekście jest którekolwiek z tych słów, typ odpada. Przykład: wyrok KIO zawiera „orzeka”, a żadne z 60 odwołań treningowych go nie zawiera. Słowa dobieramy skryptem na danych (`data/uzp/dane/negatywne/`).
3. Pola: najpierw reguły, LLM tylko dla tego, czego reguły nie wyciągną (ADR-0004). Reguła pola w YAML to `etykiety` i `format`: szukamy pierwszej etykiety z listy i bierzemy najbliższą wartość w tym formacie (`rachunek`, `kwota`, `data`, `identyfikator`, `tekst`). Przykład: „Rachunek nadawcy: 37 8692 8950 …” daje `"z_rachunku": "37869289508384042119046312"`. Formaty są w kodzie (`odwolania2json/pola.py`), etykiety w YAML, więc nowy bank lub nowy typ dokumentu to zmiana konfiguracji.
4. JSON: kształt z `szablon` w tym samym pliku YAML; czego nie znaleziono, to `null`, listy są puste.

Nowy typ dokumentu to nowy plik `config/typy/<typ>.yaml`. Kod się nie zmienia.

## Rozważane warianty

- Docling (MIT): dobry rozbiór PDF i OCR, ale ciągnie PyTorch i modele (gigabajty); ryzykowne na komputerze biurowym.
- Wszystko przez LLM: drożej, wolniej, niedeterministycznie, tylko dostawca z UE.

## Konsekwencje

- Większość pól (NIP, KRS, rachunki, daty) wyciągamy deterministycznie i bez kosztów.
- Klasyfikację i kształt JSON ustawiamy w YAML; jakość klasyfikacji pokazuje `tools/ocena_f1.py`.
