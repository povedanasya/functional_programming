# Лабораторна робота №8. Алгебраїчні типи даних «по-Python'івськи»

**Варіант 14 — події системи.** ADT `Event = Login | Logout | FileOpened | ErrorEvent | EventGroup`,
рівні помилок через `Literal["warning", "error", "critical"]`, структурний контракт `Timestamped`
через `Protocol`, журнал обробляється чистою функцією-reducer `step`/`reduce_log`, статистика,
`count_errors`, `worst_level` і `describe` — через `match/case`.
Виконала: Поведа Анастасія, ФЕП-23.

## Модель

| Вузол | Поля |
|---|---|
| `Login` | `user`, `timestamp` |
| `Logout` | `user`, `timestamp` |
| `FileOpened` | `user`, `path`, `timestamp`, `mode: Literal["read","write"]` |
| `ErrorEvent` | `message`, `level: Level`, `timestamp` |
| `EventGroup` | `items: tuple[Event, ...]`, `label` — рекурсивний вузол, група може містити групи |

Усі вузли — `@dataclass(frozen=True)`: хешовані, незмінні; функції повертають нові значення.

## Що зроблено

| Файл | Призначення |
|---|---|
| `model.py` | ADT, `TypeAlias` `Event`, `Literal` `Level`/`Mode`, `Protocol` `Timestamped`. |
| `evaluator.py` | `Stats` (TypedDict) і незмінний початковий стан `EMPTY`; reducer `step(state, event)` повертає новий стан (група згортається рекурсивно через `reduce`), `reduce_log`, `level_rank`, `kind`, `flatten`, `timestamp_of`, `error_level`, `count_errors(min_level=…)`, `worst_level`. Від'ємна часова мітка → `ValueError`. |
| `pretty.py` | `describe` — рекурсивний текстовий опис із відступами; `Protocol` `Renders`. |
| `expr.py`, `eval_.py` | Базове завдання з методички: `Expr = Num \| Add \| Mul`, `eval_expr` з `EvalOverflow`, `render`, альтернативний `Bin` з `Literal["+", "*"]`. |
| `main.py` | Демонстраційний запуск. |
| `tests/test_events.py` | pytest: кожен вид події в `step`, повна статистика журналу, рекурсивна група, `flatten`/`kind`/`timestamp_of`, рівні та підрахунок помилок, помилкові входи, незмінність і хешованість, рендер вкладеної групи, `Protocol`. |
| `tests/test_expr.py` | Тести базового завдання, зокрема переповнення. |
| `tests/test_properties.py` | Hypothesis: група згортається так само, як її листки; лічильники узгоджені з кількістю подій; `step` не мутує стан; рендер виразу обчислюється до того ж значення. |
| `mypy.ini` | Строгий режим mypy. |

## Як запускати

```bash
pip install -r requirements.txt
python main.py

pytest
mypy --strict .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab08/`.
