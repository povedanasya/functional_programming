"""Доменні моделі ЛР7: ShipmentRank із повним порядком через total_ordering."""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass(frozen=True, eq=False)
class ShipmentRank:
    """Відправлення в рейтингу; порядок: пріоритет ↑, дорожче краще, потім id."""

    id: str
    weight: float
    distance: float
    priority: int
    cost: float
    adjusted: float = 0.0

    def _key(self) -> tuple[int, float, str]:
        return (self.priority, self.adjusted, self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ShipmentRank):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ShipmentRank):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:
        return hash(self._key())
