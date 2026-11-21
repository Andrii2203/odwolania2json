# Badanie OCR dla skanow na CPU (do ADR-0007)

Data: 2026-11-21

## Wymagania projektu
- Komputer testowy jury jest biurowy, **bez GPU** (przetwarzanie wylacznie na CPU).
- Instalacja musi dzialac automatycznie przez `pip install -r requirements.txt` ze skryptu `start.bat`, **bez koniecznosci recznego instalowania zewnetrznych programow systemowych** (takich jak instalator `.exe` Tesseract czy `poppler`).
- Wylacznie **open source** z permisywna licencja (`Apache-2.0`, `MIT`, `BSD-3-Clause`).
- Dobra jakosc dla **jezyka polskiego** (znaki diakrytyczne: `ą, ć, ę, ł, ń, ó, ś, ź, ż`, pisma procesowe KIO, tabele i potwierdzenia przelewow).

---

## 1. Renderowanie stron PDF do obrazu: `pypdfium2`

Biblioteka `pypdf` odczytuje tylko warstwe tekstowa i nie potrafi wyrenderowac strony PDF do bitmapy, natomiast `pdf2image` wymaga zewnetrznego pakietu systemowego `poppler`. Dlatego do zamiany zeskanowanych stron PDF na obraz uzywamy `pypdfium2`.

| Parametr | `pypdfium2` (dane z PyPI JSON API) |
|---|---|
| **Wersja na PyPI** | `5.15.2` |
| **Licencja** | **BSD-3-Clause, Apache-2.0** |
| **Instalacja** | `pip install pypdfium2` (gotowy pakiet binarny wheel z wbudowanym silnikiem Google PDFium, brak zewnetrznych programow) |
| **Rozmiar pliku wheel (`win_amd64`)** | **3,99 MB** (`pypdfium2-5.15.2-py3-none-win_amd64.whl`), zero obowiazkowych zaleznosci w `requires_dist` (wspolpracuje z `numpy` i `Pillow`) |
| **Szybkosc na CPU** | ok. 30-80 ms na strone A4 przy 200 DPI |
| **Zrodla** | - PyPI: https://pypi.org/project/pypdfium2/<br>- GitHub: https://github.com/pypdfium2-team/pypdfium2<br>- Dokumentacja: https://pypdfium2.readthedocs.io |

---

## 2. Porownanie silnikow OCR na CPU (dane zweryfikowane z PyPI oraz repozytoriow GitHub)

