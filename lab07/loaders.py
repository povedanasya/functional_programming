"""Поліморфне завантаження відправлень через functools.singledispatch (ЛР7)."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping
from functools import singledispatch
from pathlib import Path
from typing import Any

Rows = list[dict[str, Any]]


def _check(rows: Any) -> Rows:
    """Мінімальна валідація готової колекції: список словників."""
    if not isinstance(rows, list) or any(not isinstance(r, Mapping) for r in rows):
        raise ValueError("Expected list of dicts")
    return [dict(r) for r in rows]


def _from_csv(text: str) -> Rows:
    """CSV-текст → список словників (значення лишаються рядками)."""
    return list(csv.DictReader(io.StringIO(text.strip())))


def _parse_text(text: str) -> Rows:
    """JSON, якщо текст починається з '[', інакше CSV."""
    stripped = text.strip()
    if stripped.startswith("["):
        return _check(json.loads(stripped))
    return _from_csv(text)


@singledispatch
def load_shipments(src: object) -> Rows:
    """Повертає список словників-відправлень із JSON/CSV-джерела будь-якого типу."""
    raise TypeError(f"Unsupported type: {type(src)!r}")


@load_shipments.register
def _(src: str) -> Rows:
    """JSON-рядок або шлях до .json/.csv."""
    if src.lstrip().startswith(("[", "{")):
        return _check(json.loads(src))
    return load_shipments(Path(src))


@load_shipments.register
def _(src: Path) -> Rows:
    """Файл .json або .csv за розширенням."""
    text = src.read_text(encoding="utf-8")
    if src.suffix.lower() == ".csv":
        return _from_csv(text)
    return _check(json.loads(text))


@load_shipments.register
def _(src: io.TextIOBase) -> Rows:
    """Відкритий текстовий файл: формат визначається за вмістом."""
    return _parse_text(src.read())


@load_shipments.register
def _(src: list) -> Rows:  # type: ignore[type-arg]
    """Готова колекція словників."""
    return _check(src)


load_students = load_shipments
"""Базовий приклад з методички: той самий loader для записів студентів."""
