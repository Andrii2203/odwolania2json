# ADR-0015: Bramka `utnij`: wartość kończy się na pierwszym stopie

Status: przyjęte, 2026-11-22; etap 5 z ADR-0012

## Kontekst

Gdy dane strony są w jednej linii („Belmoria Rozwiązania S.A. ul. Zaczarowana 78, 90-803 Łódź KRS: …”), nazwa brała całą linię. Wariant `laczenie_linii` (ADR-0011) dawał F1 0.834. Wzorzec nazwy kończy się na końcu linii, a nie na adresie czy numerze.

## Decyzja

1. Pole może mieć klucz `utnij`: lista wzorców (z fragmentami `{…}`). Wartość ucinamy przed pierwszym trafieniem, potem obcinamy końcowe „ ,;”.
2. Wspólny fragment `KONIEC_NAZWY` w `config/ustawienia.yaml`: adres (ul., al., pl., os.), kod pocztowy, KRS/NIP/REGON/PESEL, e-mail, „tel.”, „reprezentowan…”, „(dalej”.
3. `utnij: ['{KONIEC_NAZWY}']` mają nazwy: Odwołującego, pełnomocnika, Zamawiającego, mocodawcy.
4. Dziennik dopisuje do reguły „bramka: ucięte przed „ul.””.

## Konsekwencje

- Warianty F1 0.9692 -> 0.9706 (`laczenie_linii` 0.834 -> 0.851), treningowe bez zmian (0.9990).
- Nowa reguła walidacji jest w konfiguracji, nie w kodzie (UZP liczy konfigurację reguł walidacji do elastyczności).
- Nazwa z „ul.” w środku (np. „Zarząd Dróg ul. …”) zostanie ucięta; w danych UZP takiej nie ma.
