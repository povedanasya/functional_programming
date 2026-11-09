import pytest
from core import Record, Track


@pytest.fixture
def tracks() -> list[Track]:
    return [
        {"id": 1, "title": "bohemian rhapsody", "genre": "rock", "listens": [500, 300]},
        {"id": 2, "title": "SHAPE OF YOU", "genre": "pop", "listens": [1500]},
        {
            "id": 3,
            "title": "nothing else matters",
            "genre": "rock",
            "listens": [100, 60],
        },
        {"id": 4, "title": "blinding lights", "genre": "pop", "listens": [1200]},
        {"id": 5, "title": "take five", "genre": "jazz", "listens": [700, 500]},
    ]


@pytest.fixture
def records() -> list[Record]:
    return [
        {
            "id": 1,
            "name": "amit",
            "age": 30,
            "city": "Delhi",
            "purchases": [100.0, 50.0],
        },
        {"id": 2, "name": "neha", "age": 17, "city": "Delhi", "purchases": [500.0]},
        {"id": 3, "name": "raj", "age": 25, "city": "Mumbai", "purchases": [160.0]},
        {
            "id": 4,
            "name": "sita",
            "age": 40,
            "city": "Delhi",
            "purchases": [60.0, 40.0],
        },
    ]
