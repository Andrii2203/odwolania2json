# Тести

TDD: спершу опис тут (з прикладом) → червоний тест → код → тест зелений.
Кожен тест = один приклад. Тест без пункту тут не пишемо.

## T1. Наскрізний (walking skeleton): кожна справа з 3 документів → 3 JSON

```
input/przyklad_01/odwolanie.pdf              → output/przyklad_01/odwolanie.json              має ключ "OdwolanieKIO"
input/przyklad_01/pelnomocnictwo.pdf         → output/przyklad_01/pelnomocnictwo.json         має ключ "mocodawca"
input/przyklad_01/potwierdzenie_przelewu.pdf → output/przyklad_01/potwierdzenie_przelewu.json має ключ "przelew_bankowy"
… і так для всіх 60 справ (180 документів)
```
- Дані: `data/uzp/dane/*`. Запуск — справжній CLI, як у журі.
- Доводить: CLI, дерево папок, імена файлів, **класифікація кожного документа**, форма JSON.
- Складний приклад: pełnomocnictwo без слова «mocodawca», але з «udzielam pełnomocnictwa» — теж має бути `pelnomocnictwo`.
- Тест: `tests/test_e2e.py::test_t1_sprawa_trzy_dokumenty`

## T2. Чужий документ → жодного файлу

```
input/case1/negatywny przyklad.pdf  (оголошення TED)  →  у output/ немає жодного JSON
```
- Дані: `data/uzp/szablon-aplikacja/input/case1/negatywny przyklad.pdf` (так у шаблоні UZP: для нього немає вихідного JSON).
- Тест: `tests/test_e2e.py::test_t2_obcy_dokument`

## Вимірювання якості (не тест)
`tools/ocena_f1.py` проганяє всі 60 тренувальних справ через CLI і рахує F1 за ADR-0003:
```
Документів: 180 | тип визначено правильно: 180/180
F1 = 0.412  (TP 900 | FP 120 | FN 2450)
Найгірші поля:
  odwolanie  Odwolujacy[].nip   FN 58  FP 0
```
Це компас: кожна зміна екстракції має піднімати F1.
