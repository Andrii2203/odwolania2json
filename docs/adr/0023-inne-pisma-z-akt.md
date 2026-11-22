# ADR-0023: Inne pisma z akt sprawy nie są odwołaniem ani przelewem

Status: przyjęte, 2026-11-22; uzupełnia ADR-0002 (znaczniki i wykluczenia)

## Kontekst

Zbiór testowy UZP to „realne sprawy odwoławcze”. W aktach sprawy są też pisma, których nie ma w danych treningowych: odpowiedź na odwołanie, przystąpienie do postępowania odwoławczego, SWZ, umowa, faktura, wezwanie Prezesa KIO do uzupełnienia wpisu. Próba na krótkich tekstach takich pism: 6 z 6 dostawało typ (odpowiedź i przystąpienie: odwołanie; SWZ, umowa, faktura, wezwanie: przelew, bo wystarczało słowo „przelew” i „rachunek”). JSON z wartościami zamiast `{}` to same FP.

## Decyzja

Reguły według treści pisma, nie według przykładów:

1. Odwołanie nie wnosi o oddalenie odwołania. Wspólne wykluczenia (`config/ustawienia.yaml`): „o oddalenie odwołania”, „odpowiedź na odwołanie”, „przystąpienie do postępowania”. Pełnomocnictwo pisze „zgłoszenia przystąpienia” (zakres umocowania, 22 z 70 pełnomocnictw UZP), więc go nie wyklucza.
2. Odwołanie: dodatkowo „przystępując” (strona, która przystąpiła).
3. Potwierdzenie przelewu zawsze podaje nadawcę. Znaczniki przelewu: „przelew” i etykieta nadawcy, ta sama lista co etykiety pola `z_rachunku` (kotwica YAML `&nadawca`, bez kopii listy).

## Konsekwencje

- Na 476 prawdziwych dokumentach (180 treningowych, 30 skanów, 16 obcych UZP, 250 TED) klasyfikacja bez zmian; etykieta nadawcy jest w 70 z 70 przelewów, wykluczenia w 0 z 70 odwołań. Warianty F1 0.9798 bez zmian.
- T23: teksty pism w `tests/dane/pisma/` napisane na wzór prawdziwych; prawdziwych pism z akt KIO nie mamy.
- Przelew bez żadnej etykiety nadawcy (inny bank, inna nazwa) dostanie `{}`; nową nazwę dopisuje się w etykietach `z_rachunku`, działa wtedy i dla klasyfikacji, i dla pola.
