"""Базові ліниві потоки ЛР5: генератори, take/drop, sliding_window, itertools.

Усі функції повертають ітератори й нічого не матеріалізують, окрім take (список
із перших n елементів за умовою завдання). Нескінченні потоки обмежуються
take / islice / takewhile на боці викликача.
"""

from __future__ import annotations

import operator
from collections import deque
from collections.abc import Callable, Iterable, Iterator
from itertools import accumulate, count, dropwhile, islice, starmap, takewhile
from typing import TypeVar

T = TypeVar("T")


def fib_stream() -> Iterator[int]:
    """Нескінченний потік чисел Фібоначчі: 0, 1, 1, 2, 3, ..."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def naturals(start: int = 1) -> Iterator[int]:
    """Нескінченний лічильник натуральних чисел від start (делегує itertools.count)."""
    yield from count(start)


def take(n: int, it: Iterable[T]) -> list[T]:
    """Перші n елементів як список; n < 0 — ValueError, n == 0 — порожній список."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return list(islice(it, n))


def drop(n: int, it: Iterable[T]) -> Iterator[T]:
    """Ітератор без перших n елементів (ліниво «промотує» n значень)."""
    if n < 0:
        raise ValueError("n must be >= 0")
    iterator = iter(it)
    next(islice(iterator, n, n), None)
    return iterator


def sliding_window(it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Ковзні вікна розміру k як кортежі; якщо елементів менше k — жодного вікна."""
    if k <= 0:
        raise ValueError("window size must be > 0")
    iterator = iter(it)
    window: deque[T] = deque(islice(iterator, k), maxlen=k)
    if len(window) < k:
        return
    yield tuple(window)
    for x in iterator:
        window.append(x)
        yield tuple(window)


def moving_average(it: Iterable[float], k: int) -> Iterator[float]:
    """Рухоме середнє по вікнах розміру k (ліниво, через sliding_window)."""
    return (sum(w) / k for w in sliding_window(it, k))


def window_sums(it: Iterable[float], k: int) -> Iterator[float]:
    """Ковзні суми по вікнах розміру k через starmap(sum, ...)."""
    return starmap(lambda *w: sum(w), sliding_window(it, k))


def prefix_sums(it: Iterable[float]) -> Iterator[float]:
    """Префіксні суми (itertools.accumulate)."""
    return accumulate(it)


def prefix_products(it: Iterable[float]) -> Iterator[float]:
    """Префіксні добутки (accumulate з operator.mul)."""
    return accumulate(it, operator.mul)


def take_while(pred: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    """Елементи, поки предикат істинний (itertools.takewhile)."""
    return takewhile(pred, it)


def drop_while(pred: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    """Елементи після першого, для якого предикат хибний (itertools.dropwhile)."""
    return dropwhile(pred, it)
