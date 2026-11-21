# ADR-0016: Kontekst sprawy: puste pole z innego dokumentu tej samej sprawy

Status: przyjęte, 2026-11-22; etap 8 z ADR-0012

## Kontekst

Sprawa to trzy dokumenty o tych samych stronach. W 60/60 sprawach treningowych: mocodawca = Odwołujący (nazwa, NIP), pełnomocnik z odwołania jest w pełnomocnictwie, tytuł przelewu ma nazwisko pełnomocnika i numer postępowania. Gdy reguła zawodzi w jednym dokumencie (inny układ), ta sama wartość bywa znaleziona w innym.

## Decyzja

1. Sprawa = PDF-y z jednego katalogu. `przetworz_wszystkie` najpierw wyciąga pola ze wszystkich dokumentów sprawy, potem uzupełnia, potem oddaje wyniki.
2. Plik typu ma klucz `kontekst`: pole -> {typ źródła: pole źródła}. Przykład: `mocodawca[].data.nip: {odwolanie: 'Odwolujacy[].nip'}`.
3. Wypełniamy tylko puste pole i tylko wartością, która jest w tekście tego dokumentu (cyfry także z odstępami i myślnikami). Niczego nie wymyślamy.
4. Pusta lista (np. brak mocodawcy) dostaje jeden element, jeśli jest kandydat w tekście.
5. Dziennik: „kontekst sprawy: <typ> <pole>” i fragment tekstu. Przełącznik `etapy.kontekst_sprawy` w `config/ustawienia.yaml`.

## Konsekwencje

- Warianty (jeden dokument sprawy zmieniony, dwa oryginalne) F1 0.9730 -> 0.9798; `laczenie_linii` 0.866 -> 0.902; treningowe bez zmian (0.9990).
- JSON sprawy powstaje po przetworzeniu wszystkich jej dokumentów (sprawa ma zwykle 3 dokumenty, więc to bez wpływu na limit czasu).
- Skany UZP to pojedyncze dokumenty bez sprawy: tam etap nic nie daje.
- Dalej: mianownik imienia i nazwiska z innego dokumentu sprawy (ten sam rdzeń nazwiska).
