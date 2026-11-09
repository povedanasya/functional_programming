from itertools import starmap

import pytest
from streams import moving_average, naturals, sliding_window, take, window_sums


def test_windows_basic() -> None:
    assert list(sliding_window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]


def test_window_sums() -> None:
    assert list(starmap(lambda *w: sum(w), sliding_window(range(5), 2))) == [1, 3, 5, 7]
    assert take(4, window_sums(naturals(), 3)) == [6, 9, 12, 15]


def test_moving_average() -> None:
    assert list(moving_average([1, 2, 3, 4], 2)) == [1.5, 2.5, 3.5]


def test_edge_cases() -> None:
    assert list(sliding_window([], 2)) == []
    assert list(sliding_window([1, 2], 3)) == []
    assert list(sliding_window([1, 2, 3], 3)) == [(1, 2, 3)]
    assert list(sliding_window([7], 1)) == [(7,)]


def test_invalid_window_size() -> None:
    with pytest.raises(ValueError):
        list(sliding_window([1, 2, 3], 0))
    with pytest.raises(ValueError):
        list(sliding_window([1, 2, 3], -2))