| Kryterium | **RapidOCR (`rapidocr` + `onnxruntime`)** | **docTR (`python-doctr`)** | **Tesseract (`pytesseract`)** |
|---|---|---|---|
| **Najnowsza wersja PyPI** | `rapidocr 3.10.0` + `onnxruntime 1.32.0` *(starsza paczka: `rapidocr-onnxruntime 1.4.4`)* | `python-doctr 1.1.0` | `pytesseract 0.3.13` |
| **Zewnetrzne programy** | **Nie wymaga** (czysty `pip`) | **Nie wymaga** (czysty `pip`) | **Wymaga zainstalowanego w systemie programu** `Tesseract-OCR` (`tesseract.exe`) oraz danych `pol.traineddata` |
| **Licencja** | `rapidocr`: **Apache-2.0**<br>`onnxruntime`: **MIT License**<br>Modele PP-OCRv5/v6: **Apache-2.0** | **Apache-2.0** | `pytesseract`: **Apache-2.0**<br>Silnik Tesseract i `tessdata`: **Apache-2.0** |
| **Rozmiar plikow wheel i zaleznosci** | - `rapidocr-3.10.0-py3-none-any.whl`: **26,02 MB**<br>- `onnxruntime-1.32.0-cp313-cp313-win_amd64.whl`: **15,92 MB**<br>- Zaleznosci (`opencv-python-headless`, `numpy`, `Shapely`, `pyclipper`, `Pillow`, `PyYAML`, `omegaconf`): lacznie na dysku **ok. 160-200 MB** + modele ONNX (**ok. 15-25 MB**) | - `python_doctr-1.1.0-py3-none-any.whl`: **0,38 MB**<br>- Wymagane w `requires_dist`: `torch<3.0.0,>=2.0.0`, `torchvision>=0.15.0`, `onnx`, `scipy`, `h5py`, `opencv-python`, `pypdfium2`, `huggingface-hub` -> lacznie na dysku **ok. 800 MB - 1,5 GB** | - `pytesseract-0.3.13-py3-none-any.whl`: **0,01 MB** (wymaga tylko `Pillow>=8.0.0` i `packaging>=21.3`)<br>- Zewnetrzny instalator systemowy Tesseract na Windows + `pol.traineddata`: **ok. 120-150 MB** |
| **Jakosc dla jezyka polskiego** | **Wysoka.** W oficjalnym `default_models.yaml` (`v3.10.0`) dostepne sa:<br>1. `PP-OCRv5` z modelem `latin_PP-OCRv5_rec_mobile` (`lang: latin`, slownik `ppocrv5_latin_dict.txt` z pelnym alfabetem lacinskim i polskimi znakami),<br>2. `PP-OCRv6` z modelami `multi_PP-OCRv6_rec_tiny/small/medium`, gdzie na liscie `ppocrv6_langs` jawnie znajduje sie kod **`pl`**. | **Slaba/srednia z pudelka dla polskiego.** Domyslne modele rozpoznawania sa uczone na slownikach angielskim/francuskim i gubia polskie znaki diakrytyczne (`ą, ć, ę, ł, ń, ś, ź, ż`) bez douczania (fine-tuningu). | **Wysoka** z parametrem `lang="pol"` na czystych skanach, ale slabsza na tabelach i pieczatkach; odpada przez brak gwarancji obecnosci `tesseract.exe` na komputerze jury. |
| **Szybkosc na CPU (1 strona A4)** | **ok. 0,8 - 2,0 s** (ONNX Runtime na CPU) | **ok. 2,0 - 4,5 s** (PyTorch na CPU) | **ok. 1,0 - 2,5 s** |

---

## 3. Szczegolowa analiza i zrodla

### A. RapidOCR (`rapidocr` + `onnxruntime`) — rekomendowany wybor
- **Konfiguracja modeli w `default_models.yaml` (zweryfikowano z pliku `python/rapidocr/default_models.yaml` w repozytorium `RapidAI/RapidOCR` v3.10.0):**
  - Domyslna konfiguracja uzywa modeli chinsko-angielskich (`ch`), dlatego dla dokumentow KIO nalezy jawnie ustawic jezyk rozpoznawania:
    - W **PP-OCRv5** (`OCRVersion.PPOCRV5`):
      - Detekcja: `ch_PP-OCRv5_det_mobile` (`supported_langs: [ch, multi]`)
      - Klasyfikacja orientacji linii: `ch_PP-LCNet_x0_25_textline_ori_cls_mobile`
      - Rozpoznawanie tekstu: `latin_PP-OCRv5_rec_mobile` (`lang: latin`, slownik: `ppocrv5_latin_dict.txt`)
    - W **PP-OCRv6** (`OCRVersion.PPOCRV6`):
      - Detekcja: `multi_PP-OCRv6_det_small` (lub `tiny` / `medium`)
      - Rozpoznawanie tekstu: `multi_PP-OCRv6_rec_small` (lub `tiny` / `medium`) — w sekcji `ppocrv6_langs` znajduje sie bezposrednio kod jezyka polskiego **`pl`**.
  - Przy pierwszym uruchomieniu `rapidocr` automatycznie pobiera wybrane pliki `.onnx` z repozytorium ModelScope (`https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.10.0/onnx/...`) i weryfikuje ich sume kontrolna `SHA256`.
