"""ADT подій системи (варіант 14): frozen dataclass, Union, Literal, Protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, TypeAlias

Level: TypeAlias = Literal["warning", "error", "critical"]
Mode: TypeAlias = Literal["read", "write"]


class Timestamped(Protocol):
    """Структурний контракт: будь-що з часовою міткою."""

    @property
    def timestamp(self) -> int: ...


@dataclass(frozen=True)
class Login:
    user: str
    timestamp: int


@dataclass(frozen=True)
class Logout:
    user: str
    timestamp: int


@dataclass(frozen=True)
class FileOpened:
    user: str
    path: str
    timestamp: int
    mode: Mode = "read"


@dataclass(frozen=True)
class ErrorEvent:
    message: str
    level: Level
    timestamp: int


@dataclass(frozen=True)
class EventGroup:
    """Вкладена структура: група подій одного запиту, може містити інші групи."""

    items: tuple[Event, ...]
    label: str = ""


Event: TypeAlias = Login | Logout | FileOpened | ErrorEvent | EventGroup
