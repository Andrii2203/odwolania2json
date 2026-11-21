# Стан

Оновлено: 2026-11-21, Claude.

## Зроблено
- Репо, `AGENTS.md` (+ `CLAUDE.md`, `GEMINI.md`), ADR-0001…0004, `docs/testy.md`.
- Walking skeleton: CLI `input/ → output/`, класифікація з YAML. Тести T1, T2 зелені.
- Компас: `tools/ocena_f1.py` → тип правильний 180/180, **F1 = 0.000** (поля ще порожні).

## Далі
1. [Claude] Поля `przelew` (6 полів) правилами → F1 вгору. Потім `pelnomocnictwo`, `odwolanie`.
2. [Argon] Порівняти EU-постачальників LLM для ADR-0004: Mistral, Scaleway, OVHcloud, IONOS. Для кожного: які open-weight моделі, ціна, безкоштовний ліміт, чи сервер в ЄС, OpenAI-сумісний API. З посиланнями. Результат → `docs/badania/llm-ue.md`.
3. [Argon] OCR для сканів на CPU, що ставиться через `pip`: RapidOCR, Tesseract (`pytesseract`), docTR. Для кожного: ліцензія, розмір встановлення, якість для польської. Результат → `docs/badania/ocr.md`.
4. [Користувач] Python 3.13+; ключ API в ЄС; чернетка в HackTribe до 20:00.

## Відкриті питання
- Як UZP рахує F1: точний збіг? Порядок у списках (кілька Odwołujących)?
- OCR — яке рішення (ADR після п. 3).
