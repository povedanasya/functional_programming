import pytest
from closures import exponential_delay, fixed_delay, make_fake_sleep
from decorators import retries


def test_retries_fixed_backoff_succeeds_on_third_attempt() -> None:
    calls = {"n": 0}
    sleep, slept = make_fake_sleep()

    @retries(attempts=3, delay=fixed_delay(0.5), sleep=sleep)
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3
    assert slept() == (0.5, 0.5)  # фіксований backoff, без реального сну


def test_retries_exponential_backoff_with_cap() -> None:
    calls = {"n": 0}
    sleep, slept = make_fake_sleep()

    @retries(attempts=5, delay=exponential_delay(0.1, 2.0, max_delay=0.5), sleep=sleep)
    def flaky() -> int:
        calls["n"] += 1
        if calls["n"] < 5:
            raise RuntimeError("boom")
        return calls["n"]

    assert flaky() == 5
    assert [round(s, 3) for s in slept()] == [0.1, 0.2, 0.4, 0.5]


def test_retries_reraises_after_last_attempt() -> None:
    logs: list[str] = []
    sleep, slept = make_fake_sleep()

    @retries(attempts=2, delay=fixed_delay(1.0), sleep=sleep, logger=logs.append)
    def always_fails() -> None:
        raise ValueError("nope")

    with pytest.raises(ValueError):
        always_fails()
    assert slept() == (1.0,)  # після останньої спроби пауза не планується
    assert any("fail after 2" in m for m in logs)


def test_retries_only_for_listed_exceptions() -> None:
    calls = {"n": 0}

    @retries(attempts=5, exceptions=(TimeoutError,), sleep=lambda _: None)
    def wrong_kind() -> None:
        calls["n"] += 1
        raise KeyError("not retried")

    with pytest.raises(KeyError):
        wrong_kind()
    assert calls["n"] == 1


def test_retries_policy_receives_attempt_number() -> None:
    seen: list[int] = []
    calls = {"n": 0}

    def policy(attempt: int) -> float:
        seen.append(attempt)
        return 0.0

    @retries(attempts=4, delay=policy, sleep=lambda _: None)
    def flaky() -> None:
        calls["n"] += 1
        if calls["n"] < 4:
            raise RuntimeError

    flaky()
    assert seen == [1, 2, 3]


def test_retries_preserves_metadata_and_single_attempt() -> None:
    def task(x: int) -> int:
        """Doc."""
        return x

    wrapped = retries(attempts=1)(task)
    assert wrapped(3) == 3
    assert wrapped.__name__ == "task" and wrapped.__doc__ == "Doc."
    assert wrapped.__wrapped__ is task  # type: ignore[attr-defined]


def test_retries_invalid_attempts() -> None:
    with pytest.raises(ValueError):
        retries(attempts=0)
