# Wektory etykiet (etap 6): ślepy pomiar dwóch modeli 2026-11-22

Argon (Gemini). Pytanie: jak wektorowe dopasowanie nieznanych etykiet (etap 6 w `docs/potok.md`) radzi sobie bez podpowiedzi w konfiguracji i jaka jest różnica między modelem lokalnym na CPU a modelem przez API w UE.

## Dlaczego zwykły pomiar `tools/warianty.py` nie wystarczyłby (problem przecieku odpowiedzi)

W `config/ustawienia.yaml` (`narzedzia.warianty.etykiety`) było dotąd 14 reguł (45 zamian etykiet), ale większość z nich została już wcześniej ręcznie dopisana do `config/typy/przelew.yaml` (gdzie dla 6 pól wpisano łącznie aż 52 synonimy). Gdybyśmy mierzyli wektory na dotychczasowych wariantach albo dopisali 10 nowych wariantów wiedząc, co jest w konfiguracji, byłoby to dopasowanie do znanych odpowiedzi.

Dlatego przed uruchomieniem pomiaru przygotowaliśmy dwustopniowy ślepy eksperyment w osobnym katalogu poza repozytorium (`scratch/`), bez edycji żadnego pliku w `config/` i `odwolania2json/`.

## Co zrobiliśmy przed uruchomieniem testu (krok po kroku)

### Krok 1. Przygotowanie środowiska i dwóch modeli w `scratch/`

1. **Model lokalny CPU (`intfloat/multilingual-e5-small`, 118M parametrów, MIT):**
   - W `.venv` projektu były już `onnxruntime` 1.32.0 i `numpy`. Do `scratch/pkgs/` doinstalowano wyłącznie lekki pakiet `tokenizers` (`--no-deps`), a do `scratch/e5-small/` pobrano z Hugging Face pliki `tokenizer.json` (17,1 MB) oraz `onnx/model.onnx` (470,3 MB).
   - Każdą krótką frazę kodowano z prefiksem `"query: " + fraza.strip().lower()`, obcinano do 32 tokenów, uśredniano po masce uwagi (*mean pooling*) i normalizowano L2.
2. **Model chmurowy w UE (`bge-m3`, 568M parametrów, MIT, przez OVHcloud AI Endpoints):**
   - Sprawdzono katalog `/v1/models` OVHcloud (`https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`): dostępne są trzy modele embeddingów (`bge-m3`, `bge-multilingual-gemma2`, `Qwen3-Embedding-8B`). Wybrano `bge-m3`.
   - Ustalono ograniczenie API OVHcloud `/v1/embeddings`: przy paczce 64 tekstów serwer zwraca `HTTP 400 Bad Request`, natomiast przy `batch_size = 16` wszystkie zapytania przechodzą z `HTTP 200`. Wektory z API również normalizowano L2 i zapisywano w lokalnym cache (`cache_bge-m3.json`), aby nie odpytywać sieci wielokrotnie o tę samą frazę.

### Krok 2. Przygotowanie Testu 1 („Wycięta ściągawka” – ablation na 60 prawdziwych `przelew.pdf` UZP)

W pamięci skopiowano konfigurację `config/typy/przelew.yaml` i **usunięto z niej 46 synonimów**, zostawiając dokładnie po **1 kanonicznej nazwie na każde z 6 pól**:
- `przelew_bankowy.data_operacji`: `["data operacji"]` (usunięto: `data transakcji`, `data realizacji`, `data wykonania`, `data księgowania`, `data obciążenia`, `w dniu`)
- `przelew_bankowy.kwota`: `["kwota operacji"]` (usunięto: `kwota`, `wartość`, `w kwocie`)
- `przelew_bankowy.z_rachunku`: `["rachunek nadawcy"]` (usunięto 10 synonimów, w tym `rachunek obciążany`, `z rachunku`, `zleceniodawca`, `płatnik`, `nadawca`, `dane nadawcy`)
- `przelew_bankowy.na_rachunek`: `["rachunek odbiorcy"]` (usunięto 11 synonimów, w tym `na rachunek`, `rachunek uznawany`, `beneficjent`, `odbiorca`, `adresat`, `dane odbiorcy`)
- `przelew_bankowy.numer_transakcji`: `["numer transakcji"]` (usunięto 9 synonimów, w tym `nr ref.`, `numer referencyjny`, `id transakcji`, `numer operacji`)
- `przelew_bankowy.tytul`: `["tytuł przelewu"]` (usunięto 8 synonimów, w tym `tytuł operacji`, `opis operacji`, `tytułem`, `szczegóły płatności`)

