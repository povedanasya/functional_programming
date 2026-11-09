from itertools import islice

import pytest
from hypothesis import given
from hypothesis import strategies as st
from patterns import (
    Numbered,
    first_n,
    laps,
    numbered,
    pattern_windows,
    repeat_pattern,
    states,
    until,
)
from streams import take

LIGHTS = {"red": "green", "green": "yellow", "yellow": "red"}


def test_repeat_pattern_cycles(pattern: list[str]) -> None:
    assert take(7, repeat_pattern(pattern)) == ["A", "B", "C", "A", "B", "C", "A"]
    assert take(3, repeat_pattern("x")) == ["x", "x", "x"]


def test_numbered_sequence_and_laps(pattern: list[str]) -> None:
    assert first_n(pattern, 4) == [
        Numbered(1, "A", 0),
        Numbered(2, "B", 0),
        Numbered(3, "C", 0),
        Numbered(4, "A", 1),
    ]
    assert [x.seq for x in first_n(pattern, 3, start=10)] == [10, 11, 12]
    assert [x.lap for x in first_n(pattern, 7)] == [0, 0, 0, 1, 1, 1, 2]


def test_until_stops_by_condition(pattern: list[str]) -> None:
    stopped = until(lambda x: x.seq > 4 and x.item == "A", numbered(pattern))
    assert [x.item for x in stopped] == ["A", "B", "C", "A", "B", "C"]
    assert list(until(lambda x: True, numbered(pattern))) == []


def test_laps_exact_repetitions(pattern: list[str]) -> None:
    assert [x.item for x in laps(pattern, 2)] == ["A", "B", "C", "A", "B", "C"]
    assert list(laps(pattern, 0)) == []
    assert len(list(laps("ab", 5))) == 10


def test_states_machine() -> None:
    assert take(5, states(LIGHTS, "red")) == ["red", "green", "yellow", "red", "green"]
    assert take(3, states({1: 1}, 1)) == [1, 1, 1]


def test_pattern_windows(pattern: list[str]) -> None:
    assert take(4, pattern_windows(pattern, 2)) == [
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),
        ("A", "B"),
    ]
    assert take(2, pattern_windows(pattern, 5)) == [
        ("A", "B", "C", "A", "B"),
        ("B", "C", "A", "B", "C"),
    ]


def test_edge_cases(pattern: list[str]) -> None:
    assert first_n(pattern, 0) == []
    assert take(3, repeat_pattern(["only"])) == ["only"] * 3
    with pytest.raises(ValueError):
        list(repeat_pattern([]))
    with pytest.raises(ValueError):
        numbered([])
    with pytest.raises(ValueError):
        first_n(pattern, -1)
    with pytest.raises(ValueError):
        list(laps(pattern, -1))
    with pytest.raises(ValueError):
        list(pattern_windows(pattern, 0))


def test_pattern_not_mutated_and_independent() -> None:
    pattern = ["A", "B"]
    stream = numbered(pattern)
    assert next(stream).item == "A"
    pattern.append("Z")  # зміна списку після старту не впливає на потік
    assert [x.item for x in islice(stream, 3)] == ["B", "A", "B"]
    assert pattern == ["A", "B", "Z"]


patterns = st.lists(st.text(min_size=1, max_size=3), min_size=1, max_size=6)


@given(patterns, st.integers(min_value=0, max_value=50))
def test_property_item_is_pattern_at_seq_mod_len(pat: list[str], n: int) -> None:
    for x in first_n(pat, n):
        assert x.item == pat[(x.seq - 1) % len(pat)]
        assert x.lap == (x.seq - 1) // len(pat)


@given(patterns, st.integers(min_value=0, max_value=10))
def test_property_laps_length(pat: list[str], k: int) -> None:
    items = [x.item for x in laps(pat, k)]
    assert items == pat * k


@given(patterns, st.integers(min_value=1, max_value=5))
def test_property_windows_are_consecutive(pat: list[str], k: int) -> None:
    source = take(k + 10, repeat_pattern(pat))
    windows = take(11, pattern_windows(pat, k))
    assert windows == [tuple(source[i : i + k]) for i in range(11)]
