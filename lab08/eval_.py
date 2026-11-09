"""Чистий eval для базового AST через match/case із перевіркою діапазону."""

from __future__ import annotations

from typing import Final

from expr import Add, Expr, Mul, Num

MAX_ABS: Final[int] = 10_000


class EvalOverflow(ValueError):
    """Результат вийшов за межі ±MAX_ABS."""


def _check_range(x: int) -> int:
    if abs(x) > MAX_ABS:
        raise EvalOverflow(f"overflow: {x}")
    return x


def eval_expr(e: Expr) -> int:
    """Обчислює вираз рекурсивно; кожен проміжний результат перевіряється."""
    match e:
        case Num(value=v):
            return _check_range(v)
        case Add(left=a, right=b):
            return _check_range(eval_expr(a) + eval_expr(b))
        case Mul(left=a, right=b):
            return _check_range(eval_expr(a) * eval_expr(b))


def render(e: Expr) -> str:
    """Повністю дужковий текст виразу."""
    match e:
        case Num(value=v):
            return str(v)
        case Add(left=a, right=b):
            return f"({render(a)} + {render(b)})"
        case Mul(left=a, right=b):
            return f"({render(a)} * {render(b)})"
