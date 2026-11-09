"""Базове завдання з методички: AST Expr = Num | Add | Mul і форма Bin з Literal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, TypeAlias


@dataclass(frozen=True)
class Num:
    value: int


@dataclass(frozen=True)
class Add:
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Mul:
    left: Expr
    right: Expr


Expr: TypeAlias = Num | Add | Mul

Op: TypeAlias = Literal["+", "*"]


@dataclass(frozen=True)
class Num2:
    value: int


@dataclass(frozen=True)
class Bin:
    op: Op
    left: Expr2
    right: Expr2


Expr2: TypeAlias = Num2 | Bin


class SupportsBin(Protocol):
    """Структурний контракт бінарного вузла."""

    @property
    def op(self) -> Op: ...

    @property
    def left(self) -> Expr2: ...

    @property
    def right(self) -> Expr2: ...


def eval_expr2(e: Expr2) -> int:
    """Чистий обчислювач альтернативного AST з оператором-літералом."""
    match e:
        case Num2(value=v):
            return v
        case Bin(op="+", left=a, right=b):
            return eval_expr2(a) + eval_expr2(b)
        case Bin(op="*", left=a, right=b):
            return eval_expr2(a) * eval_expr2(b)
        case _:
            raise ValueError(f"unknown node: {e!r}")
