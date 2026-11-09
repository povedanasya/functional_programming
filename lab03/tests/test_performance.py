"""Порівняння часу: модель «до» (mutable) і «після» (immutable), --durations=5."""

from core import add_label, add_reading, stats
from model import Sensor
from mutable_model import (
    add_label_inplace,
    add_reading_inplace,
    make_sensor_dict,
    stats_dict,
)

N = 2_000


def test_mutable_before() -> None:
    s = make_sensor_dict(1, "temperature")
    for i in range(N):
        add_reading_inplace(s, i, 20.0 + i % 7)
    add_label_inplace(s, "checked")
    total = sum(stats_dict(s)[3] for _ in range(N))
    assert total > 0


def test_immutable_after(sensor: Sensor) -> None:
    s = sensor
    for i in range(N):
        s = add_reading(s, i, 20.0 + i % 7)
    s = add_label(s, "checked")
    stats.cache_clear()
    total = sum(stats(s).mean for _ in range(N))
    assert total > 0
    assert stats.cache_info().hits == N - 1
