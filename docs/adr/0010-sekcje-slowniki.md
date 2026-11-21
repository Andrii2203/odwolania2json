# ADR-0010: Sekcje, słowniki i szablony wartości w regułach pól

Status: przyjęte, 2026-11-21; uzupełnia ADR-0008

## Kontekst

Odwołanie ma dwie strony z tymi samymi polami (NIP, KRS, REGON), w różnej kolejności: raz najpierw Odwołujący, raz Zamawiający. Niektóre pola są liczbą ze słownika UZP (`czynnosc_powod_id`, `przez-pelnomocnika`). Numer TED bywa zapisany jako `2026/S 142-999327`, a w JSON ma być `999327-2026`.

## Decyzja

Nowe klucze pola w pliku typu (wszystkie opcjonalne):

1. `sekcja`: wzorzec bloku tekstu. Pole szukamy tylko w blokach, które pasują do tego wzorca. Przykład: od „Odwołujący:” do następnego nagłówka.
2. `slownik`: nazwa słownika z `config/ustawienia.yaml` (`slowniki`). Wartość tekstowa zamienia się na liczbę: `Decyzja o unieważnieniu postępowania` daje `9`, `tak` daje `1`. Liczby są w ustawieniach, bo plik typu nie ma liczb (ADR-0009).
3. `wartosc` może mieć grupy nazwane z wzorca: `'{nr}-{rok}'`.
4. `wzorce` na najwyższym poziomie pliku typu: własne fragmenty typu, obok wspólnych z `config/ustawienia.yaml`.
5. `podzial` działa też dla listy bez zagnieżdżenia: trafienie po k-tej granicy idzie do k-tego elementu. Dzięki temu KRS drugiego zamawiającego nie przechodzi do pierwszego, gdy pierwszy KRS nie ma.

Zmiany w zachowaniu:

- Pole bez `[]` bierze pierwsze trafienie w tekście, a nie trafienie pierwszego wzorca. Wynik przelewu i pełnomocnictwa bez zmian (F1 0.5711 przed i po).
- Powtórzenia pomijamy po sortowaniu według pozycji, więc zostaje najwcześniejsze trafienie.
- W elemencie listy zostaje pierwsza wartość pola, kolejne trafienia go nie nadpisują.
- Dopisane 2026-11-21 (skany, ADR-0007): `sekcja` może stać też przy jednym wzorcu (`{wzorzec: …, sekcja: …}`) i wtedy dotyczy tylko jego. Pełnomocnicy: `adw. X` w całym tekście albo dowolne imię i nazwisko na liście „udziela pełnomocnictwa: … do reprezentowania”.

## Konsekwencje

- Odwołanie to tylko plik YAML: 0 błędów na 60 sprawach treningowych, łączny F1 z 0.5711 do 0.9983.
- Reguły są dopasowane do 60 spraw. W ukrytych sprawach może być inny układ. Dlatego zostaje plan LLM (ADR-0004) dla pól, których reguły nie znajdą.
