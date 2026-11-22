# ADR-0025: Sklejone linie: podpisujący i nagłówki stron w środku linii

Status: przyjęte, 2026-11-22

## Kontekst

Wiele reguł zakłada układ linii z danych UZP: nagłówek „Odwołujący:” na początku linii, imię i nazwisko podpisującego w jednej linii, a funkcja w następnej. Inny PDF (dwie kolumny, inne narzędzie do tekstu, OCR składający wiersze) skleja linie. Pomiar `tools/warianty.py` (rodzina `laczenie_linii`): najwięcej błędów w `mocodawca[].podpisujacy[].imie_nazwisko` (253) i całe sekcje Zamawiającego i Odwołującego (po ok. 100 na pole).

## Decyzja

1. Podpisujący: jeden wzorzec `({OSOBA})(?:\s*[-–]\s*|\s+){FUNKCJA}` zamiast dwóch (nowa linia albo myślnik): imię i nazwisko, potem myślnik albo dowolne odstępy, potem funkcja.
2. `nowa_linia` w pliku typu: wzorce miejsc, w których przed wyciąganiem pól wstawiana jest nowa linia. Odwołanie: przed „Odwołujący:”, „Zamawiający:” (z dwukropkiem, jak w dokumencie albo wielkimi), „Działając w imieniu”, „ODWOŁANIE”, „Wykonawca wybrany” w środku linii. W 70 odwołaniach UZP te słowa w środku linii nie występują (0), więc znane dokumenty się nie zmieniają; „Wykonawca” bez dalszego słowa występuje w środku linii (53), więc go nie ma.

## Konsekwencje

- T25. Treningowe F1 0.9990 bez zmian; warianty 0.9798 -> 0.9870.
- Nowy typ może użyć `nowa_linia` bez zmiany kodu.
- Dziennik pokazuje fragment z tekstu po wstawieniu nowych linii.
