# Дослідження OCR для сканів на CPU

Дата: 2026-11-21

## Вимоги проєкту
- Тестовий ПК журі — **офісний, без GPU** (робота виключно на CPU).
- Встановлення — автоматично через `pip install -r requirements.txt` під час запуску `start.bat`, **без потреби вручну ставити зовнішні системні програми** (Tesseract `.exe`, Poppler тощо).
- Лише **open source** з дозвільною ліцензією (Apache 2.0 / MIT / BSD).
- Висока якість розпізнавання **польської мови** (діакритичні знаки: `ą, ć, ę, ł, ń, ó, ś, ź, ż`, юридичний текст KIO, таблиці та банківські квитанції).

---

## 1. Рендер сторінок PDF у зображення: `pypdfium2`

Оскільки `pypdf` вміє лише витягувати текстовий шар і не рендерить PDF-сторінки в растр, а `pdf2image` вимагає встановленої системної утиліти `poppler`, для рендеру сканів потрібен самодостатній пакет з готовим бінарним wheel.

| Параметр | `pypdfium2` |
|---|---|
| **Що це** | Python-обгортка над рушієм Google PDFium (постачається з прекомпільованим бінарником PDFium всередині wheel для Windows/Linux/macOS) |
| **Ліцензія** | **Apache 2.0 / BSD-3-Clause** (сумісна з вимогами UZP) |
| **Встановлення** | `pip install pypdfium2 pillow` (жодних зовнішніх програм) |
| **Розмір встановлення** | **~5–15 МБ** (wheel з бінарником PDFium) + `Pillow` (~10 МБ) |
| **Швидкість на CPU** | Дуже висока (~30–80 мс на сторінку A4 при 200–300 DPI) |
| **Посилання** | PyPI: https://pypi.org/project/pypdfium2/<br>GitHub: https://github.com/pypdfium2-team/pypdfium2 |

---

## 2. Порівняння рушіїв OCR на CPU

| Критерій | **RapidOCR (`rapidocr` + `onnxruntime`)** | **docTR (`python-doctr` / `onnxtr`)** | **Tesseract (`pytesseract`)** |
|---|---|---|---|
| **Зовнішні програми** | **Не потрібні** (чистий `pip`) | **Не потрібні** (чистий `pip`) | **Потрібна програма** `Tesseract-OCR` у системі + файл `pol.traineddata` |
| **Ліцензія** | **Apache 2.0** (і бібліотека RapidOCR, і моделі PaddleOCR PP-OCRv4/v5) | **Apache 2.0** (Mindee docTR) | **Apache 2.0** (`pytesseract`, рушій Tesseract і `tessdata`) |
| **Розмір встановлення (`pip` + моделі)** | **~150–220 МБ** (`onnxruntime` ~55 МБ, `opencv-python-headless` ~85 МБ, моделі PP-OCRv5 mobile det+cls+latin_rec ~20 МБ) | **`python-doctr[torch]`:** **~800 МБ – 1.5 ГБ** (тягне `torch` + `torchvision` + моделі ~100 МБ)<br>**`onnxtr`:** ~250 МБ | `pytesseract`: **< 1 МБ**, але системний інсталятор Tesseract на Windows: **~120–150 МБ** |
| **Якість для польської мови** | **Висока** із моделлю **`latin` (PP-OCRv5)**. Словник `ppocrv5_latin_dict.txt` включає всі польські літери (`ą, ć, ę, ł, ń, ó, ś, ź, ż`). Добре тримає таблиці, штампи і нахилений скан | **Низька / середня з коробки для польської.** Базовий словник `latin` у docTR орієнтований на англійську/французьку і часто губить або підмінює польські знаки (`ł → l`, `ą → a`, `ż → z`) без донавчання | **Висока** на чистих рівних сканах із пакетом `-l pol`, але гірше за PaddleOCR/RapidOCR справляється зі складними таблицями, печатками та шумом |
| **Швидкість на CPU (1 стор. A4)** | **~0.8–2.0 с** (ONNX Runtime на CPU, моделі `mobile`) | **~2.0–4.5 с** (PyTorch на CPU) | **~1.0–2.5 с** |

---

## 3. Детальний розбір варіантів

