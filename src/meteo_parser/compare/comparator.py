from __future__ import annotations

from typing import Optional

from src.meteo_parser.compare.models import CheckResult, RankWindow


def in_min_max_range(
    *,
    window: RankWindow,
    field: str,
    value: Optional[float],
) -> CheckResult:
    """
    True только если value внутри [min, max]
    """
    if value is None:
        return CheckResult(
            dataset=window.dataset,
            metric=window.metric,
            scale=window.scale,
            month=window.month,
            period=window.period,
            field=field,
            value=None,
            ok=False,
            rng=None,
            reason="value is None",
        )

    if not window.values or window.min_value is None or window.max_value is None:
        return CheckResult(
            dataset=window.dataset,
            metric=window.metric,
            scale=window.scale,
            month=window.month,
            period=window.period,
            field=field,
            value=float(value),
            ok=False,
            rng=None,
            reason="no ranked values in DB",
        )

    lo = float(window.min_value)
    hi = float(window.max_value)
    v = float(value)

    ok = lo <= v <= hi
    return CheckResult(
        dataset=window.dataset,
        metric=window.metric,
        scale=window.scale,
        month=window.month,
        period=window.period,
        field=field,
        value=v,
        ok=ok,
        rng=(lo, hi),
        reason=f"{lo} <= {v} <= {hi}",
    )
