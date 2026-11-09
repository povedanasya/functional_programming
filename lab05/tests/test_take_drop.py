from itertools import count, islice

import pytest
from streams import drop, naturals, take


def test_take_advances_shared_iterator() -> None:
    xs = count(1)
    assert take(5, xs) == [1, 2, 3, 4, 5]
    assert take(3, xs) == [6, 7, 8]


def test_drop_then_take_on_count() -> None:
    xs = drop(10, count(0))
    assert list(islice(xs, 3)) == [10, 11, 12]


def test_edge_cases() -> None:
    assert take(0, naturals()) == []
    assert take(3, []) == []
    assert list(drop(5, [1, 2])) == []
    assert list(drop(0, [1, 2])) == [1, 2]


def test_negative_n_rejected() -> None:
    with pytest.raises(ValueError):
        take(-1, naturals())
    with pytest.raises(ValueError):
        drop(-1, naturals())
