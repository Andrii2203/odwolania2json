# Odwołania2JSON — контекст для AI (Claude і Gemini/Argon)

HackNation 2026, завдання UZP «Odwołania2JSON». Здача: **нд 22.11.2026, 11:00**.
З користувачем говоримо українською і **на прикладах**.

## Що робимо
Програма бере PDF-документи справи до KIO і для кожного пише JSON.

```
input/case1/odwolanie.pdf  →  output/case1/odwolanie.json
{"OdwolanieKIO": {"miejscowosc": "Kraków", ...}, "Odwolujacy": [{"nip": "9995519382", ...}], ...}
```

Типи: `odwolanie`, `pelnomocnictwo`, `przelew` (потвердження переказу).
Чужий документ (напр. оголошення TED) → **жодного файлу**.

## Вимоги UZP (не порушувати)
- Python 3.13+, `requirements.txt`, запуск з CLI (`start.bat`).
- `input/` і `output/` у корені; дерево папок те саме, JSON має **те саме ім'я**, що й PDF.
- Лише open source. LLM — тільки модель з відкритими вагами через API, де **і компанія, і сервер в ЄС** (ADR-0004). Ключ API здаємо разом із рішенням.
- Тестовий ПК — офісний, без GPU. Більшість документів — цифрові PDF, але бувають скани → потрібен OCR.
- Значення немає в документі → `null`. Нічого не вигадувати.
- Оцінка: F1 на прихованих справах (≥10). Фінал (топ-3): 50% F1 + 50% — нові типи документів **через конфіг, без зміни коду**.
- Повні умови: `docs/UZP/` (лише локально, не в git).

## Як працюємо
1. **Готове рішення першим** (open source, бажано MIT/BSD/Apache). Якщо з великої бібліотеки треба мала частина — пишемо своє.
2. **Не перевіряємо руками** те, що перевіряє інструмент: тести — `pytest`, якість — `tools/ocena_f1.py`.
3. **Кожне рішення → ADR** у `docs/adr/` (контекст, рішення, наслідки — коротко).
4. **TDD:** опис тесту з прикладом у `docs/testy.md` → червоний тест → код → тест зелений. Тестів мінімум, кожен = пункт у `docs/testy.md`. Тестів заради тестів не пишемо.
5. **Економія токенів:** читай лише потрібні файли й частини; без субагентів; відповідай коротко.
6. **Кінець сесії:** онови `docs/STAN.md` (зроблено / далі / питання).
7. **Код без коментарів.** Якщо коментар конче потрібен — польською. Повідомлення CLI — польською. Документація (`AGENTS.md`, `docs/`) — українською.

## Карта
| Шлях | Що |
|---|---|
| `odwolania2json/` | код; CLI: `python -m odwolania2json` |
| `config/typy/*.yaml` | тип документа: `znaczniki` (класифікація), `szablon` (форма JSON). Новий тип = новий YAML |
| `tests/` | тести з `docs/testy.md` |
| `tools/ocena_f1.py` | F1 на 60 тренувальних справах (ADR-0003) |
| `data/uzp/` | клон https://github.com/Urzad-Zamowien-Publicznych/hacknation-2026 (не в git) |
| `docs/adr/`, `docs/testy.md`, `docs/STAN.md` | рішення, тести, стан |

## Команди (Windows)
```
py -3.13 -m venv .venv && .venv\Scripts\pip install -r requirements-dev.txt
git clone https://github.com/Urzad-Zamowien-Publicznych/hacknation-2026 data/uzp
start.bat                                  # input\ → output\
.venv\Scripts\python -m pytest -q          # тести
.venv\Scripts\python tools\ocena_f1.py     # F1 і найгірші поля
```

## Ролі
- **Claude:** архітектура, конвеєр, складні поля, ADR.
- **Gemini (Argon):** задачі з позначкою `[Argon]` у `docs/STAN.md`. Змінює лише файли, названі в задачі. ADR і тести — тільки після слова користувача.
