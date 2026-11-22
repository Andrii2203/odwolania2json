# Analiza braków i ryzyk przed oddaniem (2026-11-22)

Argon (Gemini). Przegląd `docs/UZP/from discord.md`, `data/uzp/VM.md`, `data/uzp/README.md`, Regulaminu oraz kodu projektu (`odwolania2json/`, `config/`).

## 1. Pułapki oceny automatycznej na maszynie UZP (Ubuntu 24.04, 2 vCPU)

1. **Wielkość liter w rozszerzeniu `.PDF` na Linuksie (`odwolania2json/cli.py:51`) – ryzyko pominięcia plików:**
   - W `cli.py` lista plików wejściowych jest pobierana przez `sorted(args.input.rglob("*.pdf"))`.
   - Na Windows wzorzec `*.pdf` nie rozróżnia wielkości liter, ale na Ubuntu 24.04 system plików rozróżnia wielkość liter (`case-sensitive`).
   - Fizyczne skanery biurowe często zapisują pliki z wielkimi literami (`SKAN_001.PDF`, `Dokument.PDF`). Na Linuksie `rglob("*.pdf")` pominie takie pliki i nie zapisze dla nich JSON.
   - **Co zrobić:** wybierać pliki przez `[p for p in args.input.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf"]`.

2. **Płaskie `input/` bez podkatalogów a `kontekst_sprawy` (`odwolania2json/pipeline.py:118-120`):**
   - W `przetworz_wszystkie()` dokumenty są łączone w sprawy po `pdf.parent`.
   - Jeśli oceniający wgra 150 plików PDF bezpośrednio do `/opt/solution/input/` bez podkatalogów `case1/`, `case2/`, wszystkie 150 dokumentów trafi do jednej wspólnej sprawy `sprawy[Path("input")]`.
   - Choć `uzupelnij_sprawe()` sprawdza obecność wartości w tekście docelowego dokumentu (`_w_tekscie`), przy płaskim katalogu przeszukuje krzyżowo kandydatów ze wszystkich odwołań i pełnomocnictw naraz (np. gdy ten sam pełnomocnik albo podmiot występuje w kilku sprawach).

3. **OCR wszystkich stron długich skanów na 2 vCPU (`odwolania2json/pipeline.py:37-46`):**
   - Limit czasu na maszynie UZP z 2 vCPU to 45 minut na 150 plików PDF (średnio 18 s na PDF).
   - Według `data/uzp/README.md` (wprowadzenie) kluczowe informacje znajdują się z reguły na pierwszych trzech stronach dokumentu (plus ostatnia strona z podpisami w pełnomocnictwie).
   - Jeśli w tajnym zbiorze testowym znajdzie się kilkanaście skanów `odwolanie.pdf` mających po 15–25 stron uzasadnienia prawnego, OCR straci po 1–2 minuty na strony 4..25 każdego odwołania (z których żadne pole nie trafia do JSON), wyczerpie budżet `CZAS_OCR_S = 2400` i zostawi jednostronicowe skany przelewów na końcu listy bez OCR (`{}`).
   - **Co zrobić:** ograniczyć w `config/ustawienia.yaml` liczbę stron wysyłanych do OCR dla jednego dokumentu (np. pierwsze N stron oraz ostatnia strona) albo w pierwszej kolejności przetwarzać dokumenty krótsze (1–2 strony), a wielostronicowe skany na końcu.

4. **Uprawnienia do `/opt/solution` przy logowaniu z konta oceniających (`data/uzp/VM.md:56-59`):**
   - Według `VM.md` oceniający logują się po 11:00 własnym kontem i uruchamiają komendę z `/opt/solution/RUN.md` (z `sudo`).
   - Na wypadek uruchomienia bez `sudo` albo zmiany zmiennej `$HOME` przy `sudo`, cały katalog `/opt/solution` (`.venv`, `.python`, modele RapidOCR) powinien mieć prawa odczytu i wykonania dla wszystkich użytkowników (`chmod -R a+rX /opt/solution`), a `/opt/solution/output` prawa zapisu (`chmod -R a+rwX /opt/solution/output`).

5. **Działające GUI w tle na otwartym porcie VM (`data/uzp/VM.md:29-40`):**
   - W `VM.md` otwarto z internetu porty `80, 443, 8000, 8080` i zaznaczono: „Usługi i kontenery, które działają w tle, nie zostaną zatrzymane”.
   - Uruchomienie naszego GUI (Streamlit) jako usługi `systemd` (`restart=always`) na porcie `8080` pozwoli jury otworzyć gotowy prototyp w przeglądarce (`http://<adres-ip>:8080`) bez instalowania czegokolwiek lokalnie.

## 2. Luki w ekstrakcji pól (F1 = 100% oceny w preselekcji)

1. **Deduplikacja w `pola.py` przed formatowaniem wartości (`odwolania2json/pola.py:115-122`):**
   - W `trafienia()` zbiór `widziane` sprawdza surowy wycinek tekstu `surowe` przed wywołaniem `spec["_wartosc"](m, surowe, stala)`.
   - Gdy w `pelnomocnictwo.pdf` ten sam NIP mocodawcy występuje w nagłówku z myślnikami (`999-551-93-82`), a w treści bez myślników (`9995519382`), `surowe` jest różne, mimo że po `format: cyfry` wartość jest identyczna (`"9995519382"`). Skutkuje to utworzeniem drugiego, nadmiarowego elementu na liście `mocodawca` (znany błąd na skanach UZP).
   - **Co zrobić:** sprawdzać i zapisywać w `widziane` także sformatowaną `wartosc`.

