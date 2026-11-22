# Potok przetwarzania (ADR-0012)

Każdy dokument przechodzi te same etapy. Każda wartość, skądkolwiek pochodzi (regex, wektory, LLM, inny dokument sprawy), przechodzi tę samą bramkę (etap 5) i musi być dosłownie w tekście dokumentu. Niczego nie wymyślamy.

Etapy podłączamy po jednym. Etap zostaje tylko wtedy, gdy pomiar pokazał wyższy F1. Stan każdego etapu jest w tabeli niżej; zmieniamy ją razem z kodem.

## Schemat

```
PDF
 0. Wejście: pusty / uszkodzony / skan -> OCR                  [mechanika]
 1. Tekst: pypdf, OCR, poprawki OCR słownikiem sjp.pl          [mechanika, słownik]
 2. Widok do szukania: małe litery, bez znaków diakrytycznych, [mechanika]
    spacje, przeniesienie "postępo-\nwania" -> "postępowania",
    mapa pozycji do oryginału
 3. Klasyfikacja: znaczniki (+ wektor dokumentu, jeśli pomiar  [mechanika / wektory]
    pokaże, że można usunąć "oficjalna nazwa")
 4. Pola: regex z YAML                                         [mechanika]
 5. BRAMKA: format, długość, cięcie na stopach,                [mechanika, JSON Schema w YAML]
    "w nazwie nie ma KRS:/NIP:/ul."
 6. Puste pola -> wektory etykiet -> regex za etykietą -> BRAMKA [wektory]
 7. Nadal puste / podejrzane -> LLM -> "czy jest dosłownie      [LLM]
    w tekście?" -> BRAMKA
 8. Kontekst sprawy: wartości z innych dokumentów tej samej     [mechanika]
    sprawy jako kandydaci (NIP Odwołującego z odwołania
    szukamy w pełnomocnictwie) -> tylko jeśli jest w tekście
 9. Porządki: mianownik (Morfeusz2), daty ISO, słowo -> id,     [mechanika, słownik]
    duplikaty ("999-928-40-65" = "9999284065")
10. JSON + dziennik "skąd każda wartość" (etap, reguła,         [przejrzystość dla UZP]
    fragment tekstu)
```

## Zasady

1. Wartość wycinamy z oryginału. Małe litery i brak polskich znaków są tylko w widoku do szukania (etap 2); pozycje z widoku przenosimy na oryginał. UZP porównuje dokładnie: `"Belmoria Rozwiązania S.A."`, nie `"belmoria rozwiązania s.a."`.
2. `null` bywa poprawny: wartości w dokumencie nie ma. Etapy 6–8 wypełniają pole tylko powyżej progu i tylko wartością, która jest w tekście.
3. Kolejność od taniego do drogiego: regex, wektory (lokalnie), LLM (sieć, koszt, wynik niepowtarzalny).
4. Bez sieci (LLM niedostępny) program działa: etapy 0–6 i 8–10.
5. Każdy etap ma przełącznik w `config/ustawienia.yaml` (`etapy`), żeby zmierzyć F1 z nim i bez niego.
6. Dziennik (etap 10) to to, co widzi pracownik: dla każdego pola etap, reguła i fragment tekstu. Ten sam dziennik służy do szukania błędów. Dziennik nie trafia do `output/` (żeby nie mylić oceny), tylko do GUI i do `--wyjasnij`.

Przykład dziennika dla jednego pola:

```
Odwolujacy[0].nazwa = "Belmoria Rozwiązania S.A."
  etap 4  regex     odwolanie.yaml: Odwolujacy[].nazwa, wzorzec 1
  etap 5  bramka    ucięte przed "ul." (stop: adres)
  tekst             "Odwołujący:\nBelmoria Rozwiązania S.A. ul. Zaczarowana 78, 90-803 Łódź"
```

## Stan etapów