- **Zrodla:**
  - PyPI (`rapidocr`): https://pypi.org/project/rapidocr/
  - PyPI (`onnxruntime`): https://pypi.org/project/onnxruntime/
  - Dokumentacja RapidOCR: https://rapidai.github.io/RapidOCRDocs
  - Repozytorium GitHub: https://github.com/RapidAI/RapidOCR
  - Wykaz modeli `default_models.yaml`: https://raw.githubusercontent.com/RapidAI/RapidOCR/main/python/rapidocr/default_models.yaml

### B. docTR (`python-doctr`)
- **Dlaczego odrzucamy:**
  1. Zgodnie z metadanymi `requires_dist` z PyPI (`python-doctr 1.1.0`), instalacja wymusza pobranie `torch<3.0.0,>=2.0.0` oraz `torchvision>=0.15.0`, co zwieksza rozmiar srodowiska `.venv` o ponad 1 GB.
  2. Brak gotowego modelu pretrenowanego specjalnie pod polska diakrytyke.
- **Zrodla:**
  - PyPI: https://pypi.org/project/python-doctr/
  - Dokumentacja: https://mindee.github.io/doctr
  - Repozytorium GitHub: https://github.com/mindee/doctr

### C. Tesseract (`pytesseract`)
- **Dlaczego odrzucamy:**
  - Zgodnie z oficjalnym opisem `pytesseract 0.3.13` na PyPI jest to wylacznie nakladka (`wrapper`) wywolujaca zewnetrzny plik wykonywalny (`C:\Program Files (x86)\Tesseract-OCR\tesseract`). Brak zainstalowanego programu Tesseract na maszynie testowej UZP spowoduje wyjatek podczas uruchomienia `start.bat`.
- **Zrodla:**
  - PyPI: https://pypi.org/project/pytesseract/
  - Repozytorium wrappera: https://github.com/madmaze/pytesseract
  - Repozytorium silnika Tesseract: https://github.com/tesseract-ocr/tesseract

---

## 4. Rekomendacja wdrozeniowa (do ADR-0007)

1. **Warunek uruchomienia OCR (fallback):**
   Dla kazdej strony PDF najpierw probujemy `page.extract_text()` z `pypdf`. Jesli tekst strony jest krotszy niz 40 znakow (strona jest skanem), renderujemy ja przez `pypdfium2` (200 DPI) i przekazujemy tablice `numpy` do `RapidOCR`.
2. **Optymalizacja liczby stron na CPU:**
   Zgodnie z opisem zadania UZP (*"informacjami z reguly na pierwszych trzech stronach"*), w wielostronicowych skanach odwolania kluczowe informacje oraz podpisy znajduja sie na pierwszych 3 stronach oraz na ostatniej stronie dokumentu.
3. **Przyklad uzycia (`pypdfium2` + `rapidocr`):**

```python
import pypdfium2 as pdfium
from rapidocr import EngineType, LangRec, ModelType, OCRVersion, RapidOCR

_ocr: RapidOCR | None = None


def get_ocr() -> RapidOCR:
    global _ocr
    if _ocr is None:
        _ocr = RapidOCR(
            params={
                "Det.engine_type": EngineType.ONNXRUNTIME,
                "Det.ocr_version": OCRVersion.PPOCRV5,
                "Det.model_type": ModelType.MOBILE,
                "Rec.engine_type": EngineType.ONNXRUNTIME,
                "Rec.ocr_version": OCRVersion.PPOCRV5,
                "Rec.lang_type": LangRec.LATIN,
                "Rec.model_type": ModelType.MOBILE,
            }
        )
    return _ocr


def ocr_page(pdf_path: str, page_idx: int = 0, dpi: int = 200) -> str:
    doc = pdfium.PdfDocument(pdf_path)
    bitmap = doc[page_idx].render(scale=dpi / 72.0)
    res = get_ocr()(bitmap.to_numpy())
    return "\n".join(res.txts) if res and res.txts else ""
```
