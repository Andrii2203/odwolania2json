# ADR-0026: Kreator: pole z przykładu, GUI dla osoby bez przygotowania

Status: przyjęte, 2026-11-22

## Kontekst

Uwagi użytkownika do GUI (22.11): nie wiadomo, od czego zacząć; w kreatorze nie wiadomo, co wpisać w kolumnach „etykieta” i „rodzaj”; „wspólne wykluczenia” to żargon; puste wiersze bez przykładu; za dużo naraz na ekranie. Finał: 50% oceny za dodawanie typów samą konfiguracją, pokazywane na GUI.

## Decyzja

1. Pole z przykładu (T26): użytkownik podaje nazwę pola i wartość skopiowaną z dokumentu. Etykieta: tekst przed wartością w tej samej linii po ostatnim dwukropku, przecinku albo średniku, a gdy wartość zaczyna linię, poprzednia linia (`kreator.etykieta_przed`). Rodzaj: pierwszy z `kreator.rodzaje` (kolejność: najpierw wąskie wzorce), z którym plik typu odtwarza tę wartość na przykładzie; najpierw rodzaj z nazwą w etykiecie, najpierw krótsze etykiety, na końcu bez etykiety. Etykietę i rodzaj można poprawić ręcznie.
2. `przygotuj_typ` i `wczytaj_typy(dodatkowe=...)` w `pipeline.py`: nowy typ z tekstu YAML bez kopii `config/` (GUI, kreator).
3. GUI: zakładki „Zamień PDF na JSON” i „Dodaj nowy typ dokumentu”; trzy kroki na górze; bez panelu bocznego: rozpoznawane typy w jednej linii, dodatkowy typ (TED, typ z kreatora) to jeden przełącznik; przyciski „Pokaż na przykładzie” (sprawa UZP z `data/uzp`, jeśli jest; w kreatorze prosta faktura `docs/przyklady/kreator/faktura.pdf` z `faktura.html`, dane fikcyjne, zamiast ogłoszenia TED, w którym jest dużo nieznanych pojęć); przy dokumencie nazwa typu i status zwykłymi słowami; ręczna poprawka JSON i YAML w zwiniętych blokach; typ z kreatora od razu do użycia w pierwszej zakładce; w polu wyboru pliku „tylko PDF”.
4. Kreator: zamiast tabeli wiersze „nazwa pola | wartość z dokumentu” z przykładem w każdym polu, wynik obok („✅ data”, „❌ brak w dokumencie”), poprawka etykiety i rodzaju w okienku wyniku, „➕ Dodaj pole”, „🗑”.
5. Podgląd z zakreślaczem (T27, `odwolania2json/podglad.py`): fragment z dziennika na żółto, wartość na pomarańczowo, numer jak wiersz w „Skąd te wartości”; tekst szukany bez odstępów (pypdf i pdfium łamią linie inaczej). Kolory i wielkości w `config/ustawienia.yaml` (`gui`, `PODGLAD_DPI`).

## Konsekwencje

- Kreator działa bez wiedzy o etykietach i rodzajach, gdy wartość jest w tekście dokumentu. Wartość w kilku liniach albo bez etykiety w tej samej lub poprzedniej linii: rodzaj albo etykietę trzeba wybrać ręcznie (GUI to pokazuje).
- Skan (PDF bez tekstu) bez podświetlenia; w pierwszej zakładce data i kwota tylko na żółto (w JSON inny zapis niż w dokumencie).
- Ekstrakcja w CLI bez zmian (F1 bez zmian); zmienia się tylko kolejność listy rodzajów w kreatorze.
