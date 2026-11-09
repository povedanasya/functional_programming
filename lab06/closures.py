"""Замикання ЛР6: лічильник зі станом, логер з префіксом, політики затримок повторів.

Варіант 14: політика затримки — це функція attempt -> seconds, яку створює фабрика
(замикання над параметрами backoff) і яку планувальник отримує як Callable.
"""

from __future__ import annotations

from collections.abc import Callable

DelayPolicy = Callable[[int], float]
"""Номер невдалої спроби (1, 2, ...) -> пауза перед наступною спробою, с."""


def make_counter(start: int = 0) -> Callable[[], int]:
    """Лічильник викликів: стан value живе в замиканні та змінюється через nonlocal."""
    value = start

    def inc() -> int:
        nonlocal value
        value += 1
        return value

    return inc


def make_logger(prefix: str, sink: Callable[[str], None]) -> Callable[[str], None]:
    """Логер з інжектованим приймачем sink (без print у ядрі)."""
    return lambda msg: sink(f"[{prefix}] {msg}")


def fixed_delay(seconds: float) -> DelayPolicy:
    """Фіксований backoff: однакова пауза після кожної невдалої спроби."""
    if seconds < 0:
        raise ValueError("delay must be >= 0")
    return lambda attempt: seconds


def exponential_delay(
    base: float, factor: float = 2.0, max_delay: float = float("inf")
) -> DelayPolicy:
    """Експоненційний backoff: base * factor**(attempt-1), але не більше max_delay."""
    if base < 0 or factor <= 0 or max_delay < 0:
        raise ValueError("base, max_delay must be >= 0 and factor > 0")
    return lambda attempt: min(base * factor ** (attempt - 1), max_delay)


def make_fake_sleep(
    logger: Callable[[str], None] = lambda _: None,
) -> tuple[Callable[[float], None], Callable[[], tuple[float, ...]]]:
    """Підміна time.sleep для тестів: пара (sleep, slept) над спільним станом.

    sleep нічого не чекає, лише записує тривалість; slept повертає знімок історії.
    """
    history: list[float] = []

    def sleep(seconds: float) -> None:
        history.append(seconds)
        logger(f"(sleep {seconds:.3f}s skipped)")

    def slept() -> tuple[float, ...]:
        return tuple(history)

    return sleep, slept
