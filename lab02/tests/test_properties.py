"""Property-based тести (Hypothesis) для конвеєра варіанта 14."""

from copy import deepcopy

from core import Track, build_chart_pipeline, reduce_listen_stats, with_total_listens
from hypothesis import given
from hypothesis import strategies as st

tracks_st = st.lists(
    st.fixed_dictionaries(
        {
            "id": st.integers(min_value=1, max_value=10_000),
            "title": st.text(min_size=1, max_size=12),
            "genre": st.sampled_from(["rock", "pop", "jazz"]),
            "listens": st.lists(st.integers(min_value=0, max_value=10**6), max_size=5),
        }
    ),
    max_size=30,
)


@given(tracks_st, st.integers(min_value=0, max_value=10))
def test_top_n_is_prefix_of_sorted(items: list[Track], n: int) -> None:
    full = build_chart_pipeline(top_n=len(items) + 1)(items)
    top = build_chart_pipeline(top_n=n)(items)
    assert top == full[:n]
    keys = [(-t["total_listens"], t["id"]) for t in full]
    assert keys == sorted(keys)


@given(tracks_st)
def test_pipeline_does_not_mutate(items: list[Track]) -> None:
    original = deepcopy(items)
    build_chart_pipeline(top_n=5, threshold=10.0)(items)
    assert items == original


@given(tracks_st)
def test_stats_are_consistent(items: list[Track]) -> None:
    totals = list(with_total_listens()(items))
    stats = reduce_listen_stats(totals)
    assert stats["count"] == len(items)
    assert abs(stats["listens_sum"] - sum(t["total_listens"] for t in totals)) < 1e-6
    if items:
        assert abs(stats["avg_listens"] * stats["count"] - stats["listens_sum"]) < 1e-6
