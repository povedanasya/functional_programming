from copy import deepcopy

import pytest
from core import (
    Record,
    Track,
    boost_genre,
    build_chart_pipeline,
    build_pipeline,
    compose,
    juxt,
    min_listens,
    normalize_titles,
    pipe,
    reduce_listen_stats,
    reduce_stats,
    sort_by_listens_desc,
    take,
    with_total_listens,
)

# --- варіант 14 ---


def test_top_n_order_and_tiebreak(tracks: list[Track]) -> None:
    top = build_chart_pipeline(top_n=3, genre="rock", factor=1.5)(tracks)
    assert [t["id"] for t in top] == [2, 1, 4]
    assert top[1]["total_listens"] == pytest.approx(1200.0)
    assert top[2]["total_listens"] == pytest.approx(1200.0)


def test_tiebreak_by_id_when_listens_equal(tracks: list[Track]) -> None:
    top = build_chart_pipeline(top_n=5, genre="rock", factor=1.5)(tracks)
    keys = [(t["total_listens"], t["id"]) for t in top]
    assert keys == sorted(keys, key=lambda k: (-k[0], k[1]))
    assert [t["id"] for t in top if t["total_listens"] == 1200.0] == [1, 4, 5]


def test_no_mutation(tracks: list[Track]) -> None:
    original = deepcopy(tracks)
    build_chart_pipeline(top_n=5, threshold=500.0)(tracks)
    reduce_listen_stats(with_total_listens()(tracks))
    assert tracks == original


def test_threshold_filter(tracks: list[Track]) -> None:
    top = build_chart_pipeline(top_n=10, genre="none", factor=1.0, threshold=1200.0)(
        tracks
    )
    assert [t["id"] for t in top] == [2, 4, 5]


def test_with_total_listens_and_boost(tracks: list[Track]) -> None:
    totals = list(with_total_listens()(tracks))
    assert [t["total_listens"] for t in totals] == [
        800.0,
        1500.0,
        160.0,
        1200.0,
        1200.0,
    ]
    boosted = list(boost_genre("rock", 2.0)(totals))
    assert [t["total_listens"] for t in boosted] == [
        1600.0,
        1500.0,
        320.0,
        1200.0,
        1200.0,
    ]
    assert "total_listens" not in tracks[0]


def test_normalize_titles(tracks: list[Track]) -> None:
    titles = [t["title"] for t in normalize_titles()(tracks)]
    assert titles[:2] == ["Bohemian Rhapsody", "Shape Of You"]


def test_reduce_listen_stats(tracks: list[Track]) -> None:
    stats = reduce_listen_stats(with_total_listens()(tracks))
    assert stats["count"] == 5
    assert stats["listens_sum"] == pytest.approx(4860.0)
    assert stats["avg_listens"] == pytest.approx(972.0)
    assert reduce_listen_stats([]) == {
        "count": 0.0,
        "listens_sum": 0.0,
        "avg_listens": 0.0,
    }


def test_composition_equals_manual_steps(tracks: list[Track]) -> None:
    manual = take(2)(
        sort_by_listens_desc()(
            min_listens(1000.0)(boost_genre("pop", 1.1)(with_total_listens()(tracks)))
        )
    )
    composed = compose(
        take(2),
        sort_by_listens_desc(),
        min_listens(1000.0),
        boost_genre("pop", 1.1),
        with_total_listens(),
    )
    assert list(composed(tracks)) == list(manual)
    assert [t["id"] for t in manual] == [2, 4]


def test_pipe_and_juxt() -> None:
    assert pipe(3, lambda x: x + 1, lambda x: x * 2) == 8
    assert compose(lambda x: x * 2, lambda x: x + 1)(3) == 8

    def length(xs: list[int]) -> int:
        return len(xs)

    def total(xs: list[int]) -> int:
        return sum(xs)

    assert juxt(length, total)([3, 1, 2]) == (3, 6)


# --- базовий приклад з методички ---


def test_base_pipeline_top_n(records: list[Record]) -> None:
    top = build_pipeline(top_n=2, city="Delhi", factor=1.1)(records)
    assert [r["id"] for r in top] == [1, 3]
    assert top[0]["name"] == "Amit"
    assert top[0]["total"] == pytest.approx(165.0)


def test_base_reduce_stats(records: list[Record]) -> None:
    stats = reduce_stats(build_pipeline(top_n=10)(records))
    assert stats["count"] == 3
    assert stats["sum_total"] == pytest.approx(165.0 + 160.0 + 110.0)
    assert stats["avg_total"] == pytest.approx(435.0 / 3)


def test_base_no_mutation(records: list[Record]) -> None:
    original = deepcopy(records)
    build_pipeline()(records)
    assert records == original
