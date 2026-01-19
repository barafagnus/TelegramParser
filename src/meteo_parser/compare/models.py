from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RankWindow:
    dataset: str
    metric: str
    scale: str
    month: int
    period: str
    values: list[float]

    min_value: Optional[float]
    max_value: Optional[float]


@dataclass(frozen=True)
class CheckResult:
    dataset: str
    metric: str
    scale: str
    month: int
    period: str

    field: str
    value: Optional[float]

    ok: bool
    rng: Optional[tuple[float, float]]
    reason: str
