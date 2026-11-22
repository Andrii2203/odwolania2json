# ADR-0026: Kreator: pole z przykładu, GUI dla osoby bez przygotowania

Status: przyjęte, 2026-11-22

## Kontekst

Uwagi użytkownika do GUI (22.11): nie wiadomo, od czego zacząć; w kreatorze nie wiadomo, co wpisać w kolumnach „etykieta” i „rodzaj”; „wspólne wykluczenia” to żargon; puste wiersze bez przykładu; za dużo naraz na ekranie. Finał: 50% oceny za dodawanie typów samą konfiguracją, pokazywane na GUI.

## Decyzja

1. Pole z przykładu (T26): użytkownik podaje nazwę pola i wartość skopiowaną z dokumentu. Etykieta: tekst przed wartością w tej samej linii po ostatnim dwukropku, przecinku albo średniku, a gdy wartość zaczyna linię, poprzednia linia (`kreator.etykieta_przed`). Rodzaj: pierwszy z `kreator.rodzaje` (kolejność: najpierw wąskie wzorce), z którym plik typu odtwarza tę wartość na przykładzie; najpierw rodzaj z nazwą w etykiecie, najpierw krótsze etykiety, na końcu bez etykiety. Etykietę i rodzaj można poprawić ręcznie.
2. `przygotuj_typ` i `wczytaj_typy(dodatkowe=...)` w `pipeline.py`: nowy typ z tekstu YAML bez kopii `config/` (GUI, kreator).
3. GUI: zakładki „Zamień PDF na JSON” i „Dodaj nowy typ dokumentu”; trzy kroki na górze; przyciski „Pokaż na przykładzie” (sprawa UZP z `data/uzp`, jeśli jest, i ogłoszenie TED z `docs/przyklady/kreator/`); przy dokumencie nazwa typu i status zwykłymi słowami; źródło wartości, ręczna poprawka JSON i YAML w zwiniętych blokach; typ z kreatora od razu do użycia w pierwszej zakładce.

## Konsekwencje

- Kreator działa bez wiedzy o etykietach i rodzajach, gdy wartość jest w tekście dokumentu. Wartość w kilku liniach albo bez etykiety w tej samej lub poprzedniej linii: rodzaj albo etykietę trzeba wybrać ręcznie (GUI to pokazuje).
- Ekstrakcja w CLI bez zmian (F1 bez zmian); zmienia się tylko kolejność listy rodzajów w kreatorze.
