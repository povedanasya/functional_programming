from dataclasses import FrozenInstanceError

import pytest
from core import (
    add_label,
    add_reading,
    freeze,
    index_by_sensor,
    is_out_of_range,
    stats,
    with_config,
)
from hypothesis import given
from hypothesis import strategies as st
from model import Reading, Sensor, make_config, make_sensor


def test_add_reading_returns_new_sensor(sensor: Sensor) -> None:
    before = (sensor.readings, sensor.labels, dict(sensor.config))
    new = add_reading(sensor, 120, 23.0)
    assert (sensor.readings, sensor.labels, dict(sensor.config)) == before
    assert new is not sensor
    assert len(new.readings) == 3
    assert new.last_value() == 23.0 and sensor.last_value() == 22.5


def test_out_of_range_reading_adds_alert_label(sensor: Sensor) -> None:
    new = add_reading(sensor, 120, 27.0)
    assert "alert" in new.labels and "alert" not in sensor.labels
    assert is_out_of_range(sensor, 27.0) and not is_out_of_range(sensor, 20.0)


def test_add_label_returns_new_sensor(sensor: Sensor) -> None:
    new = add_label(sensor, "checked")
    assert sensor.labels == frozenset({"room"})
    assert new.labels == frozenset({"room", "checked"})
    assert new.disable().enabled is False and sensor.enabled is True


def test_frozen_fields_cannot_be_assigned(sensor: Sensor) -> None:
    with pytest.raises(FrozenInstanceError):
        sensor.kind = "humidity"  # type: ignore[misc]


def test_reading_is_tuple(sensor: Sensor) -> None:
    reading = sensor.readings[0]
    assert isinstance(reading, tuple) and reading == (0, 21.5)
    with pytest.raises(AttributeError):
        reading.value = 0.0  # type: ignore[misc]


def test_config_is_read_only(sensor: Sensor) -> None:
    with pytest.raises(TypeError):
        sensor.config["max"] = 99.0  # type: ignore[index]
    assert sensor.config["max"] == 25.0


def test_make_config_copies_source() -> None:
    raw = {"min": 1.0}
    config = make_config(**raw)
    raw["min"] = 2.0
    assert config["min"] == 1.0


def test_with_config_creates_new_mapping(sensor: Sensor) -> None:
    new = with_config(sensor, max=30.0, period=60.0)
    assert dict(new.config) == {"min": 18.0, "max": 30.0, "period": 60.0}
    assert dict(sensor.config) == {"min": 18.0, "max": 25.0}


def test_hashability_and_dict_key(sensor: Sensor) -> None:
    other = add_label(sensor, "checked")
    assert len({sensor, other, add_label(sensor, "checked")}) == 2
    index = index_by_sensor((sensor, other))
    assert index[sensor].mean == pytest.approx(22.0)
    assert index[other] == index[sensor]
    assert set(index) == {sensor, other}


def test_stats_and_cache(sensor: Sensor) -> None:
    stats.cache_clear()
    assert stats(sensor) == (2, 21.5, 22.5, 22.0)
    stats(sensor)
    info = stats.cache_info()
    assert info.hits == 1 and info.misses == 1
    assert stats(add_reading(sensor, 120, 27.0)).high == 27.0
    assert stats(make_sensor(2, "humidity")) == (0, 0.0, 0.0, 0.0)


def test_freeze_deep() -> None:
    frozen = freeze({"a": [1, {2, 3}], "b": {"c": [4]}})
    with pytest.raises(TypeError):
        frozen["a"] = 0
    assert frozen["a"] == (1, frozenset({2, 3}))
    with pytest.raises(TypeError):
        frozen["b"]["c"] = 0
    assert frozen["b"]["c"] == (4,)


readings_st = st.tuples(
    st.integers(min_value=0, max_value=10**6),
    st.floats(min_value=-50, max_value=150, allow_nan=False),
).map(lambda t: Reading(*t))
sensors_st = st.builds(
    make_sensor,
    st.integers(min_value=1),
    st.sampled_from(["temperature", "humidity", "pressure"]),
    st.tuples(readings_st, readings_st).map(tuple),
    st.frozensets(st.text(min_size=1, max_size=6)),
)


@given(sensors_st, readings_st)
def test_property_add_reading_pure(s: Sensor, r: Reading) -> None:
    before = (s.readings, s.labels, dict(s.config))
    new = s.add_reading(r)
    assert (s.readings, s.labels, dict(s.config)) == before
    assert new.readings == s.readings + (r,)
    assert new.last_value() == r.value


@given(sensors_st)
def test_property_hash_consistent_with_eq(s: Sensor) -> None:
    twin = Sensor(s.id, s.kind, s.readings, s.labels, s.config, s.enabled)
    assert twin == s and hash(twin) == hash(s)
    assert stats(s) == stats(twin)
