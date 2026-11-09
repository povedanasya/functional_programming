"""Чисті операції над ADT подій через match/case і reducer (варіант 14)."""

from __future__ import annotations

from collections.abc import Iterable
from functools import reduce
from typing import TypedDict

from model import ErrorEvent, Event, EventGroup, FileOpened, Level, Login, Logout


class Stats(TypedDict):
    logins: int
    logouts: int
    files_opened: int
    errors: dict[Level, int]
    active_users: frozenset[str]
    last_timestamp: int


EMPTY: Stats = {
    "logins": 0,
    "logouts": 0,
    "files_opened": 0,
    "errors": {},
    "active_users": frozenset(),
    "last_timestamp": 0,
}
"""Початковий стан reducer-а; ніколи не мутується — step повертає новий словник."""


def _check_ts(ts: int) -> int:
    if ts < 0:
        raise ValueError(f"negative timestamp: {ts}")
    return ts


def level_rank(level: Level) -> int:
    """Числова вага рівня помилки для порівнянь."""
    match level:
        case "warning":
            return 1
        case "error":
            return 2
        case "critical":
            return 3


def kind(e: Event) -> str:
    """Назва виду події для статистики та виводу."""
    match e:
        case Login():
            return "login"
        case Logout():
            return "logout"
        case FileOpened():
            return "file"
        case ErrorEvent():
            return "error"
        case EventGroup():
            return "group"


def flatten(e: Event) -> tuple[Event, ...]:
    """Усі листові події групи у порядку обходу (новий кортеж)."""
    match e:
        case EventGroup(items=items):
            return tuple(leaf for i in items for leaf in flatten(i))
        case _:
            return (e,)


def timestamp_of(e: Event) -> int:
    """Часова мітка події; для групи — найпізніша серед вкладених (0 для порожньої)."""
    match e:
        case EventGroup(items=items):
            return max((timestamp_of(i) for i in items), default=0)
        case Login(timestamp=t) | Logout(timestamp=t):
            return _check_ts(t)
        case FileOpened(timestamp=t) | ErrorEvent(timestamp=t):
            return _check_ts(t)


def step(state: Stats, e: Event) -> Stats:
    """Крок reducer-а: повертає НОВИЙ стан, вхідний не змінюється."""
    last = max(state["last_timestamp"], timestamp_of(e))
    match e:
        case Login(user=u):
            return {
                **state,
                "logins": state["logins"] + 1,
                "active_users": state["active_users"] | {u},
                "last_timestamp": last,
            }
        case Logout(user=u):
            return {
                **state,
                "logouts": state["logouts"] + 1,
                "active_users": state["active_users"] - {u},
                "last_timestamp": last,
            }
        case FileOpened():
            return {
                **state,
                "files_opened": state["files_opened"] + 1,
                "last_timestamp": last,
            }
        case ErrorEvent(level=lvl):
            errors = {**state["errors"], lvl: state["errors"].get(lvl, 0) + 1}
            return {**state, "errors": errors, "last_timestamp": last}
        case EventGroup(items=items):
            return reduce(step, items, state)


def reduce_log(events: Iterable[Event], initial: Stats = EMPTY) -> Stats:
    """Згортає журнал подій у статистику однією чистою функцією reduce."""
    return reduce(step, events, initial)


def error_level(e: Event) -> Level | None:
    """Рівень помилки для ErrorEvent, None для решти подій."""
    match e:
        case ErrorEvent(level=lvl):
            return lvl
        case _:
            return None


def _error_levels(events: Iterable[Event]) -> list[Level]:
    leaves = (leaf for e in events for leaf in flatten(e))
    return [lvl for lvl in map(error_level, leaves) if lvl is not None]


def count_errors(events: Iterable[Event], *, min_level: Level = "warning") -> int:
    """Кількість помилок рівня не нижче min_level (з урахуванням вкладених груп)."""
    threshold = level_rank(min_level)
    return sum(1 for lvl in _error_levels(events) if level_rank(lvl) >= threshold)


def worst_level(events: Iterable[Event]) -> Level | None:
    """Найвищий рівень помилки в журналі або None, якщо помилок немає."""
    levels = _error_levels(events)
    if not levels:
        return None
    worst: Level = max(levels, key=level_rank)
    return worst
