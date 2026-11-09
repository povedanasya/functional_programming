# Лабораторна робота №3. Нездатні до змін структури даних (immutability)

**Варіант 14 — IoT-сенсори.** Сутності `Sensor` і `Reading` (показ як `NamedTuple`), мітки як `frozenset`,
конфігурація сенсора як `MappingProxyType`. Pure-оновлення: додавання показу (з автоматичною міткою `alert`,
якщо значення поза межами конфігурації), додавання мітки, зміна конфігурації; розрахунок статистики
(`stats`) кешується через `lru_cache`; опційно — `freeze` для глибокого заморожування.
Виконала: Поведа Анастасія, ФЕП-23.

## Цілі

- застосувати `tuple`/`NamedTuple`, `frozenset`, `@dataclass(frozen=True, slots=True)`, `MappingProxyType`;
- замінити мутації на повернення нових копій (`dataclasses.replace`, конкатенація tuple, `|` для frozenset);
- перевірити немутацію, read-only поведінку та хешованість тестами;
- виміряти ефект переходу на незмінну модель (`pytest --durations=5`).

## Що зроблено

| Файл | Призначення |
|---|---|
| `model.py` | `Reading` (NamedTuple), `Sensor` (frozen, slots), `Kind = Literal[...]`, `make_config` (proxy над копією), `make_sensor`. Методи `add_reading` / `add_label` / `disable` повертають нові об'єкти через `replace`. |
| `core.py` | Чисті функції: `stats` (`@lru_cache`, повертає `Stats` NamedTuple), `is_out_of_range`, pure-оновлення `add_reading`, `add_label`, `with_config`, `recalculate`, `index_by_sensor` (сенсор як ключ словника), `freeze` (глибоке заморожування). |
| `mutable_model.py` | Мутабельна версія «до» (dict + list + set) — лише для порівняння часу. |
| `main.py` | Демонстрація: ланцюжок оновлень, незмінність оригіналу, кеш, read-only config. |
| `tests/test_immutability.py` | Немутація, мітка `alert`, `FrozenInstanceError`, показ як tuple, `TypeError` для proxy, копіювання джерела config, хешованість і словник з ключем-сенсором, кеш `cache_info`, `freeze`, 2 property-тести (Hypothesis). |
| `tests/test_performance.py` | Два тести однакового навантаження на mutable- і immutable-моделі для `--durations=5`. |
| `conftest.py` | Фікстура `sensor`. |

### Хешованість

`Sensor` хешований завдяки `frozen=True`, але поле `config` (`mappingproxy`) не має `__hash__`,
тому воно виключене з хешу через `field(hash=False)` і бере участь лише у `__eq__`. Усі інші
поля (`tuple` з `NamedTuple`, `frozenset`, примітиви) хешуються.

## Порівняння часу (`python -m pytest -q --durations=5`)

| Тест | Модель | Час |
|---|---|---|
| `test_mutable_before` | dict + list + set, статистика щоразу перераховується | ~0.18 s |
| `test_immutable_after` | frozen dataclass + tuple + `lru_cache` | ~0.01 s |

Незмінна модель на 2000 додаваннях показів створює 2000 нових tuple (O(n²) копіювання), але
кешований розрахунок статистики повністю компенсує це: 1999 звернень із 2000 — cache hit.

## Висновок про незмінність

Переваги: референтна прозорість і прості тести без `deepcopy`, безпечне спільне читання,
хешованість (сенсор як ключ `dict`, вхід `lru_cache`). Накладні витрати: кожне оновлення
створює новий об'єкт і копіює tuple/frozenset, `MappingProxyType` захищає лише верхній рівень
(для вкладених структур потрібен `freeze`). Для сутностей розміру «сенсор» ці витрати
несуттєві, а виграш у передбачуваності — великий.

## Як запускати

```bash
pip install -r requirements.txt
python main.py

pytest -q --durations=5
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab03/`.
