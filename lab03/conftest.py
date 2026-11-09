import pytest
from model import Reading, Sensor, make_sensor


@pytest.fixture
def sensor() -> Sensor:
    return make_sensor(
        1,
        "temperature",
        (Reading(0, 21.5), Reading(60, 22.5)),
        frozenset({"room"}),
        min=18.0,
        max=25.0,
    )
