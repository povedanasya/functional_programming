from copy import deepcopy

import pytest
from app import render_report
from core import (
    Enrollment,
    Report,
    bundle_discount,
    combine_discounts,
    compose,
    final_cost,
    make_enrollment_processor,
    make_multiplier,
    min_price_filter,
    pipe,
    process_enrollments_pure,
    stamp_total,
    status_discount,
    tax,
    with_cost,
)
from starter_imperative import process_enrollments

RATES = {"student": 0.15, "regular": 0.0, "alumni": 0.05}


def run(enrollments: list[Enrollment]) -> Report:
    return process_enrollments_pure(
        enrollments,
        min_price=1000.0,
        status_rates=RATES,
        bundle_min=3,
        bundle_rate=0.1,
        max_discount=0.25,
        tax_rate=0.2,
    )


def test_referential_transparency(sample_enrollments: list[Enrollment]) -> None:
    r1 = run(sample_enrollments)
    r2 = run(sample_enrollments)
    assert r1 == r2


def test_no_mutation(sample_enrollments: list[Enrollment]) -> None:
    original = deepcopy(sample_enrollments)
    process_enrollments_pure(
        sample_enrollments,
        min_price=0,
        status_rates=RATES,
        bundle_min=1,
        bundle_rate=0.5,
        max_discount=1.0,
        tax_rate=0.0,
    )
    assert sample_enrollments == original


def test_matches_imperative(sample_enrollments: list[Enrollment]) -> None:
    expected = process_enrollments(deepcopy(sample_enrollments), 1000)
    assert run(sample_enrollments) == expected


def test_filters_unconfirmed_and_cheap(sample_enrollments: list[Enrollment]) -> None:
    result = run(sample_enrollments)
    assert [e["id"] for e in result["enrollments"]] == [1, 4, 5]
    assert result["count"] == 3
    assert result["total_cost"] == pytest.approx(
        (4000 * 0.85 + 9000 * 0.75 + 2000 * 0.85) * 1.2
    )


def test_final_cost() -> None:
    assert final_cost(1000.0, 0.1, 0.2) == pytest.approx(1080.0)
    assert final_cost(0.0, 0.5, 0.2) == 0.0


def test_with_cost_returns_new_dict() -> None:
    enrollment: Enrollment = {
        "id": 1,
        "course": "Python",
        "price": 100.0,
        "status": "student",
        "courses": 1,
        "confirmed": True,
    }
    new = with_cost(enrollment, 42.0)
    assert new == {**enrollment, "cost": 42.0}
    assert "cost" not in enrollment
    assert new is not enrollment


def test_callable_policies(sample_enrollments: list[Enrollment]) -> None:
    process = make_enrollment_processor(
        accept=lambda price: price >= 3000,
        discount=lambda e: 0.5 if e["status"] == "student" else 0.0,
        apply_tax=lambda amount: amount,
    )
    result = process(sample_enrollments)
    assert [e["id"] for e in result["enrollments"]] == [1, 4]
    assert result["total_cost"] == pytest.approx(4000 * 0.5 + 9000 * 0.5)


def test_discount_rules() -> None:
    student: Enrollment = {"status": "student", "courses": 1}
    bulk: Enrollment = {"status": "unknown", "courses": 5}
    assert min_price_filter(500)(499.9) is False
    assert min_price_filter(500)(500) is True
    assert status_discount(RATES)(student) == 0.15
    assert status_discount(RATES, default=0.01)(bulk) == 0.01
    assert bundle_discount(3, 0.1)(student) == 0.0
    assert bundle_discount(3, 0.1)(bulk) == 0.1
    assert tax(0.2)(100.0) == pytest.approx(120.0)


def test_combine_discounts_is_capped() -> None:
    rule = combine_discounts(status_discount(RATES), bundle_discount(3, 0.1), cap=0.2)
    assert rule({"status": "student", "courses": 1}) == pytest.approx(0.15)
    assert rule({"status": "student", "courses": 3}) == pytest.approx(0.2)
    assert rule({"status": "regular", "courses": 3}) == pytest.approx(0.1)


def test_compose_and_multiplier() -> None:
    assert make_multiplier(3)(7) == 21
    assert compose(make_multiplier(2), make_multiplier(5))(1) == 10
    assert pipe(1, make_multiplier(2), make_multiplier(5)) == 10
    priced = compose(tax(0.2), tax(-0.1))
    assert priced(100.0) == pytest.approx(108.0)


def test_stamp_total_uses_injected_clock() -> None:
    assert stamp_total(10.0, lambda: 123.0) == (10.0, 123.0)


def test_render_report(sample_enrollments: list[Enrollment]) -> None:
    text = render_report(run(sample_enrollments))
    assert text.splitlines() == [
        "Enrollment: 1 Python cost: 4080.00",
        "Enrollment: 4 Data Science cost: 8100.00",
        "Enrollment: 5 Go cost: 2040.00",
        "Count: 3",
        "Total: 14220.00",
    ]
