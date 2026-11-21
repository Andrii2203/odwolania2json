# ADR-0008: Wzorce regex i listy w regułach pól

Status: przyjęte, 2026-11-21; uzupełnia ADR-0009 (`etykiety` przed wzorcami, pole bez `[]`)

## Kontekst

`etykiety` z ADR-0002 dają jedną wartość po etykiecie. Pełnomocnictwo i odwołanie mają listy: kilku mocodawców, kilku pełnomocników, kilku podpisujących. Wartości często nie mają etykiety: „r. pr. Jan Nowak”, „Belmoria Rozwiązania S.A.”.

## Decyzja

Pole w YAML może mieć `wzorce` zamiast `etykiety`. Wzorzec to wyrażenie regularne. Wartość to grupa 1 (albo całe trafienie), bez nadmiarowych spacji.

```yaml
pelnomocnicy[].imie_nazwisko:
  wzorce: ['(?:r\.\s?pr\.|adw\.)\s+({OSOBA})']
```

„adw. Bartosz Szymanski, … adw. Cezary Wierzbicki” daje `[{"imie_nazwisko": "Bartosz Szymanski"}, {"imie_nazwisko": "Cezary Wierzbicki"}]`.

1. Zbieramy wszystkie trafienia wszystkich wzorców w kolejności w tekście. Powtórzenia pomijamy.
2. `[]` w ścieżce: kolejne trafienia trafiają do kolejnych elementów listy. Nowy element to kopia elementu z `szablon`.
3. Liczbę elementów listy wyznacza pierwsze pole tej listy w YAML. Następne pola tylko uzupełniają istniejące elementy. Przykład: NIP-y są tylko mocodawców, a nazw firm jest więcej (zamawiający), więc NIP idzie pierwszy.
4. Dwa `[]` (`mocodawca[].podpisujacy[].imie_nazwisko`): `podzial` to wzorzec granicy („W imieniu …”). Trafienie po k-tej granicy idzie do k-tego elementu zewnętrznej listy. Bez granic wszystko idzie do pierwszego.
5. `wartosc` przy wzorcu: stała zamiast tekstu („KRS 999…” daje `osoba_prawna`). `format: cyfry`: zostają tylko cyfry.
6. Wspólne fragmenty (`{OSOBA}`, `{FIRMA}`) są w `config/ustawienia.yaml` w `wzorce`.

## Konsekwencje

- Nowy typ z listami to nadal tylko plik YAML.
- Regex jest trudniejszy do czytania niż etykieta. Dlatego wspólne fragmenty mają nazwy.
- Gdy dwóch mocodawców ma różny układ, kolejność może się pomylić. Takie pola przejmie LLM (ADR-0004).
