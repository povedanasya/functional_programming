"""Демо ЛР5: нескінченні потоки, вікна та генератор шаблонів (варіант 14)."""

from __future__ import annotations

from itertools import islice

from patterns import first_n, laps, numbered, pattern_windows, states, until
from streams import (
    drop,
    fib_stream,
    moving_average,
    naturals,
    prefix_sums,
    take,
    window_sums,
)

PATTERN = ("A", "B", "C")
LIGHTS = {"red": "green", "green": "yellow", "yellow": "red"}


def main() -> None:
    """Друкує приклади роботи потоків (єдиний I/O у лабораторній)."""
    print("fib first 10:", take(10, fib_stream()))
    print("fib drop 5 take 8:", take(8, drop(5, fib_stream())))
    print(
        "window sums of naturals (k=3, first 10):", take(10, window_sums(naturals(), 3))
    )
    print("moving average [1..6], k=2:", list(moving_average([1, 2, 3, 4, 5, 6], 2)))
    print("prefix sums [1,2,3,4]:", list(prefix_sums([1, 2, 3, 4])))

    print("first 7 of ABC:", [f"{x.seq}:{x.item}" for x in first_n(PATTERN, 7)])
    print("2 laps of ABC :", [(x.seq, x.item, x.lap) for x in laps(PATTERN, 2)])
    stopped = until(lambda x: x.seq > 4 and x.item == "A", numbered(PATTERN))
    print("until A after 4:", [x.item for x in stopped])
    print("windows k=2  :", take(4, pattern_windows(PATTERN, 2)))
    print("lights       :", take(7, states(LIGHTS, "red")))
    print("drop 100, 3  :", [x.seq for x in islice(drop(100, numbered(PATTERN)), 3)])


if __name__ == "__main__":
    main()
