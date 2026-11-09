import pytest
from closures import (
    exponential_delay,
    fixed_delay,
    make_counter,
    make_fake_sleep,
    make_logger,
)
from hypothesis import given
from hypothesis import strategies as st


def test_counter_keeps_state() -> None:
    c = make_counter(10)
    assert c() == 11
    assert c() == 12


def test_counters_are_independent() -> None:
    a, b = make_counter(), make_counter(100)
    assert [a(), a(), b()] == [1, 2, 101]


def test_logger_uses_injected_sink() -> None:
    lines: list[str] = []
    info = make_logger("INFO", lines.append)
    info("ready")
    assert lines == ["[INFO] ready"]


def test_fixed_delay_policy() -> None:
    policy = fixed_delay(0.25)
    assert [policy(i) for i in range(1, 5)] == [0.25, 0.25, 0.25, 0.25]
    assert fixed_delay(0.0)(7) == 0.0
    with pytest.raises(ValueError):
        fixed_delay(-1.0)


def test_exponential_delay_policy_and_cap() -> None:
    policy = exponential_delay(0.1, factor=2.0)
    assert [round(policy(i), 3) for i in range(1, 5)] == [0.1, 0.2, 0.4, 0.8]
    capped = exponential_delay(1.0, factor=3.0, max_delay=5.0)
    assert [capped(i) for i in range(1, 5)] == [1.0, 3.0, 5.0, 5.0]
    with pytest.raises(ValueError):
        exponential_delay(1.0, factor=0.0)


def test_fake_sleep_records_without_waiting() -> None:
    logs: list[str] = []
    sleep, slept = make_fake_sleep(logs.append)
    assert slept() == ()
    sleep(0.5)
    sleep(1.0)
    assert slept() == (0.5, 1.0)
    assert logs == ["(sleep 0.500s skipped)", "(sleep 1.000s skipped)"]
    other_sleep, other_slept = make_fake_sleep()
    other_sleep(9.0)
    assert slept() == (0.5, 1.0) and other_slept() == (9.0,)  # незалежний стан


@given(
    st.integers(min_value=-1000, max_value=1000), st.integers(min_value=0, max_value=50)
)
def test_property_counter_counts_calls(start: int, n: int) -> None:
    c = make_counter(start)
    assert [c() for _ in range(n)] == list(range(start + 1, start + n + 1))


@given(
    st.floats(min_value=0.0, max_value=10.0),
    st.floats(min_value=1.0, max_value=4.0),
    st.integers(min_value=1, max_value=20),
)
def test_property_exponential_is_monotone_and_bounded(
    base: float, factor: float, attempt: int
) -> None:
    policy = exponential_delay(base, factor, max_delay=100.0)
    assert 0.0 <= policy(attempt) <= policy(attempt + 1) <= 100.0
