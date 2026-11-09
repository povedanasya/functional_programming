from decorators import cached
from hypothesis import given
from hypothesis import strategies as st


def test_cached_ttl_and_invalidate() -> None:
    now = {"t": 1000.0}
    hits = {"n": 0}

    @cached(ttl=1.0, time_fn=lambda: now["t"])
    def f(x: int) -> int:
        hits["n"] += 1
        return x * 2

    assert f(10) == 20 and f(10) == 20
    assert hits["n"] == 1
    now["t"] += 2.0  # TTL минув
    assert f(10) == 20
    assert hits["n"] == 2
    assert f.cache_invalidate(lambda a, kw: a == (10,)) == 1
    assert f(10) == 20
    assert hits["n"] == 3


def test_cache_clear_and_size() -> None:
    @cached()
    def g(x: int, *, y: int = 0) -> int:
        return x + y

    g(1), g(1, y=2), g(2)
    assert g.cache_size() == 3
    assert g(1, y=2) == 3
    g.cache_clear()
    assert g.cache_size() == 0


def test_cached_preserves_metadata() -> None:
    @cached()
    def documented(x: int) -> int:
        """Doc."""
        return x

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "Doc."


@given(st.lists(st.integers(min_value=-50, max_value=50), min_size=1, max_size=30))
def test_property_each_distinct_arg_computed_once(xs: list[int]) -> None:
    hits = {"n": 0}

    @cached()
    def sq(x: int) -> int:
        hits["n"] += 1
        return x * x

    assert [sq(x) for x in xs] == [x * x for x in xs]
    assert hits["n"] == len(set(xs)) == sq.cache_size()
