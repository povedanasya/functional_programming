"""Чисте ядро ЛР2: конвеєр перетворень над записами (варіант 14 — музичний каталог).

map/filter/reduce через генераторні вирази, композиція compose/pipe/juxt,
окрема reduce-агрегація. Жодних мутацій вхідних даних і жодного I/O.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from functools import reduce
from itertools import islice
from typing import TypedDict, TypeVar

A = TypeVar("A")
B = TypeVar("B")


# --- композиція ---


def compose(*funcs: Callable[[A], A]) -> Callable[[A], A]:
    """Композиція справа наліво: compose(f, g)(x) == f(g(x))."""

    def _composed(x: A) -> A:
        for f in reversed(funcs):
            x = f(x)
        return x

    return _composed


def pipe(x: A, *funcs: Callable[[A], A]) -> A:
    """Конвеєр зліва направо: pipe(x, f, g) == g(f(x))."""
    return reduce(lambda acc, f: f(acc), funcs, x)


def juxt(*funcs: Callable[[A], B]) -> Callable[[A], tuple[B, ...]]:
    """juxt(f, g)(x) == (f(x), g(x)) — кілька поглядів на одне значення."""
    return lambda x: tuple(f(x) for f in funcs)


# --- варіант 14: музичний каталог ---


class Track(TypedDict, total=False):
    id: int
    title: str
    genre: str
    listens: list[int]
    total_listens: float


TrackStep = Callable[[Iterable[Track]], Iterable[Track]]


class ListenStats(TypedDict):
    count: float
    listens_sum: float
    avg_listens: float


def with_total_listens() -> TrackStep:
    """map: total_listens = сума прослуховувань за періодами (новий запис)."""
    return lambda tracks: (
        {**t, "total_listens": float(sum(t.get("listens", []) or []))} for t in tracks
    )


def boost_genre(genre: str, factor: float) -> TrackStep:
    """map: підсилити прослуховування лише для вибраного жанру."""

    def _boost(tracks: Iterable[Track]) -> Iterator[Track]:
        for t in tracks:
            total = float(t.get("total_listens", 0.0))
            boosted = total * factor if t.get("genre") == genre else total
            yield {**t, "total_listens": boosted}

    return _boost


def min_listens(threshold: float) -> TrackStep:
    """filter: відкинути непопулярні треки (нижче порога прослуховувань)."""
    return lambda tracks: filter(
        lambda t: float(t.get("total_listens", 0.0)) >= threshold, tracks
    )


def normalize_titles() -> TrackStep:
    """map: назва треку у Title Case без зайвих пробілів."""
    return lambda tracks: map(
        lambda t: {**t, "title": str(t.get("title", "")).strip().title()}, tracks
    )


def sort_by_listens_desc() -> TrackStep:
    """sorted з двома ключами: прослуховування спадно, id зростом."""
    return lambda tracks: sorted(
        tracks,
        key=lambda t: (-float(t.get("total_listens", 0.0)), int(t.get("id", 0))),
    )


def take(n: int) -> TrackStep:
    """Top-N (рейтинг) через itertools.islice."""
    return lambda tracks: list(islice(tracks, n))


def reduce_listen_stats(tracks: Iterable[Track]) -> ListenStats:
    """reduce-агрегація: count, listens_sum, avg_listens."""
    count, total = reduce(
        lambda acc, t: (acc[0] + 1, acc[1] + float(t.get("total_listens", 0.0))),
        tracks,
        (0.0, 0.0),
    )
    return {
        "count": count,
        "listens_sum": total,
        "avg_listens": total / count if count else 0.0,
    }


def build_chart_pipeline(
    top_n: int = 3,
    genre: str = "rock",
    factor: float = 1.5,
    threshold: float = 0.0,
) -> Callable[[Iterable[Track]], list[Track]]:
    """Складає конвеєр варіанта 14 через compose; повертає чисту функцію."""
    steps = compose(
        take(top_n),
        sort_by_listens_desc(),
        min_listens(threshold),
        boost_genre(genre, factor),
        with_total_listens(),
        normalize_titles(),
    )
    return lambda tracks: list(steps(tracks))


# --- базовий приклад із методички: клієнти інтернет-магазину ---


class Record(TypedDict, total=False):
    id: int
    name: str
    age: int
    city: str
    purchases: list[float]
    total: float


RecordStep = Callable[[Iterable[Record]], Iterable[Record]]


class Stats(TypedDict):
    count: float
    sum_total: float
    avg_total: float


def only_adults(min_age: int = 18) -> RecordStep:
    """filter: повнолітні."""
    return lambda recs: (r for r in recs if int(r.get("age", 0)) >= min_age)


def with_total() -> RecordStep:
    """map: total = sum(purchases)."""
    return lambda recs: (
        {**r, "total": float(sum(r.get("purchases", []) or []))} for r in recs
    )


def boost_city(city: str, factor: float) -> RecordStep:
    """map: підсилити total для заданого міста."""

    def _boost(recs: Iterable[Record]) -> Iterator[Record]:
        for r in recs:
            t = float(r.get("total", 0.0))
            yield {**r, "total": t * factor if r.get("city") == city else t}

    return _boost


def normalize_names() -> RecordStep:
    """map: ім'я у Title Case."""
    return lambda recs: (
        {**r, "name": str(r.get("name", "")).strip().title()} for r in recs
    )


def sort_by_total_desc() -> RecordStep:
    """sorted: total спадно, id зростом."""
    return lambda recs: sorted(
        recs, key=lambda r: (-float(r.get("total", 0.0)), r.get("id", 0))
    )


def take_records(n: int) -> RecordStep:
    """Top-N для записів клієнтів."""
    return lambda recs: list(islice(recs, n))


def reduce_stats(recs: Iterable[Record]) -> Stats:
    """reduce-агрегація: count, sum_total, avg_total."""
    count, total = reduce(
        lambda acc, r: (acc[0] + 1, acc[1] + float(r.get("total", 0.0))),
        recs,
        (0.0, 0.0),
    )
    return {
        "count": count,
        "sum_total": total,
        "avg_total": total / count if count else 0.0,
    }


def build_pipeline(
    top_n: int = 2, city: str = "Delhi", factor: float = 1.1
) -> Callable[[Iterable[Record]], list[Record]]:
    """Конвеєр базового прикладу з методички."""
    steps = compose(
        take_records(top_n),
        sort_by_total_desc(),
        boost_city(city, factor),
        with_total(),
        only_adults(18),
        normalize_names(),
    )
    return lambda recs: list(steps(recs))
