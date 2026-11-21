# ADR-0005: Nie wiadomo, jak dokładnie UZP liczy F1

Status: przyjęte, 2026-11-21

## Kontekst

Nie wiadomo: (1) czy wymagają dokładnej zgodności wartości, (2) czy liczy się kolejność na listach (kilku Odwołujących, kilku pełnomocników). Czekanie na odpowiedź to strata czasu.

## Decyzja

Robimy tak, żeby wynik był najlepszy przy każdej odpowiedzi.

1. Format dokładnie jak we wzorcu. Każdą wartość zapisujemy w tym samym formacie i typie co w treningowych JSON:

   | W dokumencie | Zapisujemy | Typ |
   |---|---|---|
   | `21.03.2026` | `"2026-03-21"` | tekst ISO |
   | `1 kwietnia 2026` | `"2026-04-01"` | tekst ISO |
   | `200,00 zł` | `200.0` | liczba |
   | `PL05 4706 8028 …` | `"05470680287581539721455024"` | tekst bez `PL` i spacji |
   | `NIP: 999-928-40-65` | `"9999284065"` | tekst z cyfr |
   | PESEL `85120133547` | `85120133547` | liczba |

   Nasz F1 jest ścisły (ADR-0003), więc sam pokaże każde odstępstwo formatu.
2. Kolejność na listach jak w dokumencie: kto jest wymieniony pierwszy, jest pierwszy na liście. Przy listach skrypt sprawdzi, czy wzorzec też zachowuje kolejność dokumentu.
3. Pytanie na stoisku UZP nie blokuje pracy. Jeśli odpowiedź będzie inna, zmieniamy tylko porównanie w `tools/ocena_f1.py`, a nie ekstrakcję.

## Konsekwencje

- Pracujemy dalej bez odpowiedzi UZP.
- Dokładny format daje maksimum zarówno przy ścisłej, jak i przy łagodnej metryce.
