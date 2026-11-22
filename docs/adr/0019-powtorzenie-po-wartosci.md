# ADR-0019: Powtórzenie wartości rozpoznajemy po wartości po formacie

Status: przyjęte, 2026-11-22; etap 9 z ADR-0012

## Kontekst

Skan UZP `pelnomocnictwa/0002`: stopka powtarza NIP mocodawcy z myślnikami („999-509-02-81”), w treści jest „9995090281”. Powtórzenia odrzucaliśmy po zapisie w tekście, więc powstawał drugi mocodawca.

## Decyzja

W `trafienia()` (`odwolania2json/pola.py`) trafienie z tą samą wartością po `format` co wcześniejsze jest pomijane. Wyjątek: stałe z `wartosc` (np. `typ: osoba_fizyczna`) dalej po zapisie w tekście, bo kilka elementów listy może mieć tę samą stałą. Test T18.

## Konsekwencje

- Skany 0.9462 -> 0.9508; treningowe (0.9990) i warianty (0.9798) bez zmian.
- Dwa różne podmioty z tą samą wartością pola tekstowego dostaną jedną wartość (w danych nie spotkaliśmy).
