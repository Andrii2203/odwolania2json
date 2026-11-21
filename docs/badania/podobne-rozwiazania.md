# Podobne rozwiązania i pomysły do wzięcia (2026-11-21)

Wyszukiwanie w internecie, Claude. Bez kodu, tylko notatki.

## invoice2data: ten sam pomysł co nasz

Biblioteka Python (MIT), od lat wyciąga dane z faktur PDF szablonami YAML. Szablon ma:

- `keywords`: wszystkie muszą pasować (regex), żeby użyć szablonu; u nas `znaczniki` z progiem `PROG`.
- `exclude_keywords`: jeśli któryś pasuje, szablon odpada; u nas `wykluczenia`.
- `fields`: pole -> regex, w grupie tylko wartość; `type` (np. float), formaty dat; u nas `wzorce`, `format`.
- `--debug`: pokazuje, które słowa kluczowe pasowały i jaki tekst widzi program.
- Nowa wersja (invoice-x 1.0): opcjonalny LLM, gdy szablon nie pasuje, i `--new-template --ai`: LLM pisze szablon YAML dla nowego dokumentu.

Do wzięcia:

1. Tryb wyjaśnień jak `--debug` (UZP premiuje „transparentność procesu ekstrakcji”): dla każdego pola fragment tekstu i nazwa reguły.
2. Pomysł na finał: nowy typ dokumentu jako YAML, a szkic YAML może przygotować LLM (raz, przy konfiguracji), nie przy każdym dokumencie.

Źródła: https://invoice2data.readthedocs.io/latest/tutorial.html, https://github.com/invoice-x/invoice2data, https://pypi.org/project/invoice2data

## OCR gubi polskie znaki: przyczyna, nie łatki

- Silniki OCR trenowane głównie na angielskim mylą ą/a, ł/l, ó/o (przegląd polskiego OCR, codesota.com).
- Nasze `poprawki_ocr` ze słowami („odwolania” -> „odwołania”) to łatka: działa tylko dla wpisanych słów.
- Przyczynę leczy korekta słownikiem języka polskiego: słowo z OCR bez polskich znaków zamieniamy na słowo ze słownika, które różni się tylko znakami diakrytycznymi. Słownik: sjp.pl w formacie Hunspell, wersja na licencji CC BY 4.0 (pakiet Debian/Arch `hunspell-pl` jest GPL).
- PolEval 2021 miał zadanie korekty OCR dla polskiego (dane i rozwiązania publiczne).
- Brak gotowego porównania Tesseract / PaddleOCR / RapidOCR na polskich znakach; trzeba zmierzyć na naszych 30 skanach.

Źródła: https://codesota.com/polish-ocr, https://packages.debian.org/sid/hunspell-pl, https://archlinux.org/packages/extra/any/hunspell-pl/, https://maxhalford.github.io/blog/ocr-spelling-correction-is-hard

## Docling, Unstructured

Rozkładają PDF na tekst, tabele i układ (dla RAG). Nie wyciągają pól do naszego JSON. Docling używa modeli (cięższy na komputerze bez GPU). Dla nas nie zastępują reguł; ewentualnie lepszy tekst ze skanów.

Źródła: https://docling-project.github.io/docling/concepts/OCR/, https://www.nutrient.io/blog/docling-alternatives/

## Sprawdzanie na nowych dokumentach bez milionów plików

- Liczy się różnorodność układów, nie liczba plików. Miliony nie są potrzebne ani dostępne (brak wzorców JSON).
- Testy metamorficzne: zmiana formatu dokumentu nie powinna zmieniać wyniku. Bierzemy dokument z danymi, podmieniamy wartości (nazwy, NIP, daty), etykiety („NIP:” -> „NIP Odwołującego:”), kolejność bloków i podział linii; wiemy, co wstawiliśmy, więc znamy poprawny JSON. Setki, tysiące wariantów wystarczą.
- FlexDoc (2025): syntetyczne dokumenty z parametrami układu podniosły F1 ekstrakcji do 11 punktów.
- Obce dokumenty: kilkaset publicznych PDF (wyroki KIO, ogłoszenia TED/BZP, faktury) i sprawdzenie, że żaden nie dostaje typu.

Źródła: https://arxiv.org/html/2510.02133v1, https://arxiv.org/pdf/2607.27648, https://doaj.org/article/2549c35b1b2441fabcb98e1a6dc40f9d