Zadanie w Teście 1: na 60 prawdziwych przelewach UZP (gdzie banki używają usuniętych nazw) model wektorowy zna tylko te 6 pojedynczych nazw i musi sam rozpoznać właściwe miejsca w tekście.

### Krok 3. Przygotowanie Testu 2 (100 nowych ślepych wariantów etykiet, 5 210 dokumentów)

Zamrożono oryginalne pliki `config/typy/*.yaml`. Zdefiniowano **100 zupełnie nowych wariantów etykiet** w 16 grupach (żaden z tych napisów nie występuje w `config/typy/*.yaml`):

1. `data_operacji` (8): `Dzień realizacji`, `Data waluty`, `Zrealizowano dnia`, `Dzień księgowania`, `Data zlecenia`, `Termin operacji`, `Zaksięgowano dnia`, `Data płatności`
2. `kwota` (8): `Suma przelewu`, `Obciążenie kwotą`, `Należność ogółem`, `Razem kwota`, `Wartość przelewu`, `Kwota płatności`, `Suma transakcji`, `Wartość operacji`
3. `z_rachunku` (8): `Konto źródłowe`, `Obciążono rachunek`, `Rachunek winien`, `Właściciel rachunku`, `Konto obciążane`, `Z konta bankowego`, `Strona płacąca`, `Podmiot zlecający`
4. `na_rachunek` (8): `Konto docelowe`, `Uznano rachunek`, `Rachunek ma`, `Konto beneficjenta`, `Na konto bankowe`, `Strona odbierająca`, `Podmiot otrzymujący`, `Rachunek wierzyciela`
5. `tytul` (8): `Treść przelewu`, `Informacja dla odbiorcy`, `Adnotacja bankowa`, `Przedmiot płatności`, `Cel przelewu`, `Komentarz do operacji`, `Treść operacji`, `Uwagi do przelewu`
6. `numer_transakcji` (8): `Kod operacji`, `ID płatności`, `Sygnatura bankowa`, `Klucz potwierdzenia`, `Numer potwierdzenia`, `Kod referencyjny`, `Oznaczenie transakcji`, `Identyfikator płatności`
7. `^Odwołujący:` (6): `Strona odwołująca:`, `Wnoszący odwołanie:`, `Podmiot odwołujący:`, `Skarżący wykonawca:`, `Wykonawca wnoszący odwołanie:`, `Strona skarżąca:`
8. `^Zamawiający:` (6): `Podmiot zamawiający:`, `Organ zamawiający:`, `Jednostka zamawiająca:`, `Inwestor zamawiający:`, `Instytucja zamawiająca:`, `Strona zamawiająca:`
9. `\bNIP:` (6): `Identyfikator podatkowy:`, `Nr identyfikacji podatkowej:`, `Identyfikator NIP:`, `Podatkowy nr id.:`, `Kod podatkowy NIP:`, `Rejestr NIP:`
10. `\bKRS:` (6): `Rejestr przedsiębiorców:`, `Nr w rejestrze przedsiębiorców:`, `Wpis do KRS:`, `Rejestr sądowy KRS:`, `Identyfikator KRS:`, `Kod KRS:`
11. `\bREGON:` (5): `Numer statystyczny GUS:`, `Identyfikator REGON:`, `Rejestr GUS REGON:`, `Kod statystyczny REGON:`, `Nr ewidencyjny REGON:`
12. `\bPESEL:` (5): `Numer ewidencyjny PESEL:`, `Identyfikator PESEL:`, `Ewidencja PESEL:`, `Kod osobisty PESEL:`, `Nr PESEL osoby:`
13. `nr referencyjny sprawy:` (6): `identyfikator postępowania:`, `oznaczenie zamówienia:`, `kod postępowania:`, `sygnatura zamówienia:`, `znak zamówienia publicznego:`, `numer ewidencyjny sprawy:`
14. `numer ogłoszenia TED:` (4): `publikacja w Suplemencie Dz.U. UE:`, `ogłoszenie w Dz.U. S:`, `identyfikator publikacji TED:`, `wpis w Dzienniku Urzędowym UE:`
15. `^Mocodawca:` (4): `Reprezentowany podmiot:`, `Strona udzielająca pełnomocnictwa:`, `Upoważniający podmiot:`, `Podmiot reprezentowany:`
16. `reprezentowan[ay] przez:` (4): `zastępowany przez:`, `w imieniu którego występuje:`, `działający za pośrednictwem:`, `obsługiwany prawnie przez:`

