"""Property-based тести (Hypothesis) для ADT подій."""

from copy import deepcopy

from eval_ import eval_expr, render
from evaluator import EMPTY, count_errors, flatten, reduce_log, step, timestamp_of
from expr import Add, Expr, Mul, Num
from hypothesis import given
from hypothesis import strategies as st
from model import ErrorEvent, Event, EventGroup, FileOpened, Login, Logout

ts = st.integers(min_value=0, max_value=10_000)
user = st.sampled_from(["alice", "bob", "carol"])
leaf = st.one_of(
    st.builds(Login, user, ts),
    st.builds(Logout, user, ts),
    st.builds(FileOpened, user, st.just("/f"), ts, st.sampled_from(["read", "write"])),
    st.builds(
        ErrorEvent,
        st.just("msg"),
        st.sampled_from(["warning", "error", "critical"]),
        ts,
    ),
)
event = st.recursive(
    leaf,
    lambda inner: st.builds(EventGroup, st.lists(inner, max_size=4).map(tuple)),
    max_leaves=12,
)
log = st.lists(event, max_size=6).map(tuple)


@given(log)
def test_group_reduces_like_flat_leaves(events: tuple[Event, ...]) -> None:
    leaves = tuple(leaf for e in events for leaf in flatten(e))
    assert reduce_log(events) == reduce_log(leaves)
    assert reduce_log((EventGroup(items=events),)) == reduce_log(events)


@given(log)
def test_counts_are_consistent(events: tuple[Event, ...]) -> None:
    s = reduce_log(events)
    leaves = tuple(leaf for e in events for leaf in flatten(e))
    assert s["logins"] + s["logouts"] + s["files_opened"] + sum(
        s["errors"].values()
    ) == len(leaves)
    assert sum(s["errors"].values()) == count_errors(events)
    assert count_errors(events, min_level="critical") <= count_errors(events)
    assert s["last_timestamp"] == max(map(timestamp_of, leaves), default=0)


@given(event)
def test_step_does_not_mutate_state(e: Event) -> None:
    state = step(EMPTY, e)
    before = deepcopy(state)
    step(state, e)
    assert state == before and EMPTY["errors"] == {}


expr = st.recursive(
    st.builds(Num, st.integers(min_value=0, max_value=9)),
    lambda inner: st.one_of(st.builds(Add, inner, inner), st.builds(Mul, inner, inner)),
    max_leaves=6,
)


@given(expr)
def test_render_is_evaluable_python(e: Expr) -> None:
    try:
        value = eval_expr(e)
    except ValueError:
        return
    assert value == eval(render(e))  # noqa: S307 — рядок згенеровано нашим render
