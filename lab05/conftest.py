import pytest


@pytest.fixture
def pattern() -> list[str]:
    return ["A", "B", "C"]
