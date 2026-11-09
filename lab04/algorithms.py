"""Базове завдання ЛР4: quicksort, обходи бінарного дерева, мемоізований Фібоначчі.

Усі рекурсивні функції чисті: вхідні списки/дерева не змінюються.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache
from random import choice


def quicksort(xs: list[int]) -> list[int]:
    """Рекурсивний quicksort із випадковим pivot; повертає новий список."""
    if len(xs) <= 1:
        return xs[:]
    p = choice(xs)
    left = [x for x in xs if x < p]
    mid = [x for x in xs if x == p]
    right = [x for x in xs if x > p]
    return quicksort(left) + mid + quicksort(right)


@dataclass(frozen=True, slots=True)
class Node:
    """Вузол бінарного дерева."""

    key: int
    left: Node | None = None
    right: Node | None = None


def preorder(t: Node | None) -> Iterator[int]:
    """Корінь → ліве → праве (рекурсивний генератор)."""
    if t is None:
        return
    yield t.key
    yield from preorder(t.left)
    yield from preorder(t.right)


def inorder(t: Node | None) -> Iterator[int]:
    """Ліве → корінь → праве."""
    if t is None:
        return
    yield from inorder(t.left)
    yield t.key
    yield from inorder(t.right)


def postorder(t: Node | None) -> Iterator[int]:
    """Ліве → праве → корінь."""
    if t is None:
        return
    yield from postorder(t.left)
    yield from postorder(t.right)
    yield t.key


def bfs_level_order(t: Node | None) -> list[int]:
    """Ітеративний обхід у ширину через deque — не залежить від глибини стеку."""
    if t is None:
        return []
    q, out = deque([t]), []
    while q:
        n = q.popleft()
        out.append(n.key)
        if n.left:
            q.append(n.left)
        if n.right:
            q.append(n.right)
    return out


def dfs_preorder_iter(t: Node | None) -> list[int]:
    """Ітеративний preorder із власним стеком (правий кладемо першим)."""
    if t is None:
        return []
    stack, out = [t], []
    while stack:
        n = stack.pop()
        out.append(n.key)
        if n.right:
            stack.append(n.right)
        if n.left:
            stack.append(n.left)
    return out


def height(t: Node | None) -> int:
    """Висота дерева рекурсивно (порожнє дерево → 0)."""
    return 0 if t is None else 1 + max(height(t.left), height(t.right))


@lru_cache(maxsize=100_000)
def fib(n: int) -> int:
    """Мемоізований Фібоначчі: O(n) замість експоненти."""
    if n < 0:
        raise ValueError("n must be >= 0")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_naive(n: int) -> int:
    """Той самий Фібоначчі без кешу — для порівняння часу."""
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


def fib_iter(n: int) -> int:
    """Ітеративний Фібоначчі: O(n) часу, O(1) пам'яті, без стеку."""
    if n < 0:
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
