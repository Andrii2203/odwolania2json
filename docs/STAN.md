# Стан

Оновлено: 2026-11-21, Argon.

## Зроблено
- Репо (приватне): https://github.com/Andrii2203/odwolania2json. Python 3.13.
- `AGENTS.md` (+ `CLAUDE.md`, `GEMINI.md`), ADR-0001…0006, `docs/testy.md`.
- Walking skeleton: CLI `input/ → output/`, класифікація з YAML, `process()` — спільна для CLI і GUI. Тести T1, T2 зелені.
- Компас `tools/ocena_f1.py`: тип правильний 180/180, **F1 = 0.000** (поля ще порожні).
- Дослідження LLM в ЄС (`docs/badania/llm-ue.md`): порівняно Mistral AI, Scaleway, OVHcloud, IONOS (рекомендовано `Mistral Small 3.1/3.2 24B`, Apache 2.0; для локальної розробки на RTX 5060 8 ГБ — `ministral-3:8b` або `qwen2.5:7b-instruct` у Q4_K_M через Ollama).
- Дослідження OCR на CPU (`docs/badania/ocr.md`): порівняно RapidOCR, docTR, Tesseract + `pypdfium2` (рекомендовано `pypdfium2` + `rapidocr` з `onnxruntime` і моделлю PP-OCRv5 `LangRec.LATIN`, Apache 2.0, ставиться суто через `pip`).

## План
| Коли | Хто | Що |
|---|---|---|
| сб до 20:00 | Користувач | Чернетка в HackTribe (посилання на репо вище) |
| сб вечір | Claude | Поля правилами: `przelew` → `pelnomocnictwo` → `odwolanie` |
| сб вечір | [Argon] | ~~Дослідження LLM в ЄС → `docs/badania/llm-ue.md`~~ (готово) |
| сб вечір | [Argon] | ~~Дослідження OCR → `docs/badania/ocr.md`~~ (готово) |
| сб ніч | [Argon] | GUI за ADR-0006: `gui.bat`, `requirements-gui.txt`, `odwolania2json/gui.py`, лише виклик `process()` |
| сб ніч | Claude | LLM для полів, яких не беруть правила (ADR-0004); OCR (ADR після дослідження) |
| нд 7:00–9:30 | [Argon] | Презентація PDF ≤ 10 МБ за ADR-0006; `README.md` польською |
| нд 9:30–10:30 | Claude + Користувач | Фінальний прогін F1, перевірка `start.bat` на чистій папці, здача |
| нд 11:00 | — | Дедлайн |

### [Argon] Дослідження LLM в ЄС
Mistral, Scaleway, OVHcloud, IONOS. Для кожного: які моделі з відкритими вагами **і ліцензією без обмежень** (Apache 2.0 / MIT), ціна за 1 млн токенів, безкоштовний ліміт, чи сервер і компанія в ЄС, чи безкоштовний план використовує дані для навчання, OpenAI-сумісний API. З посиланнями.
Окремо: чи хостить хтось із них **Qwen3.5-4B** або **Gemma 4 E4B** (вони в нас є локально, ADR-0004), і які ліцензії в цих двох моделей.

### [Argon] Дослідження OCR
Для сканів на CPU, ставиться через `pip`, без окремих програм: RapidOCR, docTR, Tesseract (`pytesseract` — потребує програми), рендер сторінок через `pypdfium2`. Для кожного: ліцензія, розмір встановлення, якість для польської. З посиланнями.

## Відкриті питання
- Як UZP рахує F1 — не блокує (ADR-0005).
- Локальні прогони: `E:\call to ai\tools\llama.cpp\llama-server.exe` + `models\brain\Qwen3.5-4B-Q8_0.gguf` на RTX 5060 (ADR-0004).
