# ADR-0011: Pomiar na wariantach dokumentów i na obcych dokumentach z internetu

Status: przyjęte, 2026-11-21

## Kontekst

Reguły są dopasowane do 60 spraw treningowych i 30 skanów, więc F1 0.9990 nie mówi, jak program działa na nowych dokumentach. Skany przed dopasowaniem dały 0.8696. Nie mamy nietkniętego zbioru z wzorcami JSON.

## Decyzja

1. `tools/warianty.py`: z każdego dokumentu treningowego robimy warianty tekstu i od razu poprawiamy wzorzec JSON, bo wiemy, co zmieniliśmy. Rodziny: `wartosci` (ciągi cyfr), `braki` (wartość usunięta, w JSON `null`), `nazwy` (słowa nazw firm nieznane konfiguracji), `daty` (przesunięcie), `etykieta` (inny zapis etykiety), `bloki` (inna kolejność), `laczenie_linii`, `lamanie_linii`. Każda rodzina i każda zamiana etykiety ma osobne F1 i listę najgorszych pól.
2. Zmiany są na poziomie tekstu (po `tekst_pdf`), bez tworzenia PDF: kilka tysięcy wariantów w mniej niż minutę.
3. Losowość jest powtarzalna: ziarno z nazwy pliku, rodziny i numeru losowania.
4. Zamiany etykiet i bloki są w `config/ustawienia.yaml` (`narzedzia.warianty`), tak jak liczby (ADR-0009).
5. Obce dokumenty: `tools/pobierz_obce.py` pobiera polskie ogłoszenia TED z publicznego API TED do `data/obce/ted` (poza git). `tools/ocena_f1.py --dane data/obce` liczy, ile z nich dostało JSON.

## Konsekwencje

- Mamy dwie liczby dla nowych dokumentów: F1 na wariantach i odsetek obcych dokumentów z JSON.
- Warianty pokazują słabe miejsca reguł, ale nie są losową próbką ukrytych dokumentów: zamiany etykiet wybraliśmy sami. Poprawki pod warianty to też dopasowanie, więc po poprawkach warto dodać nowe zamiany.
- Ogłoszenia TED odrzuca głównie jedno słowo z `wykluczenia` („oficjalna nazwa”). Inne obce dokumenty (faktury, wyroki KIO, BZP) warto dodać.
- Nie zmieniamy imion i nazwisk (odmiana) ani kwot.
