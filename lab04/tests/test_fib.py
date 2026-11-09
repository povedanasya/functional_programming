import pytest
from algorithms import fib, fib_iter, fib_naive


def test_fib_small() -> None:
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert [fib(i) for i in range(10)] == expected
    assert [fib_naive(i) for i in range(10)] == expected


def test_fib_iter_matches() -> None:
    for n in range(50):
        assert fib(n) == fib_iter(n)


def test_cache_clear_and_info() -> None:
    fib.cache_clear()
    assert fib(0) == 0
    fib(25)
    info = fib.cache_info()
    assert info.currsize == 26
    assert info.hits > 0


def test_negative_rejected() -> None:
    with pytest.raises(ValueError):
        fib(-1)
    with pytest.raises(ValueError):
        fib_iter(-1)
