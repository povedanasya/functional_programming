import timeit

import pytest
from hypothesis import given
from hypothesis import strategies as st
from ntree import (
    TreeNode,
    bfs_iter,
    contains,
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


def sample_tree() -> TreeNode:
    #        1
    #      / | \
    #     2  3  4
    #    / \   / \
    #   5   6 7   8
    #       |
    #       9
    return TreeNode(
        1,
        (
            TreeNode(2, (TreeNode(5), TreeNode(6, (TreeNode(9),)))),
            TreeNode(3),
            TreeNode(4, (TreeNode(7), TreeNode(8))),
        ),
    )


def test_recursive_traversals() -> None:
    t = sample_tree()
    assert list(preorder(t)) == [1, 2, 5, 6, 9, 3, 4, 7, 8]
    assert list(postorder(t)) == [5, 9, 6, 2, 3, 7, 8, 4, 1]


def test_iterative_matches_recursive() -> None:
    t = sample_tree()
    assert dfs_iter(t) == list(preorder(t))
    assert bfs_iter(t) == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_single_node_edges() -> None:
    leaf = TreeNode(7)
    assert list(preorder(leaf)) == list(postorder(leaf)) == [7]
    assert dfs_iter(leaf) == bfs_iter(leaf) == [7]
    assert height(leaf) == height_naive(leaf) == height_iter(leaf) == 1
    assert count_nodes(leaf) == 1
    assert find_path(leaf, 7) == (7,)
    assert find_path(leaf, 8) is None


@pytest.mark.parametrize(
    ("target", "path"),
    [(1, (1,)), (9, (1, 2, 6, 9)), (8, (1, 4, 8)), (3, (1, 3)), (42, None)],
)
def test_find_path(target: int, path: tuple[int, ...] | None) -> None:
    assert find_path(sample_tree(), target) == path
    assert contains(sample_tree(), target) is (path is not None)


def test_height_and_count() -> None:
    t = sample_tree()
    assert height(t) == height_naive(t) == height_iter(t) == 4
    assert count_nodes(t) == 9


def test_height_cache_api() -> None:
    height.cache_clear()
    t = shared_tree(10)
    assert height(t) == 11
    info = height.cache_info()
    assert info.currsize == 11 and info.hits == 10
    height(t)
    assert height.cache_info().hits == info.hits + 1
    height.cache_clear()
    assert height.cache_info().currsize == 0


def test_cached_matches_naive_and_faster() -> None:
    t = shared_tree(18)
    height.cache_clear()
    assert height(t) == height_naive(t) == 19
    t_naive = timeit.timeit(lambda: height_naive(t), number=1)

    def cached_run() -> int:
        height.cache_clear()
        return height(t)

    assert timeit.timeit(cached_run, number=1) < t_naive


def test_iterative_safe_on_deep_tree() -> None:
    # лінійне дерево глибини 5000: рекурсія впала б, ітерація — ні
    t = TreeNode(0)
    for k in range(1, 5001):
        t = TreeNode(k, (t,))
    assert height_iter(t) == 5001
    assert bfs_iter(t)[:3] == [5000, 4999, 4998]
    assert dfs_iter(t) == bfs_iter(t)
    with pytest.raises(RecursionError):
        list(preorder(t))


def test_tree_not_mutated() -> None:
    t = sample_tree()
    before = list(preorder(t))
    find_path(t, 9)
    height(t)
    bfs_iter(t)
    assert list(preorder(t)) == before
    with pytest.raises(AttributeError):
        t.value = 100  # type: ignore[misc]


trees = st.recursive(
    st.builds(TreeNode, st.integers(0, 50)),
    lambda kids: st.builds(TreeNode, st.integers(0, 50), st.tuples(kids, kids, kids)),
    max_leaves=30,
)


@given(trees)
def test_property_iterative_equals_recursive(t: TreeNode) -> None:
    assert dfs_iter(t) == list(preorder(t))
    assert sorted(bfs_iter(t)) == sorted(postorder(t))
    assert len(dfs_iter(t)) == count_nodes(t)
    assert height(t) == height_naive(t) == height_iter(t)


@given(trees)
def test_property_find_path_is_valid_path(t: TreeNode) -> None:
    for value in bfs_iter(t):
        path = find_path(t, value)
        assert path is not None and path[0] == t.value and path[-1] == value
        assert len(path) <= height(t)
