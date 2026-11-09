from copy import deepcopy
from functools import partial
from operator import attrgetter, itemgetter, methodcaller
from pathlib import Path
from typing import Any

import pytest
from core import (
    adjusted_cost,
    clean_and_rank,
    filt,
    has_priority,
    mapf,
    normalize_shipment,
    pipeline,
    rank_shipments,
    total_cost,
)
from loaders import load_shipments, load_students
from models import ShipmentRank

# --- pipeline / partial / operator ---


def test_pipeline_applies_left_to_right() -> None:
    assert pipeline(2, lambda x: x * 3, lambda x: x - 1, lambda x: x * x) == 25
    assert pipeline("same") == "same"


def test_mapf_filt_are_partials() -> None:
    assert isinstance(mapf(str), partial) and isinstance(filt(bool), partial)
    out = pipeline([1, 2, 3, 4, 5], filt(lambda x: x > 2), mapf(lambda x: x * 10))
    assert list(out) == [30, 40, 50]


def test_partial_priority_and_cost() -> None:
    urgent_only = partial(has_priority, min_priority=3)
    assert urgent_only({"priority": 3}) is True
    assert urgent_only({"priority": 2}) is False
    flat = partial(adjusted_cost, per_kg=0.0, per_km=0.0, priority_rate=0.0)
    assert flat({"cost": 50.0, "weight": 9.0, "distance": 9.0, "priority": 4}) == 50.0
    row = {"cost": 120.0, "weight": 12.5, "distance": 340.0, "priority": 2}
    assert adjusted_cost(row) == pytest.approx(393.75)


def test_operator_helpers() -> None:
    rows = [{"p": 2, "c": 5}, {"p": 2, "c": 1}, {"p": 1, "c": 9}]
    assert sorted(rows, key=itemgetter("p", "c")) == [
        {"p": 1, "c": 9},
        {"p": 2, "c": 1},
        {"p": 2, "c": 5},
    ]
    assert methodcaller("upper")(methodcaller("strip")("  sh-7 ")) == "SH-7"
    s = ShipmentRank("SH-1", 1.0, 1.0, 2, 10.0, 12.0)
    assert attrgetter("priority", "adjusted")(s) == (2, 12.0)


# --- варіант 14: конвеєр відправлень ---


def test_normalize_creates_new_record(rows: list[dict[str, Any]]) -> None:
    original = deepcopy(rows)
    out = normalize_shipment(rows[0])
    assert out == {
        "id": "SH-101",
        "weight": 12.5,
        "distance": 340.0,
        "priority": 2,
        "cost": 120.0,
    }
    assert rows == original


def test_rank_shipments_top_n_and_order(rows: list[dict[str, Any]]) -> None:
    top = rank_shipments(rows, top=2, min_priority=2)
    assert [s.id for s in top] == ["SH-102", "SH-104"]
    assert [s.adjusted for s in top] == pytest.approx([1815.0, 975.0])
    everything = rank_shipments(rows, top=10)
    assert [s.id for s in everything] == [
        "SH-102",
        "SH-104",
        "SH-101",
        "SH-105",
        "SH-103",
    ]


def test_rank_shipments_filters_and_tiebreak() -> None:
    same = [
        {"id": "b", "weight": 1, "distance": 1, "priority": 1, "cost": 10},
        {"id": "a", "weight": 1, "distance": 1, "priority": 1, "cost": 10},
        {"id": "c", "weight": 1, "distance": 1, "priority": 1, "cost": 5},
    ]
    assert [s.id for s in rank_shipments(same, top=3)] == ["A", "B", "C"]
    assert rank_shipments(same, top=3, min_priority=2) == []


def test_total_cost_reduce(rows: list[dict[str, Any]]) -> None:
    top = rank_shipments(rows, top=3)
    assert total_cost(top) == pytest.approx(1815.0 + 975.0 + 393.75)
    assert total_cost([]) == 0.0


def test_no_mutation(rows: list[dict[str, Any]]) -> None:
    original = deepcopy(rows)
    rank_shipments(rows, top=5, min_priority=2)
    assert rows == original


# --- singledispatch ---

JSON = '[{"id": "x", "weight": 1, "distance": 1, "priority": 1, "cost": 1}]'
CSV = "id,weight,distance,priority,cost\nx,1,1,1,1\n"


def test_load_from_all_sources(tmp_path: Path) -> None:
    pj, pc = tmp_path / "s.json", tmp_path / "s.csv"
    pj.write_text(JSON, encoding="utf-8")
    pc.write_text(CSV, encoding="utf-8")
    expected = load_shipments(JSON)
    assert expected[0]["id"] == "x"
    assert load_shipments(str(pj)) == expected
    assert load_shipments(pj) == expected
    assert load_shipments(expected) == expected
    with open(pj, encoding="utf-8") as f:
        assert load_shipments(f) == expected
    with open(pc, encoding="utf-8") as f:
        assert load_shipments(f)[0]["id"] == "x"
    csv_rows = load_shipments(pc)
    assert csv_rows[0] == {
        "id": "x",
        "weight": "1",
        "distance": "1",
        "priority": "1",
        "cost": "1",
    }
    assert rank_shipments(csv_rows) == rank_shipments(expected)


def test_load_rejects_bad_input() -> None:
    with pytest.raises(TypeError):
        load_shipments(3.14)
    with pytest.raises(ValueError):
        load_shipments(["not", "dicts"])
    with pytest.raises(ValueError):
        load_shipments('{"id": "x"}')


# --- total_ordering ---


def test_shipment_rank_ordering() -> None:
    a = ShipmentRank("a", 1.0, 1.0, 3, 10.0, adjusted=100.0)
    b = ShipmentRank("b", 1.0, 1.0, 3, 10.0, adjusted=50.0)
    c = ShipmentRank("c", 1.0, 1.0, 1, 10.0, adjusted=500.0)
    assert c < b < a
    assert a > b and a >= b and c <= b and a != b
    assert a == ShipmentRank("a", 9.0, 9.0, 3, 99.0, adjusted=100.0)
    assert sorted([a, c, b]) == [c, b, a] and max([a, b, c]) is a
    assert len({a, b, c, ShipmentRank("a", 9.0, 9.0, 3, 99.0, adjusted=100.0)}) == 3


def test_shipment_rank_not_implemented_for_other_types() -> None:
    s = ShipmentRank("a", 1.0, 1.0, 1, 10.0)
    assert s.__eq__(1) is NotImplemented
    assert s.__lt__(1) is NotImplemented
    assert s != 1
    with pytest.raises(TypeError):
        _ = s < 1


# --- базовий приклад з методички ---


def test_clean_and_rank_students() -> None:
    rows = load_students(
        '[{"name": "  ALICE  ", "age": "19", "score": "8.5"},'
        ' {"name": "bob", "age": "17", "score": "9.1"},'
        ' {"name": "Carol", "age": "21", "score": "7.0"},'
        ' {"name": "denis", "age": "20", "score": "9.3"}]'
    )
    assert clean_and_rank(rows, top=2) == [
        {"name": "Denis", "age": 20, "score": 9.3},
        {"name": "Alice", "age": 19, "score": 8.5},
    ]
