"""Текстове представлення подій через match/case."""

from __future__ import annotations

from typing import Protocol

from model import ErrorEvent, Event, EventGroup, FileOpened, Login, Logout


class Renders(Protocol):
    """Структурний контракт для будь-чого, що вміє відрендерити себе."""

    def render(self) -> str: ...


def describe(e: Event, indent: int = 0) -> str:
    """Багаторядковий опис події; групи рендеряться рекурсивно з відступом."""
    pad = "  " * indent
    match e:
        case Login(user=u, timestamp=t):
            return f"{pad}[{t}] login {u}"
        case Logout(user=u, timestamp=t):
            return f"{pad}[{t}] logout {u}"
        case FileOpened(user=u, path=p, timestamp=t, mode="write"):
            return f"{pad}[{t}] {u} writes {p}"
        case FileOpened(user=u, path=p, timestamp=t):
            return f"{pad}[{t}] {u} opens {p}"
        case ErrorEvent(message=m, level="critical", timestamp=t):
            return f"{pad}[{t}] !!! CRITICAL: {m}"
        case ErrorEvent(message=m, level=lvl, timestamp=t):
            return f"{pad}[{t}] {lvl}: {m}"
        case EventGroup(items=items, label=label):
            head = f"{pad}group {label or '(unnamed)'} [{len(items)}]"
            return "\n".join([head, *(describe(i, indent + 1) for i in items)])
