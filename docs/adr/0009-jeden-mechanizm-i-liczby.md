# ADR-0009: Jeden mechanizm pól, wszystkie liczby w `config/ustawienia.yaml`

Status: przyjęte, 2026-11-21

## Kontekst

Pola były wyciągane na dwa sposoby: `etykiety` + `format` (wyrażenia regularne w kodzie, ADR-0002) i `wzorce` (wyrażenia w YAML, ADR-0008). Nowy format wartości wymagał zmiany kodu, a w finale liczy się dodawanie typów samą konfiguracją. Liczby leżały w 4 plikach (`prog` 3 razy ten sam) i nie miały zapisanego pochodzenia.

## Decyzja

1. Jeden mechanizm: `wzorce`. `etykiety` to skrót: każda etykieta staje przed każdym wzorcem, razem z `{PO_ETYKIECIE}`.

   ```yaml
   przelew_bankowy.kwota:
     etykiety: [kwota, wartość]
     wzorce: ['({KWOTA})']
     format: liczba
   ```

   „WARTOŚĆ ........ 200,00 zł” daje `200.0`.
2. Pole bez `[]`: wygrywa pierwsza etykieta i pierwszy wzorzec z trafieniem (kolejność w YAML). Pole z `[]`: kolejność w tekście (ADR-0008).
3. `format` tylko zamienia znaleziony tekst: `cyfry`, `liczba`, `data`, `tekst`. Gdzie szukać, mówią wzorce w YAML.
4. `{STOP}` to etykiety pozostałych pól typu i lista `stop`. Tekst kończy się przed linią, która zaczyna się taką etykietą.
5. Wszystkie liczby są w `config/ustawienia.yaml`: sekcja `liczby` i fragmenty `wzorce`. Przy każdej jest komentarz: standard (NRB: 26 cyfr) albo pomiar `tools/przeglad.py`. `prog` i wspólne `wykluczenia` są jedne dla wszystkich typów.
6. Test T5 pilnuje: w `config/typy/` nie ma cyfr, w kodzie są tylko 0 i 1, każda liczba w `ustawienia.yaml` ma komentarz.

## Konsekwencje

- Wynik na 180 dokumentach treningowych jest bajt w bajt taki sam jak przed zmianą; F1 0.571.
- Nowy typ, także z nowym rodzajem numeru (np. PESEL), to plik YAML i ewentualnie fragment w `ustawienia.yaml`.
- `--config` wskazuje katalog `config/` (z `ustawienia.yaml` i `typy/`), więc można podać inną konfigurację bez zmiany kodu.
- Nowy sposób zamiany wartości (np. kwota słownie) nadal wymaga funkcji w `FORMATY` w `odwolania2json/pola.py`.
