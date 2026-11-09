# Лабораторна робота №1. Основи функціонального програмування у Python

**Варіант 14 — вартість навчальних курсів.** Вхідні дані: реєстрація на курс (назва курсу, ціна, статус слухача, кількість куплених курсів, підтвердження). Для підтверджених реєстрацій обчислюється кінцева вартість: `price × (1 − знижка) × (1 + податок)`, де знижка складається зі студентської (за статусом) і пакетної (за кількістю курсів) та обмежена максимумом.
Виконала: Поведа Анастасія, ФЕП-23.

## Цілі

- зрозуміти, що таке чиста функція і референтна прозорість;
- виявити та ізолювати побічні ефекти (print, глобальні таблиці знижок, мутація вхідних словників);
- переписати імперативний фрагмент `starter_imperative.py` у функціональному стилі;
- скомпонувати правила знижок і параметризувати обчислення через `typing.Callable`.

## Що зроблено

| Файл | Призначення |
|---|---|
| `core.py` | Чисте ядро варіанта 14: `final_cost`, `with_cost`, `make_enrollment_processor` (фабрика обробника), `process_enrollments_pure`, правила `min_price_filter` / `status_discount` / `bundle_discount` / `combine_discounts` / `tax`; додаткові вправи `compose`, `pipe`, `make_multiplier`, `stamp_total` (інжекція годинника); базове завдання з методички: `order_subtotal`, `with_total`, `make_processor(accept, apply_discount, apply_tax)`, `process_orders_pure`. Жодного I/O, глобалів і мутацій. |
| `app.py` | Оболонка побічних ефектів: читання реєстрацій із JSON, `render_report`, `run` (базове завдання), `print`, `time.time`. |
| `starter_imperative.py` | Початковий імперативний код (`process_orders` з методички та `process_enrollments` за варіантом) — лишений для тестів еквівалентності. |
| `tests/test_core.py` | pytest для варіанта 14: референтна прозорість, відсутність мутацій, збіг з імперативною версією, Callable-правила, композиція знижок з обмеженням, `compose`, `make_multiplier`, `stamp_total`, `render_report`. |
| `tests/test_orders.py` | pytest для базового завдання (замовлення): мінімальні тести з методички. |
| `tests/test_properties.py` | property-based тести (Hypothesis): референтна прозорість, відсутність мутацій, інваріанти підсумку. |
| `conftest.py` | Фікстури `sample_enrollments`, `sample_orders`. |

Правила передаються як `Callable[[float], bool]` (фільтр за ціною), `Callable[[Enrollment], float]`
(правило знижки) та `Callable[[float], float]` (податок). `combine_discounts(*rules, cap=...)` компонує
кілька правил знижок в одне; `make_enrollment_processor(accept=..., discount=..., apply_tax=...)` повертає
налаштований обробник `Callable[[Iterable[Enrollment]], Report]`. `process_enrollments_pure` — окремий
випадок, зібраний із цих правил.

## Як запускати

```bash
pip install -r requirements.txt
python app.py                   # вбудований приклад
python app.py enrollments.json  # реєстрації з файлу (список об'єктів {id, course, price, status, courses, confirmed})

pytest
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab01/`.
