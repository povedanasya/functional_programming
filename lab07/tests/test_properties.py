"""Property-based тести (Hypothesis) для конвеєра відправлень."""

from copy import deepcopy
from typing import Any

from core import rank_shipments, total_cost
from hypothesis import given
from hypothesis import strategies as st
from models import ShipmentRank

rows_st = st.lists(
    st.fixed_dictionaries(
        {
            "id": st.text(min_size=1, max_size=8),
            "weight": st.floats(min_value=0, max_value=1000, allow_nan=False),
            "distance": st.floats(min_value=0, max_value=5000, allow_nan=False),
            "priority": st.integers(min_value=1, max_value=4),
            "cost": st.floats(min_value=0, max_value=10000, allow_nan=False),
        }
    ),
    max_size=25,
)


@given(rows_st, st.integers(min_value=0, max_value=10))
def test_top_is_prefix_of_sorted(rows: list[dict[str, Any]], n: int) -> None:
    full = rank_shipments(rows, top=len(rows) + 1)
    assert rank_shipments(rows, top=n) == full[:n]
    assert full == sorted(full, key=lambda s: (-s.priority, -s.adjusted, s.id))


@given(rows_st)
def test_no_mutation_and_total(rows: list[dict[str, Any]]) -> None:
    original = deepcopy(rows)
    top = rank_shipments(rows, top=5, min_priority=2)
    assert rows == original
    assert abs(total_cost(top) - sum(s.adjusted for s in top)) < 1e-6


@given(rows_st, st.integers(min_value=1, max_value=4))
def test_filter_respects_min_priority(rows: list[dict[str, Any]], p: int) -> None:
    top = rank_shipments(rows, top=100, min_priority=p)
    assert all(isinstance(s, ShipmentRank) and s.priority >= p for s in top)
    assert len(top) == sum(1 for r in rows if r["priority"] >= p)
