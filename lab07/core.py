"""Чисте ядро ЛР7: конвеєр на functools.partial / reduce та operator (варіант 14).

Предметна область — логістичні відправлення: id, weight, distance, priority, cost.
Жодних мутацій вхідних записів, жодного I/O.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from functools import partial, reduce
from operator import add, attrgetter, itemgetter, methodcaller
from typing import Any, TypeVar

from models import ShipmentRank

T = TypeVar("T")

Row = Mapping[str, Any]


def pipeline(value: T, *funcs: Callable[[Any], Any]) -> Any:
    """Протягує value через funcs зліва направо: pipeline(x, f, g) == g(f(x))."""
    return reduce(lambda acc, f: f(acc), funcs, value)


def mapf(fn: Callable[[Any], Any]) -> Callable[[Iterable[Any]], Iterable[Any]]:
    """partial-обгортка над map: mapf(fn)(iterable)."""
    return partial(map, fn)


def filt(pred: Callable[[Any], bool]) -> Callable[[Iterable[Any]], Iterable[Any]]:
    """partial-обгортка над filter: filt(pred)(iterable)."""
    return partial(filter, pred)


# --- варіант 14: логістичні відправлення ---

get_id = itemgetter("id")
strip, upper = methodcaller("strip"), methodcaller("upper")


def normalize_shipment(row: Row) -> dict[str, Any]:
    """Новий запис із очищеним id та числовими полями."""
    return {
        "id": upper(strip(str(get_id(row)))),
        "weight": float(row["weight"]),
        "distance": float(row["distance"]),
        "priority": int(row["priority"]),
        "cost": float(row["cost"]),
    }


def adjusted_cost(
    row: Row,
    *,
    per_kg: float = 2.0,
    per_km: float = 0.5,
    priority_rate: float = 0.25,
) -> float:
    """Скоригована вартість: (cost + weight·per_kg + distance·per_km) × надбавка.

    Надбавка за пріоритет: 1 + priority_rate × (priority − 1).
    """
    base = row["cost"] + row["weight"] * per_kg + row["distance"] * per_km
    return float(base * (1 + priority_rate * (row["priority"] - 1)))


def has_priority(row: Row, *, min_priority: int = 1) -> bool:
    """Предикат: пріоритет відправлення не нижче порога."""
    return bool(row["priority"] >= min_priority)


def with_adjusted(row: Row, pricer: Callable[[Row], float]) -> dict[str, Any]:
    """Новий запис із полем adjusted, обчисленим pricer."""
    return {**row, "adjusted": pricer(row)}


def to_rank(row: Row) -> ShipmentRank:
    """Перетворює словник на незмінний ShipmentRank."""
    return ShipmentRank(
        id=row["id"],
        weight=row["weight"],
        distance=row["distance"],
        priority=row["priority"],
        cost=row["cost"],
        adjusted=row["adjusted"],
    )


def rank_shipments(
    rows: Iterable[Row],
    *,
    top: int = 3,
    min_priority: int = 1,
    per_kg: float = 2.0,
    per_km: float = 0.5,
    priority_rate: float = 0.25,
) -> list[ShipmentRank]:
    """Конвеєр: нормалізація → фільтр за пріоритетом → вартість → сортування → Top-N."""
    accept = partial(has_priority, min_priority=min_priority)
    pricer = partial(
        adjusted_cost, per_kg=per_kg, per_km=per_km, priority_rate=priority_rate
    )
    result: list[ShipmentRank] = pipeline(
        rows,
        mapf(normalize_shipment),
        filt(accept),
        mapf(partial(with_adjusted, pricer=pricer)),
        mapf(to_rank),
        partial(sorted, key=attrgetter("id")),
        partial(sorted, key=attrgetter("priority", "adjusted"), reverse=True),
        lambda it: list(it)[:top],
    )
    return result


def total_cost(shipments: Iterable[ShipmentRank]) -> float:
    """reduce-агрегація: загальна скоригована вартість відправлень."""
    return reduce(add, map(attrgetter("adjusted"), shipments), 0.0)


# --- базовий приклад з методички: студенти ---

get_name = itemgetter("name")
title = methodcaller("title")


def normalize_student(row: Row) -> dict[str, Any]:
    """Новий запис студента: name у Title Case, age → int, score → float."""
    return {
        "name": title(strip(str(get_name(row)))),
        "age": int(row["age"]),
        "score": float(row["score"]),
    }


def clean_and_rank(rows: Iterable[Row], top: int = 3) -> list[dict[str, Any]]:
    """Нормалізувати → повнолітні → score ↓, name ↑ → Top-N."""
    result: list[dict[str, Any]] = pipeline(
        rows,
        mapf(normalize_student),
        filt(lambda r: r["age"] >= 18),
        partial(sorted, key=itemgetter("name")),
        partial(sorted, key=itemgetter("score"), reverse=True),
        lambda it: list(it)[:top],
    )
    return result
