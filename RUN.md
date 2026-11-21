# Uruchomienie

Komenda (z katalogu `/opt/solution`):

```
sh uruchom.sh
```

- Wejście: wszystkie PDF z `input/` (także w podkatalogach). Wynik: JSON w `output/` o tej samej ścieżce i nazwie (`input/a/b.pdf` -> `output/a/b.json`).
- Obcy, pusty albo uszkodzony PDF: plik z `{}`.
- Program kończy się sam, bez pytań.
- Usługi zewnętrzne: brak. Bez LLM i bez API; OCR (RapidOCR) działa lokalnie na CPU. Plik `.env` nie jest potrzebny.
- Instalacja (raz, na tej maszynie już wykonana): `sh instaluj.sh`. Python 3.13 i zależności są w katalogu projektu (`.python/`, `.venv/`).
