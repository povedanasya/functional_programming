import pytest
from core import Enrollment, Order


@pytest.fixture
def sample_enrollments() -> list[Enrollment]:
    return [
        {
            "id": 1,
            "course": "Python",
            "price": 4000.0,
            "status": "student",
            "courses": 1,
            "confirmed": True,
        },
        {
            "id": 2,
            "course": "SQL",
            "price": 800.0,
            "status": "regular",
            "courses": 2,
            "confirmed": True,
        },
        {
            "id": 3,
            "course": "Java",
            "price": 6000.0,
            "status": "alumni",
            "courses": 4,
            "confirmed": False,
        },
        {
            "id": 4,
            "course": "Data Science",
            "price": 9000.0,
            "status": "student",
            "courses": 3,
            "confirmed": True,
        },
        {
            "id": 5,
            "course": "Go",
            "price": 2000.0,
            "status": "alumni",
            "courses": 5,
            "confirmed": True,
        },
    ]


@pytest.fixture
def sample_orders() -> list[Order]:
    return [
        {"id": 1, "items": [{"price": 50.0, "qty": 3}], "paid": True},
        {"id": 2, "items": [{"price": 20.0, "qty": 1}], "paid": True},
        {"id": 3, "items": [{"price": 200.0, "qty": 1}], "paid": False},
        {
            "id": 4,
            "items": [{"price": 10.0, "qty": 10}, {"price": 5.5, "qty": 2}],
            "paid": True,
        },
    ]
