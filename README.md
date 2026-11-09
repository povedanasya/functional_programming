# Функціональне програмування на Python — лабораторні роботи

Поведа Анастасія, ФЕП-23, варіант 14.

| Лабораторна | Тема | Варіант 14 |
|---|---|---|
| [lab01](lab01/) | Основи ФП: чисті функції, референтна прозорість, `typing.Callable` | Вартість навчальних курсів |
| [lab02](lab02/) | Функції вищого порядку, lambda, композиція: конвеєр map/filter/reduce | Музичний каталог |
| [lab03](lab03/) | Незмінні структури даних: tuple, frozenset, frozen dataclass, MappingProxyType | IoT-сенсори |
| [lab04](lab04/) | Рекурсія та мемоізація: quicksort, обходи дерев, lru_cache | Обходи n-арного дерева |
| [lab05](lab05/) | Ліниві обчислення: генератори та itertools | Нескінченний генератор шаблонів |
| [lab06](lab06/) | Замикання та декоратори як HOF | Планувальник повторів задач |
| [lab07](lab07/) | functools та operator: partial, reduce, singledispatch, total_ordering | Логістичні відправлення |
| [lab08](lab08/) | Алгебраїчні типи даних: Union, Literal, Protocol, match/case | Події системи |

Кожна `labN/` — самостійний проєкт: `README.md`, код, `tests/` (pytest + Hypothesis),
`requirements.txt` і звіт `report.pdf`. Стиль: `black`, `ruff`; типи: `mypy --strict`
(конфіг у `pyproject.toml`).

## Як запускати

Команди виконуються з каталогу конкретної лабораторної (модулі різних лаб мають
однакові імена, тому запуск pytest/mypy з кореня репозиторію не підтримується):

```bash
cd lab03
pip install -r requirements.txt
pytest -q
mypy --strict .
ruff check .
black --check .
```

Усі лаби одразу: `python check_all.py` з кореня репозиторію.
