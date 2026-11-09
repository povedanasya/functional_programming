"""Стартові імперативні фрагменти (з методички та за варіантом 14) для тестів."""

from typing import Any

TAX_RATE = 0.2  # глобальний стан
STATUS_DISCOUNTS = {"student": 0.15, "regular": 0.0, "alumni": 0.05}
BUNDLE_MIN_COURSES = 3
BUNDLE_DISCOUNT = 0.1
MAX_DISCOUNT = 0.25


def process_orders(
    orders: list[Any], min_total: float, discount: float
) -> dict[str, Any]:
    valid: list[dict[str, Any]] = []
    total_revenue = 0.0

    for o in orders:
        if not o["paid"]:
            continue
        print("Processing order:", o["id"])

        order_total = 0.0
        for it in o["items"]:
            order_total += it["price"] * it["qty"]
        if order_total < min_total:
            continue

        order_total = order_total * (1 - discount)
        order_total = order_total * (1 + TAX_RATE)

        o["total"] = order_total
        valid.append(o)
        total_revenue += order_total

    return {"count": len(valid), "revenue": total_revenue, "orders": valid}


def process_enrollments(enrollments: list[Any], min_price: float) -> dict[str, Any]:
    valid: list[dict[str, Any]] = []
    total_cost = 0.0

    for e in enrollments:
        if not e["confirmed"]:
            continue
        print("Processing enrollment:", e["id"])

        price = e["price"]
        if price < min_price:
            continue

        discount = STATUS_DISCOUNTS[e["status"]]
        if e["courses"] >= BUNDLE_MIN_COURSES:
            discount += BUNDLE_DISCOUNT
        if discount > MAX_DISCOUNT:
            discount = MAX_DISCOUNT
        cost = price * (1 - discount)
        cost = cost * (1 + TAX_RATE)

        e["cost"] = cost
        valid.append(e)
        total_cost += cost

    return {"count": len(valid), "total_cost": total_cost, "enrollments": valid}
