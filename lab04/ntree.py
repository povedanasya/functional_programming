"""Варіант 14: n-арне дерево з tuple дітей — рекурсивні обходи, пошук, висота.

База рекурсії: вузол без дітей (листок). Крок: обробити вузол і рекурсивно
кожну дитину з tuple children. Усі функції чисті, дерево не змінюється.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True, eq=False)
class TreeNode:
    """Вузол n-арного дерева: значення і незмінний tuple дітей.

    eq=False → хеш за ідентичністю, тому вузол можна передавати в lru_cache
    без рекурсивного хешування всього піддерева.
    """

    value: int
    children: tuple[TreeNode, ...] = ()


def preorder(node: TreeNode) -> Iterator[int]:
    """Корінь → діти зліва направо (рекурсивний генератор)."""
    yield node.value
    for child in node.children:
        yield from preorder(child)


def postorder(node: TreeNode) -> Iterator[int]:
    """Діти зліва направо → корінь."""
    for child in node.children:
        yield from postorder(child)
    yield node.value


def find_path(node: TreeNode, target: int) -> tuple[int, ...] | None:
    """Рекурсивний пошук значення; повертає шлях значень від кореня або None.

    База: значення у поточному вузлі → шлях з одного елемента.
    Крок: перша дитина, у піддереві якої знайдено target.
    """
    if node.value == target:
        return (node.value,)
    for child in node.children:
        sub = find_path(child, target)
        if sub is not None:
            return (node.value, *sub)
    return None


def contains(node: TreeNode, target: int) -> bool:
    """Чи є значення в дереві (через рекурсивний find_path)."""
    return find_path(node, target) is not None


def count_nodes(node: TreeNode) -> int:
    """Кількість вузлів: 1 + сума по дітях."""
    return 1 + sum(count_nodes(c) for c in node.children)


def height_naive(node: TreeNode) -> int:
    """Висота дерева рекурсивно без кешу: листок → 1."""
    return 1 + max((height_naive(c) for c in node.children), default=0)


@lru_cache(maxsize=100_000)
def height(node: TreeNode) -> int:
    """Висота з мемоізацією піддерев: спільні піддерева рахуються один раз."""
    return 1 + max((height(c) for c in node.children), default=0)


def dfs_iter(node: TreeNode) -> list[int]:
    """Ітеративний preorder із власним стеком (дітей кладемо у зворотному порядку)."""
    stack, out = [node], []
    while stack:
        n = stack.pop()
        out.append(n.value)
        stack.extend(reversed(n.children))
    return out


def bfs_iter(node: TreeNode) -> list[int]:
    """Ітеративний обхід у ширину через deque — не залежить від глибини стеку."""
    queue, out = deque([node]), []
    while queue:
        n = queue.popleft()
        out.append(n.value)
        queue.extend(n.children)
    return out


def height_iter(node: TreeNode) -> int:
    """Висота ітеративно: рівень за рівнем через список поточного рівня."""
    level, depth = [node], 0
    while level:
        depth += 1
        level = [c for n in level for c in n.children]
    return depth


def shared_tree(depth: int, arity: int = 2) -> TreeNode:
    """Дерево глибини depth, де всі діти вузла — ОДНЕ й те саме піддерево.

    Логічно має arity**depth листків, але фізично лише depth+1 вузлів —
    саме тут мемоізація height дає експоненційний виграш.
    """
    node = TreeNode(0)
    for level in range(1, depth + 1):
        node = TreeNode(level, (node,) * arity)
    return node
