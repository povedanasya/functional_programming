from copy import deepcopy

import pytest
from core import Order, make_processor, order_subtotal, process_orders_pure, with_total
from starter_imperative import process_orders

ARGS = {"min_total": 100.0, "discount": 0.1, "tax_rate": 0.2}


def test_referential_transparency(sample_orders: list[Order]) -> None:
    r1 = process_orders_pure(sample_orders, **ARGS)
    r2 = process_orders_pure(sample_orders, **ARGS)
    assert r1 == r2


def test_no_mutation(sample_orders: list[Order]) -> None:
    original = deepcopy(sample_orders)
    process_orders_pure(sample_orders, min_total=0, discount=0.0, tax_rate=0.0)
    assert sample_orders == original


def test_matches_imperative(sample_orders: list[Order]) -> None:
    expected = process_orders(deepcopy(sample_orders), 100, 0.1)
    assert process_orders_pure(sample_orders, **ARGS) == expected


def test_callable_policies(sample_orders: list[Order]) -> None:
    process = make_processor(
        accept=lambda s: s >= 50,
        apply_discount=lambda s: s * 0.9,
        apply_tax=lambda s: s * 1.2,
    )
    result = process(sample_orders)
    assert [o["id"] for o in result["orders"]] == [1, 4]
    assert result["revenue"] == pytest.approx((150 + 111) * 0.9 * 1.2)


def test_subtotal_and_with_total() -> None:
    order: Order = {"id": 1, "items": [{"price": 2.5, "qty": 4}], "paid": True}
    assert order_subtotal(order) == 10.0
    new = with_total(order, 42.0)
    assert new["total"] == 42.0
    assert "total" not in order
