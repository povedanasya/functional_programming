import pytest
from closures import (
    DelayPolicy,
    exponential_delay,
    fixed_delay,
    make_counter,
    make_fake_sleep,
)
from decorators import cached, retries, timed
from hypothesis import given
from hypothesis import strategies as st


def test_timed_outside_retries_measures_whole_schedule() -> None:
    logs: list[str] = []
    tick = make_counter()
    sleep, slept = make_fake_sleep()
    calls = make_counter()

    @timed("job", unit="s", logger=logs.append, clock=lambda: float(tick()))
    @retries(attempts=3, delay=fixed_delay(2.0), sleep=sleep, logger=logs.append)
    def job() -> int:
        if calls() < 3:
            raise ConnectionError("down")
        return 42

    assert job() == 42
    assert slept() == (2.0, 2.0)
    assert logs[-1] == "[timed] job took 1.000 s"  # один вимір на весь план
    assert sum("attempt" in m for m in logs) == 2
    assert job.__name__ == "job"


def test_cached_inside_retries_is_not_recomputed_after_success() -> None:
    hits = make_counter()
    fails = make_counter()
    sleep, slept = make_fake_sleep()

    @retries(attempts=3, delay=exponential_delay(0.1), sleep=sleep)
    @cached()
    def report(day: int) -> str:
        hits()
        if fails() == 1:
            raise RuntimeError("first time fails")
        return f"report-{day}"

    assert report(1) == "report-1"
    assert report(1) == "report-1"
    assert hits() == 3  # 1 падіння + 1 успіх, другий виклик — кеш-хіт
    assert slept() == (0.1,)


def test_fixed_vs_exponential_total_wait() -> None:
    def run(policy: DelayPolicy) -> tuple[float, ...]:
        sleep, slept = make_fake_sleep()
        calls = make_counter()

        @retries(attempts=5, delay=policy, sleep=sleep)
        def task() -> None:
            if calls() < 5:
                raise RuntimeError

        task()
        return slept()

    fixed = run(fixed_delay(0.4))
    expo = run(exponential_delay(0.1, 2.0))
    assert fixed == (0.4, 0.4, 0.4, 0.4)
    assert [round(s, 3) for s in expo] == [0.1, 0.2, 0.4, 0.8]
    assert len(set(fixed)) == 1 and list(expo) == sorted(expo)


def test_no_real_sleep_is_called(monkeypatch: pytest.MonkeyPatch) -> None:
    import time

    monkeypatch.setattr(time, "sleep", lambda _: pytest.fail("real sleep called"))
    sleep, _ = make_fake_sleep()
    calls = make_counter()

    @retries(attempts=2, delay=fixed_delay(5.0), sleep=sleep)
    def task() -> str:
        if calls() < 2:
            raise RuntimeError
        return "done"

    assert task() == "done"


@given(st.integers(min_value=1, max_value=8), st.floats(min_value=0, max_value=2))
def test_property_sleep_count_is_failures_before_success(n: int, d: float) -> None:
    sleep, slept = make_fake_sleep()
    calls = make_counter()

    @retries(attempts=n, delay=fixed_delay(d), sleep=sleep)
    def task() -> int:
        if calls() < n:
            raise RuntimeError
        return n

    assert task() == n
    assert slept() == (d,) * (n - 1)
