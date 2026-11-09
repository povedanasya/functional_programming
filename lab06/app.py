"""Демо ЛР6: планувальник повторів задач із фіксованим і експоненційним backoff
(варіант 14). Жодних реальних затримок: sleep і clock підмінені.
"""

from __future__ import annotations

from closures import (
    exponential_delay,
    fixed_delay,
    make_counter,
    make_fake_sleep,
    make_logger,
)
from decorators import cached, retries, timed

log = make_logger("app", print)
ticks = make_counter()
fake_clock = lambda: ticks() * 0.001  # noqa: E731  — детермінований «годинник»
fake_sleep, slept = make_fake_sleep(log)

flaky_calls = make_counter()
download_calls = make_counter()


@timed("sync", logger=log, clock=fake_clock)
@retries(attempts=4, delay=fixed_delay(0.5), sleep=fake_sleep, logger=log)
def sync_task() -> str:
    """Задача з фіксованим backoff: перші два виклики падають, третій успішний."""
    if flaky_calls() < 3:
        raise ConnectionError("sync endpoint busy")
    return "synced"


@timed("download", logger=log, clock=fake_clock)
@retries(
    attempts=5,
    exceptions=(TimeoutError,),
    delay=exponential_delay(0.1, factor=2.0, max_delay=0.5),
    sleep=fake_sleep,
    logger=log,
)
def download_task(url: str) -> str:
    """Задача з експоненційним backoff (0.1, 0.2, 0.4 → 0.5 cap)."""
    if download_calls() < 4:
        raise TimeoutError(f"timeout {url}")
    return f"content of {url}"


@cached(ttl=60.0, time_fn=fake_clock)
def expensive_report(day: int) -> str:
    """Дорога операція з кешем — повторне планування не перераховує її."""
    log(f"building report for day {day}")
    return f"report-{day}"


def main() -> None:
    """Запускає задачі планувальника і показує історію пауз без очікування."""
    print("sync:", sync_task())
    print("download:", download_task("https://example.org/data"))
    print("report:", expensive_report(1), "| again:", expensive_report(1))
    print("sleeps recorded:", slept())
    print(f"total planned wait: {sum(slept()):.2f}s")


if __name__ == "__main__":
    main()
