"""Чисті бізнес-функції над незмінною моделлю сенсорів (варіант 14).

Жодна функція не змінює вхідні об'єкти: кожне оновлення повертає новий Sensor,
розрахунок статистики кешується через lru_cache (можливо лише тому,
що Sensor хешований).
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from types import MappingProxyType
from typing import Any, NamedTuple

from model import Reading, Sensor


class Stats(NamedTuple):
    """Статистика показів: кількість, мінімум, максимум, середнє."""

    n: int
    low: float
    high: float
    mean: float


@lru_cache(maxsize=1024)
def stats(sensor: Sensor) -> Stats:
    """Статистика за всіма показами сенсора. Кешується."""
    values = [r.value for r in sensor.readings]
    if not values:
        return Stats(0, 0.0, 0.0, 0.0)
    return Stats(len(values), min(values), max(values), sum(values) / len(values))


def is_out_of_range(sensor: Sensor, value: float) -> bool:
    """Чи виходить значення за межі min/max із конфігурації (якщо вони задані)."""
    low = sensor.config.get("min", float("-inf"))
    high = sensor.config.get("max", float("inf"))
    return not low <= value <= high


def add_reading(sensor: Sensor, ts: int, value: float) -> Sensor:
    """Pure update: новий сенсор із доданим показом; поза межами → мітка alert."""
    updated = sensor.add_reading(Reading(ts, value))
    return updated.add_label("alert") if is_out_of_range(sensor, value) else updated


def add_label(sensor: Sensor, label: str) -> Sensor:
    """Pure update: новий сенсор із доданою міткою."""
    return sensor.add_label(label)


def with_config(sensor: Sensor, **updates: float) -> Sensor:
    """Pure update: новий сенсор із новою read-only конфігурацією (копія + зміни)."""
    merged = {**sensor.config, **updates}
    return Sensor(
        sensor.id,
        sensor.kind,
        sensor.readings,
        sensor.labels,
        MappingProxyType(merged),
        sensor.enabled,
    )


def recalculate(sensor: Sensor) -> tuple[Sensor, Stats]:
    """Повертає той самий сенсор і його статистику (кешовану)."""
    return sensor, stats(sensor)


def index_by_sensor(sensors: tuple[Sensor, ...]) -> Mapping[Sensor, Stats]:
    """Сенсор як ключ словника (хешованість frozen dataclass) → статистика."""
    return MappingProxyType({s: stats(s) for s in sensors})


def freeze(obj: Any) -> Any:
    """Глибоке заморожування: dict → MappingProxyType, set → frozenset, list → tuple."""
    if isinstance(obj, Mapping):
        return MappingProxyType({k: freeze(v) for k, v in obj.items()})
    if isinstance(obj, (set, frozenset)):
        return frozenset(freeze(x) for x in obj)
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(x) for x in obj)
    return obj
