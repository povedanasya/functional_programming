"""Демонстрація pure-оновлень незмінного сенсора (лише друк, логіка в core/model)."""

from __future__ import annotations

from core import add_label, add_reading, index_by_sensor, stats, with_config
from model import Reading, make_sensor


def main() -> None:
    """Створює сенсор, виконує три pure-оновлення і показує, що оригінал не змінився."""
    s0 = make_sensor(
        1, "temperature", (Reading(0, 21.5),), frozenset({"room"}), min=18.0, max=25.0
    )
    s1 = add_reading(s0, 60, 22.5)
    s2 = add_reading(s1, 120, 27.0)
    s3 = with_config(add_label(s2, "checked"), max=30.0)

    for name, s in [("s0", s0), ("s1", s1), ("s2", s2), ("s3", s3)]:
        st = stats(s)
        print(
            f"{name}: readings={len(s.readings)} labels={sorted(s.labels)} "
            f"config={dict(s.config)} last={s.last_value()} mean={st.mean:.2f}"
        )
    print(
        "s0 is s3:",
        s0 is s3,
        "| s0 unchanged:",
        s0.readings == (Reading(0, 21.5),) and s0.labels == frozenset({"room"}),
    )
    stats(s3)
    print("cache:", stats.cache_info())
    index = index_by_sensor((s0, s2))
    print("as dict keys:", len(index), "sensors ->", [v.n for v in index.values()])
    try:
        s0.config["max"] = 99.0  # type: ignore[index]
    except TypeError as e:
        print("config read-only:", e)


if __name__ == "__main__":
    main()