2. **Sortowanie trafień po pozycji w tekście zamiast po priorytecie etykiety (`odwolania2json/pola.py:110-112` oraz pytanie z `from discord.md:345`):**
   - Na Discordzie padło pytanie: „gdy potwierdzenie ma datę zlecenia i datę księgowania, która to `data_operacji`?”.
   - W `pola.py` funkcja `trafienia()` sortuje wszystkie dopasowania ze wszystkich etykiet i wzorców po pozycji w tekście (`key=lambda t: t[0].start()`) i dla pola skalarnego bierze pierwsze od góry strony (`znalezione[0]`), ignorując kolejność etykiet w YAML.
   - Ryzyko w `config/typy/przelew.yaml`:
     - Na końcu listy `etykiety` pola `data_operacji` jest ogólna fraza `w dniu`. Jeśli w nagłówku wydruku bankowego stoi „Dokument wygenerowano w dniu 2026-11-20”, a niżej w tabeli „Data operacji: 2026-11-18”, program wybierze datę wygenerowania wydruku, bo stoi wyżej na stronie.
     - Gdy na wydruku wyżej jest „Data księgowania”, a niżej „Data operacji”, program weźmie tę datę, która stoi wyżej, zamiast bardziej precyzyjnej etykiety `data operacji`.
     - Brakuje też etykiet zapasowych `data zlecenia` i `data waluty`, gdyby w potwierdzeniu nie było żadnej z obecnych 7 etykiet.

3. **Imiona i nazwiska w mianowniku (`from discord.md:159`):**
   - Wytyczna UZP z Discorda: „imiona docelowo powinny być w mianowniku, tzn. »Mateusz Szymański« zamiast »Mateusza Szymańskiego«”.
   - Obecne braki:
     - W `config/ustawienia.yaml:198` wzorzec `TYTUL_PRAWNIKA` ma `radca prawny|radcy prawnego|adwokat|adwokata`, ale nie ma celownika ani narzędnika (`radcy prawnemu`, `radcą prawnym`, `adwokatowi`, `adwokatem`), które występują po słowach „udzielam pełnomocnictwa adwokatowi Janowi Kowalskiemu”.
     - Wyciągnięte imię i nazwisko w dopełniaczu lub celowniku (`Mateusza Szymańskiego`, `Mateuszowi Szymańskiemu`) trafia do JSON bez zamiany na mianownik.

4. **Pozostałe błędy z analizy skanów UZP (`docs/STAN.md:72`):**
   - Kilku Zamawiających wymienionych listą numerowaną po jednym wspólnym nagłówku („Zamawiający wspólnie prowadzący postępowanie: 1) … 2) …”), gdzie słowo „Zamawiający” nie powtarza się przy każdym punkcie.
   - Papier firmowy kancelarii prawnej w nagłówku `pelnomocnictwo.pdf` („Kancelaria Prawna … sp. k.”), który wzorzec `{FIRMA}` bierze za pierwszego mocodawcę.

## 3. Braki formalne i finałowe (50% oceny w finale + zgłoszenie)

1. **Brak pliku `README.md` w katalogu głównym repozytorium:**
   - W katalogu głównym jest tylko `RUN.md`, a nie ma `README.md`.
   - Według Regulaminu (§ 2 ust. 4b, § 3 ust. 5) i odpowiedzi z Discorda (`from discord.md:255-261`) 50% oceny finałowej zależy od wykazania, że dodanie nowej klasy dokumentu oraz konfiguracja reguł rozpoznawania (`znaczniki`, `wykluczenia`, `wzorce`, `etykiety`), walidacji (`format`, `utnij`, `stop`) i mapowania pól (`slownik`, `kontekst`) odbywa się wyłącznie przez plik konfiguracyjny YAML bez zmiany kodu.
   - W `README.md` powinny znaleźć się:
     - instrukcja uruchomienia CLI (`start.bat`, `uruchom.sh`, `--wyjasnij`) oraz GUI (`gui.bat`),
     - krótki opis architektury potoku i przejrzystości ekstrakcji (`--wyjasnij`),
     - gotowy przykład krok po kroku: jak dodać nowy typ dokumentu (np. czwarty plik `config/typy/wezwanie.yaml`) w kilkanaście linijek bez dotykania Pythona,
     - zestawienie wyników testów jakości (`ocena_f1.py`: 0.9990 na treningowych, 0.9462 na skanach; `warianty.py`: 0.9798 na 4673 wariantach; 0/160 FP na ogłoszeniach TED; ślepy test wektorów etykiet),
     - informacja o modelu LLM (0B parametrów = maksymalne 20/20 pkt za rozmiar modelu, pełny determinizm, brak wysyłania danych poza maszynę).

2. **Ograniczenia obecnego GUI (`odwolania2json/gui.py:44`):**
   - GUI wywołuje `przetworz_wszystkie([sciezka], ...)` osobno dla każdego wgranego pliku w pętli, przez co między wgranymi plikami tej samej sprawy nie działa `kontekst_sprawy`.
   - Brakuje przycisku pobrania wynikowego pliku JSON / archiwum ZIP.

3. **Brak prezentacji PDF <= 10 MB (`ADR-0006`, zadanie `[Argon]` w `docs/STAN.md`):**
   - Wymagana przy zgłoszeniu na platformie i podczas prezentacji finałowej przed jury.

4. **Sprawdzenie nazwy zespołu i upublicznienie repozytorium (`from discord.md:347`):**
   - Przypomnienie organizatorów z Discorda: „nazwy zespołów sprawdzamy z draftami, wiec uwazajcie” – nazwa zespołu w zgłoszeniu musi być identyczna jak w drafcie.
   - Repozytorium GitHub musi zostać przełączone z prywatnego na publiczne przed 11:00.