| Etap | Stan | Co jest | Czego brak |
|---|---|---|---|
| 0 | jest | skan -> OCR (ADR-0007), 3 pierwsze strony i ostatnia, limit czasu OCR, JSON zaraz po dokumencie (ADR-0018); `.PDF` wielkimi (T20); błąd jednego pliku nie zatrzymuje reszty (T7); obcy, pusty, uszkodzony -> `{}` (ADR-0013) | |
| 1 | częściowo | pypdf, RapidOCR, `poprawki_ocr` (łatki dla wpisanych słów) | słownik sjp.pl zamiast łatek |
| 2 | częściowo | klasyfikacja bez wielkości liter i polskich znaków; etykiety i nagłówki stron bez wielkości liter; `warianty_liter` | przeniesienia wyrazów; jeden widok dla wszystkich etapów z mapą pozycji |
| 3 | jest | `znaczniki`, `PROG`, `wykluczenia` | wektor dokumentu (opcja) |
| 4 | jest | `pola` w `config/typy/*.yaml` (ADR-0008, ADR-0010) | |
| 5 | częściowo | `format` (cyfry, data, liczba, tekst, bez_spacji); tekst kończy się na następnej etykiecie (`{STOP}`); etykieta innego pola nie jest wartością (T10); `utnij` w YAML: nazwa kończy się przed adresem, numerem, e-mailem (T13, ADR-0015) | sekcja, gdy nagłówek strony jest w środku linii; tytuł przelewu w środku linii; sumy kontrolne NIP/REGON odpadają: dane UZP ich nie spełniają (144/218 NIP) |
| 6 | zbadane | GLiNER2 odrzucony: F1 0.551 (`docs/badania/gliner2.md`); ślepy pomiar wektorów etykiet (Test 1 bez synonimów: 0.3900 -> 0.6486 `e5-small` / 0.7132 `bge-m3`; Test 2 na 100 nowych etykietach: 0.9270 -> 0.9624 `e5-small` / 0.9634 `bge-m3`, `docs/badania/wektory-etykiet.md`) | podłączenie do potoku (po decyzji: lokalny `multilingual-e5-small` ONNX vs OVHcloud `bge-m3`) |
| 7 | nie ma | klucz OVHcloud działa (ADR-0004) | wywołanie, sprawdzenie „wartość jest w tekście” |
| 8 | jest | klucz `kontekst` w pliku typu: puste pole z innego dokumentu sprawy, jeśli wartość jest w tekście (T14, ADR-0016) | mianownik z innego dokumentu; wybór między kandydatami |
| 9 | częściowo | daty ISO, słownik słowo -> id (ADR-0010), rachunek z kodem kraju (ADR-0014, T15), powtórzenie po wartości po formacie (NIP z myślnikami = bez, ADR-0019) | mianownik (Morfeusz2) |
| 10 | jest | JSON w `output/`; dziennik: `--wyjasnij` w CLI i tabela „Skąd każda wartość” w GUI (T12) | wpisy bramki (etap 5), gdy powstanie |

Do oddania (22.11 11:00, ocena na maszynie UZP z 2 vCPU, ADR-0017) robiliśmy z kolumny „dalej” tylko: etap 0 (straż czasu) i etap 9 (rachunek z dowolnym kodem kraju, ten sam NIP z myślnikami i bez); oba zrobione 22.11. Reszta odłożona; etap 7 (LLM) nie: lokalne rozwiązanie ma 20 pkt za model, API dodaje czas. Plan: `docs/STAN.md`.

## Jak sprawdzić etap

```
.venv\Scripts\python tools\ocena_f1.py              # 60 spraw treningowych
.venv\Scripts\python tools\ocena_f1.py --dane data\uzp\dane\skany\potwierdzenia data\uzp\dane\skany\pelnomocnictwa data\uzp\dane\skany\odwolania
.venv\Scripts\python tools\warianty.py --przyklady  # warianty dokumentów (ADR-0011)
.venv\Scripts\python tools\ocena_f1.py --dane data\obce   # obce: ma być 0 z JSON
```
