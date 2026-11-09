"""Чисте ядро: вартість навчальних курсів (варіант 14) і базове завдання.

Жодного I/O, глобального стану чи мутації вхідних даних.
Усі правила знижок, податку та фільтрації передаються як Callable.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import TypedDict, TypeVar


class Enrollment(TypedDict, total=False):
    id: int
    course: str
    price: float
    status: str
    courses: int
    confirmed: bool
    cost: float


class Report(TypedDict):
    count: int
    total_cost: float
    enrollments: list[Enrollment]


FilterFn = Callable[[float], bool]
DiscountRule = Callable[[Enrollment], float]
AmountFn = Callable[[float], float]
EnrollmentProcessor = Callable[[Iterable[Enrollment]], Report]
NowFn = Callable[[], float]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def final_cost(price: float, discount: float, tax_rate: float) -> float:
    """Кінцева вартість: ціна × (1 − знижка) × (1 + податок)."""
    return price * (1 - discount) * (1 + tax_rate)


def with_cost(enrollment: Enrollment, cost: float) -> Enrollment:
    """Повертає НОВУ реєстрацію з полем cost (вхідна не змінюється)."""
    return {**enrollment, "cost": cost}


def make_enrollment_processor(
    *,
    accept: FilterFn,
    discount: DiscountRule,
    apply_tax: AmountFn,
) -> EnrollmentProcessor:
    """Фабрика обробника реєстрацій: усі правила передаються як Callable."""

    def process(enrollments: Iterable[Enrollment]) -> Report:
        """Відбирає підтверджені реєстрації, що пройшли accept, і рахує cost."""
        qualified = [
            with_cost(e, apply_tax(e["price"] * (1 - discount(e))))
            for e in enrollments
            if e["confirmed"] and accept(e["price"])
        ]
        return {
            "count": len(qualified),
            "total_cost": sum(e["cost"] for e in qualified),
            "enrollments": qualified,
        }

    return process


def min_price_filter(min_price: float) -> FilterFn:
    """Правило фільтра: приймати курси з ціною не нижче порога."""
    return lambda price: price >= min_price


def status_discount(rates: Mapping[str, float], default: float = 0.0) -> DiscountRule:
    """Студентська знижка: частка з таблиці за статусом, інакше default."""
    return lambda e: rates.get(e["status"], default)


def bundle_discount(min_courses: int, rate: float) -> DiscountRule:
    """Пакетна знижка: rate, якщо куплено не менше min_courses курсів."""
    return lambda e: rate if e["courses"] >= min_courses else 0.0


def combine_discounts(*rules: DiscountRule, cap: float) -> DiscountRule:
    """Компонує правила знижок: сума знижок, але не більше cap."""
    return lambda e: min(sum(rule(e) for rule in rules), cap)


def tax(rate: float) -> AmountFn:
    """Правило податку: додає rate до суми."""
    return lambda amount: amount * (1 + rate)


def process_enrollments_pure(
    enrollments: Iterable[Enrollment],
    *,
    min_price: float,
    status_rates: Mapping[str, float],
    bundle_min: int,
    bundle_rate: float,
    max_discount: float,
    tax_rate: float,
) -> Report:
    """Чистий розрахунок вартості курсів з явними параметрами (без глобалів)."""
    process = make_enrollment_processor(
        accept=min_price_filter(min_price),
        discount=combine_discounts(
            status_discount(status_rates),
            bundle_discount(bundle_min, bundle_rate),
            cap=max_discount,
        ),
        apply_tax=tax(tax_rate),
    )
    return process(enrollments)


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Композиція справа наліво: compose(f, g)(x) == f(g(x))."""
    return lambda x: f(g(x))


def pipe(x: A, *funcs: Callable[[A], A]) -> A:
    """Конвеєр зліва направо: pipe(x, f, g) == g(f(x))."""
    for f in funcs:
        x = f(x)
    return x


def make_multiplier(k: int) -> Callable[[int], int]:
    """Фабрика множників: make_multiplier(3)(7) == 21."""
    return lambda x: x * k


def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    """Додає часову позначку; джерело часу інʼєктується ззовні."""
    return total, now()


# --- базове завдання з методички: замовлення інтернет-магазину ---


class Item(TypedDict):
    price: float
    qty: int


class Order(TypedDict, total=False):
    id: int
    items: list[Item]
    paid: bool
    total: float


class OrderReport(TypedDict):
    count: int
    revenue: float
    orders: list[Order]


Processor = Callable[[Iterable[Order]], OrderReport]


def order_subtotal(order: Order) -> float:
    """Сума позицій замовлення (базове завдання)."""
    return sum(it["price"] * it["qty"] for it in order["items"])


def with_total(order: Order, total: float) -> Order:
    """Повертає НОВЕ замовлення з полем total."""
    return {**order, "total": total}


def make_processor(
    *,
    accept: FilterFn,
    apply_discount: AmountFn,
    apply_tax: AmountFn,
) -> Processor:
    """Фабрика обробника замовлень із політиками accept / apply_discount / apply_tax."""

    def process(orders: Iterable[Order]) -> OrderReport:
        """Відбирає оплачені замовлення, що пройшли accept, і рахує total."""
        qualified = [
            with_total(o, apply_tax(apply_discount(order_subtotal(o))))
            for o in orders
            if o["paid"] and accept(order_subtotal(o))
        ]
        return {
            "count": len(qualified),
            "revenue": sum(o["total"] for o in qualified),
            "orders": qualified,
        }

    return process


def process_orders_pure(
    orders: Iterable[Order],
    *,
    min_total: float,
    discount: float,
    tax_rate: float,
) -> OrderReport:
    """Чиста версія стартового process_orders: усі параметри явні."""
    process = make_processor(
        accept=lambda subtotal: subtotal >= min_total,
        apply_discount=lambda amount: amount * (1 - discount),
        apply_tax=lambda amount: amount * (1 + tax_rate),
    )
    return process(orders)
