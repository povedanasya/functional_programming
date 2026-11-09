from algorithms import (
    Node,
    bfs_level_order,
    dfs_preorder_iter,
    height,
    inorder,
    postorder,
    preorder,
)


def sample_tree() -> Node:
    #      4
    #     / \
    #    2   6
    #   / \   \
    #  1   3   7
    return Node(4, left=Node(2, Node(1), Node(3)), right=Node(6, None, Node(7)))


def test_traversals() -> None:
    t = sample_tree()
    assert list(preorder(t)) == [4, 2, 1, 3, 6, 7]
    assert list(inorder(t)) == [1, 2, 3, 4, 6, 7]
    assert list(postorder(t)) == [1, 3, 2, 7, 6, 4]
    assert bfs_level_order(t) == [4, 2, 6, 1, 3, 7]
    assert dfs_preorder_iter(t) == [4, 2, 1, 3, 6, 7]


def test_empty_and_height() -> None:
    assert list(preorder(None)) == []
    assert bfs_level_order(None) == []
    assert dfs_preorder_iter(None) == []
    assert height(None) == 0
    assert height(sample_tree()) == 3


def test_iterative_matches_recursive_on_deep_tree() -> None:
    # лінійне дерево глибини 200: рекурсивний генератор ще в межах ліміту
    t: Node | None = None
    for k in range(200, 0, -1):
        t = Node(k, left=t)
    assert dfs_preorder_iter(t) == list(preorder(t)) == list(range(1, 201))
    assert height(t) == 200
