"""Property-based тести (Hypothesis) для чистого ядра."""

from copy import deepcopy

from core import Enrollment, Report, process_enrollments_pure
from hypothesis import given
from hypothesis import strategies as st

RATES = {"student": 0.15, "regular": 0.0, "alumni": 0.05}


def run(items: list[Enrollment]) -> Report:
    return process_enrollments_pure(
        items,
        min_price=0.0,
        status_rates=RATES,
        bundle_min=3,
        bundle_rate=0.1,
        max_discount=0.25,
        tax_rate=0.2,
    )


enrollments = st.lists(
    st.fixed_dictionaries(
        {
            "id": st.integers(min_value=1),
            "course": st.text(min_size=1, max_size=10),
            "price": st.floats(min_value=0, max_value=1e6, allow_nan=False),
            "status": st.sampled_from(["student", "regular", "alumni"]),
            "courses": st.integers(min_value=1, max_value=20),
            "confirmed": st.booleans(),
        }
    ),
    max_size=20,
)


@given(enrollments)
def test_property_referential_transparency(items: list[Enrollment]) -> None:
    assert run(items) == run(items)


@given(enrollments)
def test_property_no_mutation(items: list[Enrollment]) -> None:
    original = deepcopy(items)
    run(items)
    assert items == original


@given(enrollments)
def test_property_total_is_sum_and_only_confirmed(items: list[Enrollment]) -> None:
    result = run(items)
    assert result["count"] == sum(1 for e in items if e["confirmed"])
    assert result["total_cost"] == sum(e["cost"] for e in result["enrollments"])
    assert all(
        e["price"] * 0.75 * 1.2 - 1e-6 <= e["cost"] <= e["price"] * 1.2 + 1e-6
        for e in result["enrollments"]
    )
