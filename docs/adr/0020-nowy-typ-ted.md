# ADR-0020: Przykład nowego typu na prawdziwych dokumentach: ogłoszenie TED

Status: przyjęte, 2026-11-22; zastępuje wymyślony przykład `wezwanie.yaml`

## Kontekst

Finał: 50% oceny za dodawanie nowych typów dokumentów samą konfiguracją. Przykład z wymyślonym tekstem niczego nie dowodzi. Potrzebny prawdziwy dokument, którego ludzie używają, i poprawne wartości spoza naszego programu.

## Decyzja

1. Typ `docs/przyklady/ogloszenie_ted.yaml`: ogłoszenie TED po polsku (numer, data publikacji, CPV; nabywca: nazwa, numer rejestracyjny, miejscowość). Poza `config/typy/`, bo w ocenie UZP ogłoszenie TED to dokument spoza klas (`{}`).
2. Poprawne wartości z API TED (`tools/pobierz_obce.py`, mapa pól w `config/ustawienia.yaml` `narzedzia.obce_ted.wzorzec`), nie z naszego odczytu PDF.
3. Reguły piszemy na `CZESC_ROZWOJ` ogłoszeń (`data/przyklad_ted/rozwoj`, wolno patrzeć w błędy); wynik podajemy na reszcie (`pomiar`), bez poprawiania reguł pod nią.
4. Klucz typu `wspolne_wykluczenia: false`: wspólne wykluczenia (wyrok KIO „orzeka”, TED „oficjalna nazwa”) tego typu nie dotyczą. Jedyna zmiana kodu, ogólna dla każdego typu.
5. Test T21: jeden prawdziwy PDF w `tests/dane/ted/` (ponowne wykorzystanie dozwolone, decyzja Komisji 2011/833/UE): z typem JSON = dane TED, bez typu `{}`.

## Konsekwencje

- Pomiar 22.11: rozwój 62 ogłoszenia F1 0.9892; pomiar 188 ogłoszeń, których reguły nie widziały: typ 188/188, F1 0.9902. Domyślna konfiguracja: 250/250 ogłoszeń daje `{}`, treningowe bez zmian (0.9990).
- Pozostałe błędy: przeniesienie wyrazu z myślnikiem („SKŁODOWSKIEJ- CURIE”), kilku nabywców (inna kolejność niż w API), nazwa z adresem w danych TED.
