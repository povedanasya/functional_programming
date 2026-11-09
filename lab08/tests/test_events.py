from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest
from evaluator import (
    EMPTY,
    count_errors,
    error_level,
    flatten,
    kind,
    level_rank,
    reduce_log,
    step,
    timestamp_of,
    worst_level,
)
from model import (
    ErrorEvent,
    Event,
    EventGroup,
    FileOpened,
    Login,
    Logout,
    Timestamped,
)
from pretty import describe

LOGIN = Login("alice", 100)
OPEN = FileOpened("alice", "/etc/config.yml", 105)
WRITE = FileOpened("alice", "/var/log/app.log", 106, mode="write")
WARN = ErrorEvent("disk quota exceeded", "warning", 107)
ERR = ErrorEvent("write failed", "error", 108)
CRIT = ErrorEvent("database unreachable", "critical", 115)
LOGOUT = Logout("alice", 120)
GROUP = EventGroup(
    label="request-7",
    items=(OPEN, WRITE, EventGroup(label="retry", items=(WARN, ERR))),
)
LOG: tuple[Event, ...] = (LOGIN, GROUP, Login("bob", 110), CRIT, LOGOUT)


def test_step_each_kind_returns_new_state() -> None:
    s1 = step(EMPTY, LOGIN)
    assert s1["logins"] == 1 and s1["active_users"] == frozenset({"alice"})
    assert s1["last_timestamp"] == 100
    s2 = step(s1, OPEN)
    assert s2["files_opened"] == 1 and s2["last_timestamp"] == 105
    s3 = step(s2, ERR)
    assert s3["errors"] == {"error": 1}
    s4 = step(s3, LOGOUT)
    assert s4["logouts"] == 1 and s4["active_users"] == frozenset()
    assert EMPTY == {
        "logins": 0,
        "logouts": 0,
        "files_opened": 0,
        "errors": {},
        "active_users": frozenset(),
        "last_timestamp": 0,
    }


def test_reduce_log_full_statistics() -> None:
    before = deepcopy(LOG)
    stats = reduce_log(LOG)
    assert stats == {
        "logins": 2,
        "logouts": 1,
        "files_opened": 2,
        "errors": {"warning": 1, "error": 1, "critical": 1},
        "active_users": frozenset({"bob"}),
        "last_timestamp": 120,
    }
    assert LOG == before
    assert reduce_log(()) == EMPTY
    assert reduce_log(()) is EMPTY


def test_group_is_reduced_recursively() -> None:
    assert step(EMPTY, GROUP) == reduce_log((OPEN, WRITE, WARN, ERR))
    assert step(EMPTY, EventGroup(items=())) == EMPTY


def test_flatten_kind_and_timestamp() -> None:
    assert flatten(GROUP) == (OPEN, WRITE, WARN, ERR)
    assert flatten(CRIT) == (CRIT,)
    assert [kind(e) for e in LOG] == ["login", "group", "login", "error", "logout"]
    assert kind(OPEN) == "file"
    assert timestamp_of(GROUP) == 108 and timestamp_of(EventGroup(items=())) == 0
    assert timestamp_of(LOGOUT) == 120


def test_levels_and_error_counts() -> None:
    assert [level_rank(lvl) for lvl in ("warning", "error", "critical")] == [1, 2, 3]
    assert count_errors(LOG) == 3
    assert count_errors(LOG, min_level="error") == 2
    assert count_errors(LOG, min_level="critical") == 1
    assert count_errors((LOGIN, LOGOUT)) == 0
    assert worst_level(LOG) == "critical"
    assert worst_level((GROUP,)) == "error"
    assert worst_level((LOGIN,)) is None
    assert error_level(ERR) == "error" and error_level(LOGIN) is None


def test_negative_timestamp_rejected() -> None:
    with pytest.raises(ValueError):
        timestamp_of(Login("x", -1))
    with pytest.raises(ValueError):
        reduce_log((EventGroup(items=(OPEN, ErrorEvent("boom", "error", -5))),))


def test_nodes_are_immutable_and_hashable() -> None:
    with pytest.raises(FrozenInstanceError):
        LOGIN.user = "mallory"  # type: ignore[misc]
    assert LOGIN == Login("alice", 100)
    assert len({LOGIN, Login("alice", 100), LOGOUT}) == 2
    assert hash(GROUP) == hash(deepcopy(GROUP))


def test_describe_nested() -> None:
    assert describe(GROUP).splitlines() == [
        "group request-7 [3]",
        "  [105] alice opens /etc/config.yml",
        "  [106] alice writes /var/log/app.log",
        "  group retry [2]",
        "    [107] warning: disk quota exceeded",
        "    [108] error: write failed",
    ]
    assert describe(LOGIN) == "[100] login alice"
    assert describe(LOGOUT) == "[120] logout alice"
    assert describe(CRIT) == "[115] !!! CRITICAL: database unreachable"
    assert describe(EventGroup(items=())) == "group (unnamed) [0]"


def test_timestamped_protocol() -> None:
    def when(e: Timestamped) -> int:
        return e.timestamp

    assert [when(e) for e in (LOGIN, OPEN, ERR, LOGOUT)] == [100, 105, 108, 120]
    e: Event = CRIT
    assert isinstance(e, ErrorEvent) and e.level == "critical"
