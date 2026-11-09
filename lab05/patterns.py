"""Варіант 14 — нескінченний генератор шаблонів: циклічне повторення набору
символів або станів із порядковими номерами та зупинкою за умовою.

Усі функції повертають ітератори; нескінченний потік обмежується лише на виході
через islice / takewhile / take. Шаблон не змінюється (копіюється у tuple).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from itertools import count, cycle, islice, takewhile
from typing import Generic, NamedTuple, TypeVar

from streams import sliding_window

T = TypeVar("T")


class Numbered(NamedTuple, Generic[T]):
    """Елемент шаблону з порядковим номером і номером циклу повторення."""

    seq: int
    item: T
    lap: int


def repeat_pattern(pattern: Iterable[T]) -> Iterator[T]:
    """Нескінченно повторює шаблон (власний генератор з yield from).

    Порожній шаблон — ValueError, інакше цикл ніколи б не віддав значення.
    """
    items = tuple(pattern)
    if not items:
        raise ValueError("pattern must not be empty")
    while True:
        yield from items


def numbered(pattern: Iterable[T], start: int = 1) -> Iterator[Numbered[T]]:
    """Нескінченний потік (номер, символ, цикл): zip(count(start), cycle(pattern))."""
    items = tuple(pattern)
    if not items:
        raise ValueError("pattern must not be empty")
    return (
        Numbered(seq, item, (seq - start) // len(items))
        for seq, item in zip(count(start), cycle(items), strict=False)
    )


def until(
    stop: Callable[[Numbered[T]], bool], it: Iterable[Numbered[T]]
) -> Iterator[Numbered[T]]:
    """Елементи, поки умова зупинки хибна (takewhile з інвертованим предикатом)."""
    return takewhile(lambda x: not stop(x), it)


def first_n(pattern: Iterable[T], n: int, start: int = 1) -> list[Numbered[T]]:
    """Перші n пронумерованих елементів (єдина матеріалізація — на виході)."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return list(islice(numbered(pattern, start), n))


def laps(pattern: Iterable[T], max_laps: int) -> Iterator[Numbered[T]]:
    """Рівно max_laps повних повторень шаблону (зупинка за номером циклу)."""
    if max_laps < 0:
        raise ValueError("max_laps must be >= 0")
    return until(lambda x: x.lap >= max_laps, numbered(pattern))


def states(transitions: Mapping[T, T], start: T) -> Iterator[T]:
    """Нескінченний потік станів автомата: start, transitions[start], ...

    Власний генератор з yield; наступний стан обчислюється лише за запитом.
    """
    state = start
    while True:
        yield state
        state = transitions[state]


def pattern_windows(pattern: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Ковзні вікна розміру k над нескінченним повторенням шаблону."""
    return sliding_window(repeat_pattern(pattern), k)