### А. RapidOCR (`rapidocr` + `onnxruntime`) — Рекомендовано
- **Як працює:** Конвертовані у формат ONNX моделі Baidu **PaddleOCR (PP-OCRv4 / PP-OCRv5)**, що запускаються через легкий `onnxruntime` без важкого фреймворку `paddlepaddle` чи `torch`.
- **Важливий нюанс для польської мови:**
  За замовчуванням RapidOCR завантажує китайсько-англійську модель (`ch`), яка не знає польської діакритики. Щоб увімкнути польську мову, при ініціалізації треба явно вказати **`LangRec.LATIN`** та **`OCRVersion.PPOCRV5`** (у версії `rapidocr >= 3.10.0` модель `latin_PP-OCRv5_mobile_rec.onnx` і латинський словник із польськими літерами завантажуються автоматично під час першого виклику).
- **Посилання:**
  - PyPI: https://pypi.org/project/rapidocr/
  - Документація та список мов: https://rapidai.github.io/RapidOCRDocs/
  - GitHub: https://github.com/RapidAI/RapidOCR

### Б. docTR (`python-doctr`)
- **Як працює:** Двоетапний пайплайн (DBNet/FAST для детекції + CRNN/ViTSTR для розпізнавання) від компанії Mindee.
- **Чому не підходить як основний:**
  1. Стандартне встановлення `pip install "python-doctr[torch]"` тягне `PyTorch` (~800+ МБ).
  2. Стандартні претреновані моделі розпізнавання в docTR навчалися на базовому західноєвропейському словнику (англійська, французька, німецька) і не містять повного набору польських літер (`ą, ć, ę, ł, ń, ś, ź, ż`) у базовому `VOCABS["french"]` / `VOCABS["latin"]`, через що польські прізвища й назви міст розпізнаються з помилками.
- **Посилання:**
  - PyPI: https://pypi.org/project/python-doctr/
  - GitHub: https://github.com/mindee/doctr
  - Документація словників: https://mindee.github.io/doctr/modules/datasets.html

### В. Tesseract (`pytesseract`)
- **Як працює:** Класичний C++ рушій Tesseract 5 (LSTM) з мовним файлом `pol.traineddata`.
- **Чому не підходить як основний для `start.bat`:**
  - `pip install pytesseract` ставить лише тонку Python-обгортку, яка викликає бінарник `tesseract.exe` через `subprocess`.
  - Якщо на тестовому ПК UZP не встановлено `Tesseract-OCR` у `PATH` (або не доставлено мовний пакет `pol.traineddata`), програма впаде з `TesseractNotFoundError`. Вимога конкурсу — самодостатній запуск через `start.bat` та `requirements.txt`.
- **Посилання:**
  - PyPI: https://pypi.org/project/pytesseract/
  - Tesseract GitHub: https://github.com/tesseract-ocr/tesseract
  - Мовні моделі (`pol.traineddata`): https://github.com/tesseract-ocr/tessdata_fast

---

## 4. Рекомендована архітектура та приклад коду

### Коли запускати OCR
Більшість PDF у тренувальному наборі UZP мають текстовий шар (`pypdf` читає їх за мілісекунди). Тому OCR викликаємо **лише як fallback**, якщо на сторінці `pypdf` повернув порожній або майже порожній текст (наприклад, `< 40` символів на сторінку).

### Приклад: `pypdfium2` + `rapidocr` (польська мова / `latin`)

Залежності в `requirements.txt`:
```text
pypdfium2>=4.30.0
rapidocr>=3.10.0
onnxruntime>=1.19.0
```

Код витягування тексту зі сканованої сторінки PDF:
```python
import numpy as np
import pypdfium2 as pdfium
from rapidocr import EngineType, LangRec, ModelType, OCRVersion, RapidOCR

_ocr_engine: RapidOCR | None = None


def get_ocr() -> RapidOCR:
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = RapidOCR(
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
    return _ocr_engine


def ocr_pdf_page(pdf_path: str, page_index: int = 0, dpi: int = 200) -> str:
    doc = pdfium.PdfDocument(pdf_path)
    page = doc[page_index]
    bitmap = page.render(scale=dpi / 72.0)
    img_np = bitmap.to_numpy()
    result = get_ocr()(img_np)
    if not result or not result.txts:
        return ""
    return "\n".join(result.txts)
```

### Порада перед здачею
Під час першого запуску `RapidOCR` завантажує ~20 МБ `.onnx`-моделей у кеш пакету (або вказану папку `models/`). Щоб програма працювала навіть без інтернету або без затримки на першому скані, варто або покласти 3 маленькі файли моделей (`det`, `cls`, `latin_rec` ~20 МБ сумарно) у репозиторій/кеш, або прогріти ініціалізацію в `start.bat`.
