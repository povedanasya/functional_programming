"""Оболонка I/O та CLI для ЛР2: читання JSON, аргументи, друк (ядро — core.py)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from core import (
    ListenStats,
    Track,
    build_chart_pipeline,
    reduce_listen_stats,
)

SAMPLE: list[Track] = [
    {"id": 1, "title": "bohemian rhapsody", "genre": "rock", "listens": [500, 300]},
    {"id": 2, "title": "SHAPE OF YOU", "genre": "pop", "listens": [1500]},
    {"id": 3, "title": "nothing else matters", "genre": "rock", "listens": [100, 60]},
    {"id": 4, "title": "blinding lights", "genre": "pop", "listens": [1200]},
    {"id": 5, "title": "take five", "genre": "jazz", "listens": [700, 500]},
]


def load_tracks(path: Path) -> list[Track]:
    """IO-адаптер: читає треки з JSON-файлу."""
    return list(json.loads(path.read_text(encoding="utf-8")))


def render(top: list[Track], stats: ListenStats) -> str:
    """Перетворює чистий результат на текст (без друку)."""
    lines = [
        f"{t['id']:>3}  {t['title']:<22} {t['genre']:<5} {t['total_listens']:>9.1f}"
        for t in top
    ]
    return "\n".join(
        [
            *lines,
            f"count={stats['count']:.0f} listens_sum={stats['listens_sum']:.1f} "
            f"avg_listens={stats['avg_listens']:.1f}",
        ]
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Розбір аргументів CLI."""
    parser = argparse.ArgumentParser(description="Рейтинг треків за прослуховуваннями")
    parser.add_argument("--data", type=Path, help="JSON зі списком треків")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--boost-genre", default="rock")
    parser.add_argument("--factor", type=float, default=1.5)
    parser.add_argument("--min-listens", type=float, default=0.0)
    return parser.parse_args(argv)


def main(argv: list[str]) -> None:
    """Точка входу: читання → чистий конвеєр → друк."""
    args = parse_args(argv)
    tracks = load_tracks(args.data) if args.data else SAMPLE
    pipeline = build_chart_pipeline(
        args.top, args.boost_genre, args.factor, args.min_listens
    )
    top = pipeline(tracks)
    print(render(top, reduce_listen_stats(top)))


if __name__ == "__main__":
    main(sys.argv[1:])
