from itertools import islice

from streams import drop, fib_stream, take


def test_first_10() -> None:
    assert list(islice(fib_stream(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_drop_then_take() -> None:
    assert take(8, drop(5, fib_stream())) == [5, 8, 13, 21, 34, 55, 89, 144]


def test_stream_is_fresh_each_call() -> None:
    assert take(3, fib_stream()) == take(3, fib_stream()) == [0, 1, 1]
