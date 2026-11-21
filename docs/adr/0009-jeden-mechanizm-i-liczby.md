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
4. `{STOP}` to etykiety pozostałych pól typu i lista `stop`. Tekst kończy się przed linią, która zaczyna się taką etykietą. Wartość równa takiej etykiecie jest pomijana: to nagłówek tabeli („Data Opis Kwota”), nie wartość (T10).
5. Wszystkie liczby są w `config/ustawienia.yaml`: sekcja `liczby` i fragmenty `wzorce`. Przy każdej jest komentarz: standard (NRB: 26 cyfr) albo pomiar `tools/przeglad.py`. `prog` i wspólne `wykluczenia` są jedne dla wszystkich typów.
6. Test T5 pilnuje: w `config/typy/` nie ma cyfr, w kodzie są tylko 0 i 1, każda liczba w `ustawienia.yaml` ma komentarz.
7. To samo dotyczy `tools/` i `tests/` (2026-11-21). Liczby narzędzi są w sekcji `narzedzia`. Liczby z protokołów i wzorów zastępuje nazwa z API: `{"decision": "block"}` zamiast kodu wyjścia 2 w hookach Claude, `harmonic_mean` zamiast wzoru F1, `git rev-parse --show-toplevel` zamiast `parents[2]`, `unicodedata` zamiast zakresu kodów cyrylicy. T5 łapie też liczby w formatach f-stringów (`{f1:.3f}`) i we wzorcach regex w kodzie (`\d{4}`).
8. Komentarz przy liczbie z pomiaru podaje regułę wyboru i polecenie pomiaru, bez wyników (2026-11-21). Wyniki się starzeją: po nowych regułach F1 0.571 -> 0.999, a komentarze dalej pokazywały 0.571.

   ```yaml
   # Najmniejsze okno bez spadku F1 (tools/przeglad.py OKNO_WARTOSCI 40 60 120 240 500).
   OKNO_WARTOSCI: 120
   ```

9. Znaki, które są regułą o dokumencie, też są w `ustawienia.yaml` (2026-11-21): `obcinane_po_bramce` (końcówka nazwy po bramce `utnij`), `separatory_dziesietne` (grosze w `format: liczba`), `ROZDZIELNIK_CYFR` (odstęp albo myślnik w znanym numerze: kontekst sprawy i `tools/warianty.py`, wcześniej dwa różne wzorce w kodzie). W kodzie zostają tylko wzorce ogólne (`\s+`, `\D`, składnia `{NAZWA}`). Tego T5 nie sprawdza; sprawdza przegląd kodu.

## Konsekwencje

- Wynik na 180 dokumentach treningowych jest bajt w bajt taki sam jak przed zmianą; F1 0.571.
- Nowy typ, także z nowym rodzajem numeru (np. PESEL), to plik YAML i ewentualnie fragment w `ustawienia.yaml`.
- `--config` wskazuje katalog `config/` (z `ustawienia.yaml` i `typy/`), więc można podać inną konfigurację bez zmiany kodu.
- Nowy sposób zamiany wartości (np. kwota słownie) nadal wymaga funkcji w `FORMATY` w `odwolania2json/pola.py`.
