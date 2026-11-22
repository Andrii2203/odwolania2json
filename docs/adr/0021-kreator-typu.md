# ADR-0021: Kreator nowego typu w GUI

Status: przyjęte, 2026-11-22

## Kontekst

Nowy typ to plik YAML (ADR-0020), ale wzorce to wyrażenia regularne: osoba bez programowania ich nie napisze. Finał: 50% oceny za dodawanie typów samą konfiguracją.

## Decyzja

1. Zakładka „Kreator nowego typu” w GUI: przykładowy PDF, nazwa typu, słowa rozpoznające, tabela pól (pole JSON, etykieta z dokumentu, rodzaj z listy).
2. Rodzaj pola -> wzorce, format i bramka: `kreator.rodzaje` w `config/ustawienia.yaml` (data, kwota, NIP, rachunek, nazwa firmy, tekst do końca linii, ...). Nowy rodzaj to wpis w konfiguracji.
3. `odwolania2json/kreator.py`: tabela -> plik typu (YAML) -> próba na przykładzie obok istniejących typów (kopia `config/`, jak po wrzuceniu pliku do `config/typy/`). GUI pokazuje: czy przykład rozpoznany jako nowy typ, JSON, skąd każda wartość, YAML do pobrania.
4. Wspólne fragmenty `DO_KONCA_LINII`, `WIERSZE_WARTOSCI` (także przykład TED zamiast własnego wzorca). Test T22.

## Konsekwencje

- Bez wyrażeń regularnych da się zrobić pola z etykietą. Pola bez etykiety, listy (`[]`), sekcje: dalej ręcznie w YAML.
- Przykład TED z `WIERSZE_WARTOSCI`: wyniki bez zmian (rozwój 0.9892, pomiar 0.9902).
