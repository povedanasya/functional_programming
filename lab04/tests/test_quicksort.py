import random

from algorithms import quicksort
from hypothesis import given
from hypothesis import strategies as st


def test_quicksort_basic() -> None:
    assert quicksort([]) == []
    assert quicksort([1]) == [1]
    assert quicksort([3, 2, 1]) == [1, 2, 3]
    assert quicksort([2, 2, 1, 3, 2]) == [1, 2, 2, 2, 3]


def test_quicksort_random() -> None:
    xs = [random.randint(-1000, 1000) for _ in range(1000)]
    assert quicksort(xs) == sorted(xs)


def test_quicksort_does_not_mutate() -> None:
    xs = [5, 3, 9, 1]
    quicksort(xs)
    assert xs == [5, 3, 9, 1]


@given(st.lists(st.integers()))
def test_property_matches_sorted(xs: list[int]) -> None:
    assert quicksort(xs) == sorted(xs)
