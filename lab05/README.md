# Лабораторна робота №5. Ліниві обчислення: генератори та itertools

**Варіант 14 — нескінченний генератор шаблонів.** Набір символів або станів циклічно
повторюється нескінченно, кожен елемент отримує порядковий номер і номер циклу
(`zip(count, cycle)`), а потік зупиняється за умовою (`takewhile`), за кількістю
елементів (`islice`) або за кількістю повних повторень.
Виконала: Поведа Анастасія, ФЕП-23.

## Цілі

- generator expressions, `yield` / `yield from`, ітератори та лінивість;
- робота з нескінченними послідовностями (`fib_stream`, `naturals`, `repeat_pattern`, `states`);
- `itertools`: `cycle`, `count`, `islice`, `takewhile`, `dropwhile`, `accumulate`, `starmap`;
- універсальні `take` / `drop` / `sliding_window` та вікна над циклічним шаблоном.

## Що зроблено

| Файл | Призначення |
|---|---|
| `streams.py` | Базове з методички: `fib_stream`, `naturals`, `take`, `drop`, `sliding_window` (на `deque(maxlen=k)`), `moving_average`, `window_sums` (`starmap`), обгортки `prefix_sums` / `prefix_products` (`accumulate`), `take_while` / `drop_while`. |
| `patterns.py` | Варіант 14: `Numbered` (NamedTuple: `seq`, `item`, `lap`), власний генератор `repeat_pattern` (`yield from` у нескінченному циклі), `numbered` (`zip(count(start), cycle(pattern))`), `until` (зупинка за умовою через `takewhile`), `first_n` (`islice`), `laps` (рівно N повних повторень), `states` (генератор станів автомата за таблицею переходів), `pattern_windows` (`sliding_window` над циклічним шаблоном). |
| `main.py` | Демо: Фібоначчі, вікна натуральних, рухоме середнє, пронумерований шаблон `ABC`, зупинка за умовою, два повні цикли, вікна, світлофор зі станів, `drop` на нескінченному потоці. |
| `tests/test_fib_stream.py` | Перші 10 значень, `drop` + `take`, свіжий генератор на кожен виклик. |
| `tests/test_take_drop.py` | Просування спільного ітератора, `count`, `n = 0`, порожнє джерело, `n < 0`. |
| `tests/test_sliding_window.py` | Базові й граничні вікна (`k > len`, порожнє джерело, `k <= 0`), суми та рухоме середнє. |
| `tests/test_accumulate.py` | `accumulate` із сумою / добутком / `max`, `takewhile` / `dropwhile` на `count`. |
| `tests/test_patterns.py` | Повторення, нумерація і цикли, зупинка за умовою, `laps`, автомат станів, вікна над шаблоном, крайні випадки (порожній шаблон, `n = 0`, `n < 0`, `k = 0`), незалежність від мутації вхідного списку, 3 property-тести Hypothesis. |
| `tests/test_laziness.py` | Ітератор-лічильник і таблиця переходів з лічильником: обчислюється рівно стільки елементів, скільки запитано; потік із 10⁶ пропущених елементів не матеріалізується. |

## Лінивість і нескінченні потоки

Жодна функція ядра не викликає `list()` на нескінченному вході: `repeat_pattern` і `states`
віддають значення лише за запитом, `numbered` — генераторний вираз над `zip(count, cycle)`,
`until` — `takewhile`, `pattern_windows` тримає лише `k` останніх елементів у `deque`.
Єдина матеріалізація — `take` і `first_n` на виході. Шаблон копіюється у `tuple` при
створенні потоку, тому подальша мутація вхідного списку на потік не впливає. `drop(n, it)`
промотує `n` елементів одразу при виклику (як у методичці), але не зберігає їх.

## Як запускати

```bash
pip install -r requirements.txt
python main.py

pytest
mypy .
ruff check .
black --check .
```

Усі команди виконуються з каталогу `lab05/`.
