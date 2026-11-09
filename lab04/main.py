"""Демо ЛР4: обходи n-арного дерева, пошук, висота з кешем/без, базові алгоритми."""

from __future__ import annotations

import sys
import timeit

from algorithms import (
    Node,
    bfs_level_order,
    fib,
    fib_iter,
    fib_naive,
    inorder,
    quicksort,
)
from ntree import (
    TreeNode,
    bfs_iter,
    count_nodes,
    dfs_iter,
    find_path,
    height,
    height_iter,
    height_naive,
    postorder,
    preorder,
    shared_tree,
)


def main() -> None:
    """Друкує результати та таблицю часу (лише I/O, обчислення чисті)."""
    tree = TreeNode(
        1,
        (
            TreeNode(2, (TreeNode(5), TreeNode(6, (TreeNode(9),)))),
            TreeNode(3),
            TreeNode(4, (TreeNode(7), TreeNode(8))),
        ),
    )
    print("preorder :", list(preorder(tree)), "dfs_iter:", dfs_iter(tree))
    print("postorder:", list(postorder(tree)))
    print("bfs_iter :", bfs_iter(tree))
    print("find 9   :", find_path(tree, 9), " find 42:", find_path(tree, 42))
    print("nodes:", count_nodes(tree), "height:", height(tree), height_iter(tree))

    big = shared_tree(22)

    def cached_run() -> int:
        height.cache_clear()
        return height(big)

    t_cached = timeit.timeit(cached_run, number=1)
    t_naive = timeit.timeit(lambda: height_naive(big), number=1)
    print(f"height(shared_tree(22)) cached: {t_cached * 1e3:.3f} ms")
    print(f"height(shared_tree(22)) naive : {t_naive * 1e3:.1f} ms")
    print("cache_info:", height.cache_info())

    fib.cache_clear()
    print("fib(30) cached:", f"{timeit.timeit(lambda: fib(30), number=1) * 1e3:.3f} ms")
    print(
        "fib(30) naive :",
        f"{timeit.timeit(lambda: fib_naive(30), number=1) * 1e3:.1f} ms",
    )
    print("fib(90) ==", fib(90), "iter:", fib_iter(90))

    print("quicksort:", quicksort([3, 1, 4, 1, 5, 9, 2, 6]))
    t = Node(4, Node(2, Node(1), Node(3)), Node(6, None, Node(7)))
    print("inorder:", list(inorder(t)), "bfs:", bfs_level_order(t))
    print("recursion limit:", sys.getrecursionlimit())


if __name__ == "__main__":
    main()
