import pytest
from decorators import timed


def test_timed_uses_clock_and_logger() -> None:
    ticks = iter([0.0, 0.012345])
    logs: list[str] = []

    @timed("work", unit="ms", logger=logs.append, clock=lambda: next(ticks))
    def work(x: int) -> int:
        """Квадрат."""
        return x * x

    assert work(5) == 25
    assert logs == ["[timed] work took 12.345 ms"]


def test_timed_logs_even_on_exception() -> None:
    ticks = iter([1.0, 3.0])
    logs: list[str] = []

    @timed(unit="s", logger=logs.append, clock=lambda: next(ticks))
    def boom() -> None:
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        boom()
    assert logs == ["[timed] boom took 2.000 s"]


def test_timed_preserves_metadata() -> None:
    def original(a: int) -> int:
        """Doc."""
        return a

    wrapped = timed(logger=lambda _: None, clock=lambda: 0.0)(original)
    assert wrapped.__name__ == "original"
    assert wrapped.__doc__ == "Doc."
    assert wrapped.__wrapped__ is original  # type: ignore[attr-defined]


def test_timed_units() -> None:
    logs: list[str] = []
    ticks = iter([0.0, 2.0])
    timed(unit="us", logger=logs.append, clock=lambda: next(ticks))(lambda: None)()
    assert logs[0].endswith("2000000.000 us")
