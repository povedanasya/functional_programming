# Лабораторна робота №2. Функції вищого порядку, lambda, композиція

**Варіант 14 — музичний каталог.** Запис: `id`, `title`, `genre`, `listens` (прослуховування за періодами).
Конвеєр: сумарні прослуховування = сума за періодами → підсилення вибраного жанру → фільтр непопулярних
треків за порогом → сортування (прослуховування спадно, `id` зростом) → Top-N (рейтинг).
Reduce-агрегація: `count`, `listens_sum`, `avg_listens`.
Виконала: Поведа Анастасія, ФЕП-23.

## Цілі

- map / filter / reduce та їх генераторні еквіваленти;
- функції вищого порядку і `lambda`;
- композиція функцій (`compose`, `pipe`, `juxt`) і збирання конвеєра без проміжних змінних;
- жодних мутацій вхідних записів — кожен крок повертає нові словники.

## Що зроблено

| Файл | Призначення |
|---|---|
| `core.py` | Чисте ядро. Композиція: `compose`, `pipe`, `juxt`. Варіант 14: `Track` (TypedDict), трансформації `with_total_listens` (map), `boost_genre` (map), `min_listens` (filter), `normalize_titles` (map), `sort_by_listens_desc` (два ключі), `take` (islice), агрегація `reduce_listen_stats`, збирання `build_chart_pipeline`. Базовий приклад з методички (клієнти: `only_adults`, `with_total`, `boost_city`, `normalize_names`, `sort_by_total_desc`, `take_records`, `reduce_stats`, `build_pipeline`). |
| `app.py` | Оболонка I/O та CLI (argparse): читання JSON, рендер і друк результату. |
| `sample_data.json` | Приклад вхідних даних. |
| `tests/test_core.py` | pytest: Top-N і тай-брейкер, відсутність мутацій, фільтр за порогом, reduce-агрегація, еквівалентність композиції ручному ланцюжку, `pipe`/`juxt`, базовий конвеєр. |
| `tests/test_properties.py` | Hypothesis: Top-N є префіксом повного відсортованого списку, відсутність мутацій, узгодженість статистик. |
| `conftest.py` | Фікстури `tracks`, `records`. |

Кожна трансформація — фабрика, що повертає функцію `Iterable[Track] -> Iterable[Track]`,
тому конвеєр збирається через `compose(...)` з однотипних кроків. `lambda` використано у
фільтрі, map-кроках і ключі сортування.

## Як запускати

```bash
pip install -r requirements.txt
python app.py --top 3 --boost-genre rock --factor 1.5 --min-listens 300
python app.py --data sample_data.json --top 2

pytest
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab02/`.
