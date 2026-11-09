"""Незмінна модель IoT-сенсорів (варіант 14).

Reading — NamedTuple (кортеж з іменованими полями), Sensor — frozen dataclass зі slots;
покази у tuple, мітки у frozenset, конфігурація — MappingProxyType поверх копії
словника.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Literal, NamedTuple

Kind = Literal["temperature", "humidity", "pressure"]


class Reading(NamedTuple):
    """Один показ сенсора: момент часу (с) та значення."""

    ts: int
    value: float


@dataclass(frozen=True, slots=True)
class Sensor:
    """Сенсор: покази (tuple), мітки (frozenset), config (read-only)."""

    id: int
    kind: Kind
    readings: tuple[Reading, ...]
    labels: frozenset[str]
    # mappingproxy не хешується → виключаємо з hash (у eq лишається)
    config: Mapping[str, float] = field(hash=False)
    enabled: bool = True

    def last_value(self) -> float | None:
        """Останній показ або None, якщо показів ще немає."""
        return self.readings[-1].value if self.readings else None

    def add_reading(self, reading: Reading) -> Sensor:
        """Новий сенсор із доданим показом."""
        return replace(self, readings=self.readings + (reading,))

    def add_label(self, label: str) -> Sensor:
        """Новий сенсор із доданою міткою."""
        return replace(self, labels=self.labels | frozenset({label}))

    def disable(self) -> Sensor:
        """Новий сенсор, вимкнений."""
        return replace(self, enabled=False)


def make_config(**kwargs: float) -> Mapping[str, float]:
    """Read-only view над КОПІЄЮ словника, щоб ніхто не тримав посилання на оригінал."""
    return MappingProxyType(dict(kwargs))


def make_sensor(
    id: int,
    kind: Kind,
    readings: tuple[Reading, ...] = (),
    labels: frozenset[str] = frozenset(),
    **config: float,
) -> Sensor:
    """Зручний конструктор сенсора з read-only конфігурацією."""
    return Sensor(id, kind, readings, labels, make_config(**config))
