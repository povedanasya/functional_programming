"""Мутабельна модель «до» переходу на immutable — лише для порівняння в тестах."""

from __future__ import annotations

from typing import Any


def make_sensor_dict(id: int, kind: str) -> dict[str, Any]:
    """Сенсор як звичайний dict зі списком, множиною і вкладеним dict."""
    return {
        "id": id,
        "kind": kind,
        "readings": [],
        "labels": set(),
        "config": {},
        "enabled": True,
    }


def add_reading_inplace(sensor: dict[str, Any], ts: int, value: float) -> None:
    """Мутує список показів."""
    sensor["readings"].append({"ts": ts, "value": value})


def add_label_inplace(sensor: dict[str, Any], label: str) -> None:
    """Мутує множину міток."""
    sensor["labels"].add(label)


def stats_dict(sensor: dict[str, Any]) -> tuple[int, float, float, float]:
    """Статистика без кешу: щоразу перераховується."""
    values = [r["value"] for r in sensor["readings"]]
    if not values:
        return (0, 0.0, 0.0, 0.0)
    return (len(values), min(values), max(values), sum(values) / len(values))
