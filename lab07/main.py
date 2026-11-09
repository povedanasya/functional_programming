"""Демо-запуск ЛР7: відправлення з різних джерел і рейтинг (I/O лише тут)."""

from __future__ import annotations

import sys
from pathlib import Path

from core import clean_and_rank, rank_shipments, total_cost
from loaders import load_shipments, load_students

HERE = Path(__file__).parent


def main(argv: list[str]) -> None:
    """Друкує рейтинг відправлень; аргументи: [min_priority top]."""
    min_priority = int(argv[0]) if argv else 2
    top = int(argv[1]) if len(argv) > 1 else 3

    rows_json = load_shipments(HERE / "sample_data.json")
    rows_csv = load_shipments(str(HERE / "sample_data.csv"))
    with open(HERE / "sample_data.json", encoding="utf-8") as f:
        rows_file = load_shipments(f)
    print(f"json={len(rows_json)} csv={len(rows_csv)} file={len(rows_file)} rows")

    ranked = rank_shipments(rows_json + rows_csv, top=top, min_priority=min_priority)
    for s in ranked:
        print(
            f"{s.id:<8} p={s.priority} {s.weight:>6.1f} kg {s.distance:>7.1f} km "
            f"base={s.cost:>7.2f} adjusted={s.adjusted:>8.2f}"
        )
    print(f"total adjusted cost: {total_cost(ranked):.2f}")

    students = load_students(
        '[{"name": " alice ", "age": "19", "score": "8.5"}, '
        '{"name": "bob", "age": "17", "score": "9.1"}]'
    )
    print("students:", clean_and_rank(students, top=2))


if __name__ == "__main__":
    main(sys.argv[1:])
