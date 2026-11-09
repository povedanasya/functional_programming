# Лабораторна робота №7. functools та operator

**Варіант 14 — логістичні відправлення.** Запис: `id`, `weight`, `distance`, `priority`, `cost`.
Конвеєр: нормалізація → фільтр за мінімальним пріоритетом → скоригована вартість
(`(cost + weight·per_kg + distance·per_km) × (1 + priority_rate·(priority − 1))`) →
сортування (`priority` ↓, `adjusted` ↓, `id` ↑) → Top-N; загальна вартість через `reduce`.
Виконала: Поведа Анастасія, ФЕП-23.

## Цілі

- `functools.partial` для часткового застосування та побудови конвеєрів;
- `functools.reduce` як універсальний `pipeline(value, *funcs)` і для агрегації вартості;
- `operator.itemgetter` / `attrgetter` / `methodcaller` замість lambda-гетерів;
- поліморфний API завантаження даних через `functools.singledispatch`;
- повний порядок доменного класу через `functools.total_ordering`.

## Що зроблено

| Файл | Призначення |
|---|---|
| `core.py` | `pipeline` через `reduce`; `mapf`/`filt` як `partial(map/filter)`; трансформації відправлень `normalize_shipment` (`itemgetter`, `methodcaller`), `has_priority` і `adjusted_cost` (налаштовуються через `partial`), `with_adjusted`, `to_rank`; `rank_shipments` збирає конвеєр, сортує `attrgetter`-ключами за кількома критеріями та бере Top-N; `total_cost` — `reduce(add, …)`. Базовий приклад з методички: `clean_and_rank` для студентів. |
| `models.py` | `ShipmentRank` — frozen dataclass з `@total_ordering`: `__eq__`/`__lt__` за `(priority, adjusted, id)`, `NotImplemented` для чужих типів. |
| `loaders.py` | `@singledispatch load_shipments` для JSON-рядка, шляху `str`, `pathlib.Path` (.json/.csv), відкритого текстового файлу та готового списку словників; `load_students` — той самий loader для базового прикладу. |
| `main.py` | Демо: завантаження з трьох джерел, рейтинг за пріоритетом з аргументів, загальна вартість. |
| `sample_data.json`, `sample_data.csv` | Приклади даних. |
| `tests/test_lab07.py` | pytest: pipeline, partial, operator, конвеєр і Top-N, відсутність мутацій, усі джерела `singledispatch`, помилкові входи, усі оператори порівняння `ShipmentRank`, базовий приклад. |
| `tests/test_properties.py` | Hypothesis: Top-N є префіксом відсортованого результату, відсутність мутацій і збіг `total_cost` із сумою, фільтр за `min_priority`. |

## Як запускати

```bash
pip install -r requirements.txt
python main.py                 # пріоритет ≥ 2, Top-3
python main.py 3 5             # min_priority top

pytest
mypy --strict .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab07/`.
