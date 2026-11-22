# ADR-0024: Imiona i nazwiska w mianowniku przez Morfeusz2

Status: przyjęte, 2026-11-22

## Kontekst

UZP wymaga imion i nazwisk w mianowniku („Mateusz Szymański”, nie „Mateusza Szymańskiego”). W danych treningowych i skanach odmian nie ma, ale w prawdziwych pełnomocnictwach są częste („udzielam pełnomocnictwa adwokatowi Janowi Kowalskiemu”). Reguły końcówek nie wystarczą: „Pawła Wróbla” -> „Paweł Wróbel” (zanik samogłoski), „Aleksandrze Marciniak” to kobieta, „Elżbiecie” -> „Elżbieta” (oboczność).

## Decyzja

1. Gotowe narzędzie: Morfeusz2 1.99.15 (IPI PAN), analizator morfologiczny ze słownikiem SGJP; program i dane fleksyjne na dwuklauzulowej licencji BSD (http://morfeusz.sgjp.pl/doc/license/); koło `abi3` dla Windows i Linux (Ubuntu 24.04), ok. 9 MB, start 0,02 s, bez internetu.
2. `format: mianownik` w polach z imieniem i nazwiskiem (`config/typy/*.yaml`); nowy typ może go użyć bez zmiany kodu.
3. Tylko nazwy własne (rzeczownik, forma podstawowa z wielkiej litery). Jeśli każde znane słowo ma odczytanie w mianowniku, wartość zostaje bez zmian. Inaczej rodzaj i przypadek wspólne dla wszystkich znanych słów i ich formy podstawowe. Słowo spoza słownika zostaje bez zmian.
4. Tytuł pełnomocnika także w celowniku: „adwokatowi”, „radcy prawnemu” (`TYTUL_PRAWNIKA`).

## Konsekwencje

- T24. F1 bez zmian: treningowe 0.9990, skany 0.9508; nazwiska w mianowniku zostają nietknięte.
- Rzadkie nazwisko spoza SGJP w odmianie („Brzęczyszczykiewiczowi”) zostaje w odmianie.
- Nowa zależność w `requirements.txt`; instalacja na maszynie UZP przez `instaluj.sh` (internet jest).
