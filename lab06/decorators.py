"""Параметризовані декоратори ЛР6: timed, retries (з політикою затримок), cached (TTL).

Усі зовнішні залежності (годинник, sleep, логер, джерело часу, політика затримки)
інжектуються як Callable, тому тести детерміновані й без реальних затримок.
"""

from __future__ import annotations

import functools
import threading
import time
from collections.abc import Callable
from typing import Any, Literal, ParamSpec, Protocol, TypeVar, cast

from closures import DelayPolicy, fixed_delay

P = ParamSpec("P")
R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)

Key = tuple[tuple[Any, ...], tuple[tuple[str, Any], ...]]
NO_DELAY: DelayPolicy = fixed_delay(0.0)


class Decorator(Protocol):
    """Декоратор, що зберігає сигнатуру: Callable[P, R] -> Callable[P, R]."""

    def __call__(self, func: Callable[P, R], /) -> Callable[P, R]: ...


class CachedFn(Protocol[P, R_co]):
    """Обгортка з кешем: звичайний виклик плюс методи керування кешем."""

    __name__: str
    __doc__: str | None

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...

    def cache_clear(self) -> None: ...

    def cache_invalidate(
        self, predicate: Callable[[tuple[Any, ...], dict[str, Any]], bool]
    ) -> int: ...

    def cache_size(self) -> int: ...


class CacheDecorator(Protocol):
    """Декоратор, що повертає обгортку з методами кешу."""

    def __call__(self, func: Callable[P, R], /) -> CachedFn[P, R]: ...


def timed(
    label: str | None = None,
    *,
    unit: Literal["s", "ms", "us"] = "ms",
    logger: Callable[[str], None],
    clock: Callable[[], float] = time.perf_counter,
) -> Decorator:
    """Логує час виконання (навіть при винятку); годинник і логер інжектовані."""
    factor = {"s": 1.0, "ms": 1e3, "us": 1e6}[unit]

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        name = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            t0 = clock()
            try:
                return func(*args, **kwargs)
            finally:
                logger(f"[timed] {name} took {(clock() - t0) * factor:.3f} {unit}")

        return wrapper

    return decorator


def retries(
    attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    *,
    delay: DelayPolicy = NO_DELAY,
    sleep: Callable[[float], None] = time.sleep,
    logger: Callable[[str], None] = lambda _: None,
) -> Decorator:
    """Варіант 14: повторює задачу при зазначених винятках, а паузу між спробами
    визначає інжектована політика delay(attempt) — фіксована чи експоненційна.

    sleep також інжектується, тому в тестах його замінює fake_sleep без очікування.
    """
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for i in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == attempts:
                        logger(f"[retries] {func.__name__}: fail after {i}: {e!r}")
                        raise
                    wait = delay(i)
                    logger(f"[retries] {func.__name__}: attempt {i} failed: {e!r}")
                    sleep(wait)
            raise AssertionError("unreachable")  # pragma: no cover

        return wrapper

    return decorator


def make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Key:
    """Ключ кешу для хешованих аргументів: (args, відсортовані kwargs)."""
    return (args, tuple(sorted(kwargs.items())))


def cached(
    *,
    ttl: float | None = None,
    time_fn: Callable[[], float] = time.time,
) -> CacheDecorator:
    """Кеш з TTL; на обгортці є cache_clear, cache_invalidate, cache_size."""

    def decorator(func: Callable[P, R]) -> CachedFn[P, R]:
        cache: dict[Key, tuple[float | None, R]] = {}
        lock = threading.Lock()  # ponytail: один лок на функцію, достатньо для ЛР

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = make_key(args, kwargs)
            now = time_fn()
            with lock:
                if key in cache:
                    expiry, value = cache[key]
                    if expiry is None or now < expiry:
                        return value
                    del cache[key]
            value = func(*args, **kwargs)
            with lock:
                cache[key] = (None if ttl is None else now + ttl, value)
            return value

        def cache_clear() -> None:
            with lock:
                cache.clear()

        def cache_invalidate(
            predicate: Callable[[tuple[Any, ...], dict[str, Any]], bool],
        ) -> int:
            with lock:
                doomed = [k for k in cache if predicate(k[0], dict(k[1]))]
                for k in doomed:
                    del cache[k]
            return len(doomed)

        def cache_size() -> int:
            with lock:
                return len(cache)

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        wrapper.cache_invalidate = cache_invalidate  # type: ignore[attr-defined]
        wrapper.cache_size = cache_size  # type: ignore[attr-defined]
        return cast(CachedFn[P, R], wrapper)

    return decorator
