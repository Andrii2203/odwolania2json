# GLiNER2 zamiast etapów 6 i 7 (wektory, LLM): pomiar 2026-11-21

Claude. Pytanie: czy jeden mały model (GLiNER2, Apache 2.0, CPU) może wyciągać pola według schematu z opisami zamiast regex, wektorów i LLM.

## Jak mierzyliśmy

- Model `fastino/gliner2-multi-v1` (205M parametrów, mDeBERTa-v3), pakiet `gliner2` 2.2.0 z torch CPU, osobne środowisko (bez zmian w `requirements.txt`). `gliner2.5-multi-v1` nie wczytał się w tej wersji pakietu.
- `extract_json_long` (tekst dzielony na kawałki), schemat z polskimi opisami pól dla trzech typów.
- Te same 180 dokumentów treningowych i to samo porównanie co `tools/ocena_f1.py`; z fragmentu modelu mechanicznie bierzemy liczbę i datę (jak bramka); pola ze słownika (`typ`, `czynnosc_powod_id`, `przez-pelnomocnika`) pominięte w obu.

## Wynik

| | F1 razem | odwolanie | pelnomocnictwo | przelew |
|---|---|---|---|---|
| GLiNER2 | 0.551 | 0.493 | 0.493 | 0.872 |
| nasze reguły | 0.999 | 1.000 | 1.000 | 0.994 |

Czas na dokument (16 wątków CPU): odwołanie średnio 14,8 s (maks. 56 s), pełnomocnictwo 1,3 s, przelew 0,8 s. Reguły: ok. 0,2 s na dokument.

Najwięcej błędów: nazwy stron (dodatkowe, fałszywe elementy list), pełnomocnik, PESEL, tytuł zamówienia, numer TED (inny zapis niż w JSON).

## Wniosek

Nie zastępuje reguł: F1 dużo niższe, a czas odwołania przekracza ok. 18 s na dokument (pytanie uczestnika o 150 dokumentów w 45 min) już na mocnym komputerze; na biurowym będzie wolniej. Dostrajanie (opisy po angielsku, próg, tryb encji) nie zamknie różnicy 0.55 -> 0.99. Zostajemy przy regułach i etapach mechanicznych (`docs/potok.md`); wypełnianie pustych pól (etapy 6, 7) wraca do decyzji po pomiarach.
