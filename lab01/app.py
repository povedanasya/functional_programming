"""Оболонка побічних ефектів: читання JSON, друк звіту, годинник."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from core import (
    Enrollment,
    Order,
    Report,
    process_enrollments_pure,
    process_orders_pure,
    stamp_total,
)

STATUS_DISCOUNTS = {"student": 0.15, "regular": 0.0, "alumni": 0.05}

SAMPLE: list[Enrollment] = [
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
]


def load_enrollments(path: Path) -> list[Enrollment]:
    """IO-адаптер: читає реєстрації з JSON-файлу."""
    return list(json.loads(path.read_text(encoding="utf-8")))


def render_report(result: Report) -> str:
    """Перетворює чистий результат на текст звіту (без друку)."""
    lines = [
        f"Enrollment: {e['id']} {e['course']} cost: {e['cost']:.2f}"
        for e in result["enrollments"]
    ]
    return "\n".join(
        [*lines, f"Count: {result['count']}", f"Total: {result['total_cost']:.2f}"]
    )


def run(orders: list[Order]) -> None:
    """Оболонка базового завдання: друкує чистий результат process_orders_pure."""
    result = process_orders_pure(orders, min_total=100, discount=0.1, tax_rate=0.2)
    for o in result["orders"]:
        print("Processed:", o["id"], "total:", o["total"])
    print("Revenue:", result["revenue"])


def main(argv: list[str]) -> None:
    """Точка входу: читання → чисте ядро → друк; час передається в ядро."""
    enrollments = load_enrollments(Path(argv[1])) if len(argv) > 1 else SAMPLE
    result = process_enrollments_pure(
        enrollments,
        min_price=1000,
        status_rates=STATUS_DISCOUNTS,
        bundle_min=3,
        bundle_rate=0.1,
        max_discount=0.25,
        tax_rate=0.2,
    )
    print(render_report(result))
    total, stamp = stamp_total(result["total_cost"], time.time)
    print(f"Stamped: {total:.2f} at {time.strftime('%H:%M:%S', time.localtime(stamp))}")


if __name__ == "__main__":
    main(sys.argv)