Dla `odwolanie` i `pelnomocnictwo` (gdzie etykiety nie są osobną listą `etykiety:` w YAML, lecz są zaszyte w regexach) modelowi wektorowemu wolno było porównywać kandydatów z tekstu **wyłącznie z pojedynczą nazwą kanoniczną** (`"Odwołujący"`, `"Zamawiający"`, `"Mocodawca"`, `"NIP"`, `"KRS"`, `"REGON"`, `"PESEL"`, `"nr referencyjny sprawy"`, `"numer ogłoszenia TED"`, `"reprezentowany przez"` — zero synonimów). Po nałożeniu tych 100 podmian na 180 dokumentów treningowych powstało **5 210 zmienionych dokumentów**.

### Krok 4. Jak działał sam algorytm wyciągania z wektorami (Wersja A i Wersja B)

1. Najpierw uruchamiany jest zwykły etap 4 (`wyciagnij(tekst, typ)`).
2. Jeśli zostały puste pola, z tekstu dokumentu wycinani są kandydaci na etykiety:
   - w `przelew`: krótkie frazy (1–4 słowa bez cyfr) na początku linii przed `:`, końcem linii albo przed wartością (datą, kwotą, rachunkiem, identyfikatorem), których nie ma w znanych `etykiety` z YAML,
   - w `odwolanie` / `pelnomocnictwo`: frazy 1–5 słów zakończone dwukropkiem `:` (na początku lub w środku linii, z pominięciem skrótów adresowych `ul.`, `al.`, `tel.`).
3. Liczona jest macierz podobieństwa cosinusowego między kandydatami z tekstu a znanymi etykietami pól.
4. Przetestowano dwie wersje dopasowania:
   - **Wersja A (pierwsza próba – podmiana wszystkich przekraczających próg):** każdą frazę w dokumencie z `sim >= próg` podmieniano na kanoniczną etykietę najbliższego pustego pola i uruchamiano `wyciagnij()`. Wadą było to, że:
     - gdy kilka fraz w dokumencie przekroczyło próg (np. nagłówek banku miał `sim = 0.79`, a właściwa etykieta niżej `sim = 0.93`), `wyciagnij()` brał **pierwsze wystąpienie od góry tekstu** zamiast tego o najwyższym podobieństwie,
     - w `odwolanie` każde pismo ma legalne pola `null` (np. `numer_ted = null`, gdy zamówienie jest w BZP, albo `regon = null`), więc wektory uruchamiały się na każdym dokumencie i szukały etykiety dla pola, którego w dokumencie w ogóle nie było (co wygenerowało 2 221 FP).
   - **Wersja B (poprawiona – filtr obowiązkowych pól + Top-1 wg podobieństwa + Bramka):**
     - dla każdego brakującego pola kandydaci są sprawdzani w kolejności **malejącego podobieństwa cosinusowego** i wybierany jest tylko **jeden najlepszy kandydat (Top-1)**, za którym `wyciagnij()` z Bramką faktycznie znajduje poprawną wartość tego pola,
     - walidacja w `przelew`: wartość znaleziona wektorowo dla `na_rachunek` nie może być tym samym numerem rachunku co `z_rachunku` (i odwrotnie),
     - filtr obowiązkowych pól w `odwolanie`: kotwica jest szukana wektorowo tylko wtedy, gdy jej pole obowiązkowe jest puste (np. `numer ogłoszenia TED:` jest szukany wyłącznie wtedy, gdy zarówno `numer_ted`, jak i `numer_bzp` są `None`).

## Wynik – Test 1: „Wycięta ściągawka” (60 przelewów UZP, tylko 1 etykieta/pole)

| Metoda | F1 (wersja A) | **F1 (wersja B, z filtrem)** | TP | FP | FN | Czas (60 dok.) |
|---|---|---|---|---|---|---|
| **Tylko Regex (1 etykieta/pole, bez synonimów)** | 0.3900 | **0.3900** | 94 | 28 | 266 | 0,01 s |
| **Regex + Local `multilingual-e5-small` (CPU, próg 0.80)** | 0.6124 | **0.6486** *(+0.2586)* | 227 | 113 | 133 | **0,45 s** *(z cache 0,05 s)* |
| **Regex + OVHcloud `bge-m3` (API UE, próg 0.60)** | 0.6770 | **0.7132** *(+0.3232)* | 235 | 64 | 125 | 24,75 s *(z cache 0,03 s)* |

Dlaczego przy 1 etykiecie na pole F1 dochodzi do `0.7132`, a nie `0.99`: gdy w konfiguracji jest tylko `rachunek nadawcy` i `rachunek odbiorcy`, a w PDF banku stoi pojedyncze słowo `Zleceniodawca` albo `Beneficjent` (bez słowa `rachunek`), wektory odzyskują ponad połowę utraconych pól (+141 TP z 266 FN), ale czasem mylą kierunek przelewu lub nie przekraczają progu dla pojedynczego słowa.

