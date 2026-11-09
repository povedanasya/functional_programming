from collections.abc import Iterator
from itertools import islice

from patterns import numbered, repeat_pattern, states, until
from streams import drop, moving_average, sliding_window, take


class CountingSource:
    """Ітератор, що рахує, скільки елементів у нього реально запитали."""

    def __init__(self) -> None:
        self.pulled = 0

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        self.pulled += 1
        return self.pulled


def test_take_pulls_exactly_n() -> None:
    src = CountingSource()
    assert take(4, src) == [1, 2, 3, 4]
    assert src.pulled == 4


def test_sliding_window_pulls_only_what_is_consumed() -> None:
    src = CountingSource()
    windows = sliding_window(src, 3)
    assert src.pulled == 0  # генератор ще не стартував
    assert next(windows) == (1, 2, 3)
    assert src.pulled == 3
    assert next(windows) == (2, 3, 4)
    assert src.pulled == 4


def test_pipeline_is_lazy_end_to_end() -> None:
    src = CountingSource()
    pipeline = moving_average(drop(2, src), 2)
    assert src.pulled == 2  # drop промотує n елементів одразу, вікна ще не стартували
    assert list(islice(pipeline, 2)) == [3.5, 4.5]
    assert src.pulled == 5  # 2 пропущено + 3 для двох вікон по 2


def test_states_computed_on_demand_only() -> None:
    calls = {"n": 0}

    class Transitions(dict[int, int]):
        def __getitem__(self, key: int) -> int:
            calls["n"] += 1
            return key + 1

    stream = states(Transitions(), 0)
    assert calls["n"] == 0
    assert list(islice(stream, 4)) == [0, 1, 2, 3]
    assert calls["n"] == 3  # переходів рівно на один менше за спожиті стани


def test_infinite_pattern_terminates_only_via_limiter() -> None:
    stream = until(lambda x: x.seq > 1000, numbered("ab"))
    assert len(list(stream)) == 1000
    assert take(1, drop(10**6, repeat_pattern("ab"))) == ["a"]
