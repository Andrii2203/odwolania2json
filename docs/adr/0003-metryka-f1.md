# ADR-0003: Jak liczymy F1

Status: przyjęte, 2026-11-21

## Kontekst

O awansie do finału w 100% decyduje F1 na ukrytych sprawach. Nie wiadomo, jak dokładnie UZP liczy F1 (ADR-0005). Potrzebujemy własnej liczby, żeby widzieć, czy zmiana pomogła.

## Decyzja

Porównujemy każde pole-liść wzorcowego i naszego JSON po ścieżce (`Odwolujacy[0].nip`). Listy porównujemy po indeksie.

| Wzorzec | Nasz | Wynik |
|---|---|---|
| `200.0` | `200.0` | TP (trafienie) |
| `"Wpis"` | `null` | FN (pominięte) |
| `null` | `"X1"` | FP (wymyślone) |
| `"A"` | `"B"` | FP i FN (błąd) |
| `null` | `null` | nie liczy się |

`F1 = 2·TP / (2·TP + FP + FN)`

Przykład: wzorzec `{"kwota": 200.0, "numer_transakcji": null, "tytul": "Wpis"}`, nasz `{"kwota": 200.0, "numer_transakcji": "X1", "tytul": null}`. Wynik: TP 1, FP 1, FN 1, więc F1 = 2/(2+1+1) = 0,5.

Porównanie jest ścisłe: wartość i typ muszą się zgadzać (`200` to nie `200.0`, `"200"` to nie `200.0`). Jeśli oficjalna metryka jest łagodniejsza, prawdziwy wynik nie będzie gorszy.

## Konsekwencje

- `tools/ocena_f1.py` pokazuje łączny F1 i najgorsze pola.
- Ryzyko: jeśli UZP dopasowuje listy inaczej niż po indeksie, nasz F1 będzie się różnił (ADR-0005).