## Wynik – Test 2: 100 nowych ślepych wariantów etykiet (5 210 dokumentów)

| Metoda | F1 razem (wersja A) | **F1 razem (wersja B)** | `przelew` | `odwolanie` | `pelnomocnictwo` | TP | FP | FN | Czysty czas embeddingów (428 fraz) |
|---|---|---|---|---|---|---|---|---|---|
| **Obecny Regex (bez wektorów)** | 0.9270 | **0.9270** | 0.8869 | 0.9392 | 1.0000 | 57 120 | 491 | 8 500 | 0,00 s |
| **Regex + Local `multilingual-e5-small` (CPU, próg 0.80)** | 0.9554 | **0.9624** *(+0.0354)* | **0.9391** | **0.9699** | 1.0000 | 61 907 | 1 124 | 3 713 | **0,98 s** (ONNX CPU) |
| **Regex + OVHcloud `bge-m3` (API UE, próg 0.64)** | 0.9611 | **0.9634** *(+0.0364)* | **0.9385** | **0.9715** | 1.0000 | 61 917 | 995 | 3 703 | 69,73 s (HTTP, batch 16) |
| **Regex + OVHcloud `bge-m3` (API UE, próg 0.68)** | 0.9603 | **0.9626** *(+0.0356)* | 0.9376 | 0.9706 | 1.0000 | 61 689 | **864** | 3 931 | *(z cache 0,00 s)* |

## Skąd biorą się pozostałe błędy (ok. 3 700 FN w Teście 2)

Analiza najczęstszych błędów po etapie wektorowym pokazała dwie główne przyczyny:
1. **3-literowe skróty wobec pełnych nazw bez skrótu:** w teście jako opis kotwicy podano wyłącznie jedno słowo (`"NIP"`, `"KRS"`, `"REGON"`). Wektor samego skrótu `"NIP"` ma niskie podobieństwo cosinusowe (~0.52) do pełnych fraz `"Identyfikator podatkowy:"` czy `"Nr identyfikacji podatkowej:"` i przegrywa z etykietami zawierającymi słowo `"nr"` (`"nr referencyjny sprawy"`). Dodanie rozwinięcia skrótu w opisie pola (`"numer identyfikacji podatkowej NIP"`, `"Krajowy Rejestr Sądowy KRS"`) usuwa tę lukę.
2. **Inny rdzeń słowa dla strony odwołującej:** pojedyncze słowo `"Odwołujący"` ma niższe podobieństwo do `"Skarżący wykonawca:"` i `"Strona skarżąca:"` niż do wariantów z rdzeniem `odwoł-` (`"Wnoszący odwołanie:"`, `"Strona odwołująca:"`, które wektory rozpoznały w 100%).

## Wnioski

1. **Wektory etykiet + Bramka działają znacznie lepiej niż GLiNER2:** zamiast `F1 = 0.551` i 14,8 s na jedno odwołanie (`docs/badania/gliner2.md`), wyszukiwanie samej etykiety wektorem i wyciąganie wartości regexem z Bramką podnosi F1 na 100 nieznanych etykietach z **0.9270 do 0.9624–0.9634**, odzyskując **ok. 4 800 z 8 500** utraconych pól.
2. **Porównanie modeli:**
   - **OVHcloud `bge-m3` (API UE):** najwyższa dokładność w obu testach (`0.7132` vs `0.6486` w Teście 1 oraz `0.9634` vs `0.9624` w Teście 2), mniej fałszywych trafień (`FP`), zero dodatkowych bibliotek i wag lokalnie, pełna zgodność z wymogiem hostingu modelu u dostawcy w UE. Wywoływany tylko wtedy, gdy w dokumencie zostało puste pole obowiązkowe (1 zapytanie batch na dokument, ok. 0,3 s).
   - **Local `multilingual-e5-small` (ONNX CPU):** w Teście 2 daje niemal identyczny wynik (`0.9624`), jest bardzo szybki na CPU (**0,98 s** na 428 unikalnych fraz) i działa bez sieci, ale wymaga pliku `model.onnx` (470 MB) oraz potwierdzenia od UZP, że lokalny model embeddingów nie podlega zakazowi prywatnego hostingu LLM.
3. **Zasady wdrożenia etapu 6:**
   - Uruchamiać wyłącznie dla pustych pól obowiązkowych (z uwzględnieniem wykluczania `numer_ted` przy obecnym `numer_bzp` oraz `z_rachunku != na_rachunek`).
   - Dla skrótów (`NIP`, `KRS`, `REGON`, `PESEL`) w etykietach bazowych trzymać zarówno skrót, jak i jego oficjalne rozwinięcie.
