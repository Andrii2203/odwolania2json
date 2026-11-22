# ADR-0018: Czas na maszynie UZP: zapis zaraz, limit OCR, pierwsze strony skanu

Status: przyjęte, 2026-11-22

## Kontekst

README UZP: 150 PDF w 45 min na maszynie z 2 vCPU (ADR-0017). Dokument cyfrowy to ułamek sekundy, strona skanu kilka sekund. Nie wiemy, ile skanów będzie w zbiorze i jak długie. Jeśli PDF leżą w `input/` bez podkatalogów, cały zbiór to jedna sprawa (ADR-0016), a JSON powstawał dopiero po całej sprawie.

## Decyzja

1. JSON każdego dokumentu zapisujemy zaraz po nim; po kontekście sprawy zapisujemy go jeszcze raz (T16).
2. `CZAS_OCR_S` w `config/ustawienia.yaml`: po tylu sekundach od startu nowe strony bez tekstu nie idą do OCR, w dzienniku „OCR pominięty: limit czasu” (T17).
3. `STRONY_OCR`: do OCR idą pierwsze strony skanu i ostatnia (README UZP: dane „z reguły na pierwszych trzech stronach”; ostatnia ma podpisy). Na 30 skanach UZP F1 taki sam jak przy wszystkich stronach (T19).
4. Wątki OCR = liczba rdzeni dostępnych dla procesu: więcej wątków niż rdzeni spowalniało OCR wielokrotnie.

## Konsekwencje

- Przerwanie programu zostawia JSON wszystkich przetworzonych dokumentów.
- Pole z dalszej strony długiego skanu (np. 5 z 20) zostanie `null`. PDF cyfrowe bez zmian.
- 22.11 UZP wydłużył limit z 45 do 60 min na 150 PDF: `CZAS_OCR_S` 2400 -> 3300 (ta sama reguła: limit minus 5 min zapasu).
