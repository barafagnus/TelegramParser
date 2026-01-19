from __future__ import annotations

from src.meteo_parser.compare.comparator import in_min_max_range
from src.meteo_parser.compare.models import CheckResult, RankWindow
from src.meteo_parser.core.models import MonthlyRecord, DecadalRecord


def check_monthly_record_with_windows(
        *,
        rec: MonthlyRecord,
        windows: dict[tuple[str, str], RankWindow],  # (scale="monthly", month=rec.date.month)
) -> list[CheckResult]:
    period = "M"
    results: list[CheckResult] = []

    # t_mean_c vs warmest/coldest
    for metric in ("warmest", "coldest"):
        w = windows.get((metric, period))
        if w is None:
            results.append(
                in_min_max_range(window=_empty_window(metric, "monthly", rec.date.month, period), field="t_mean_c",
                                 value=rec.t_mean_c))
        else:
            results.append(in_min_max_range(window=w, field="t_mean_c", value=rec.t_mean_c))

    # precip_sum_mm vs wettest/driest
    v_precip = None if rec.precip_sum_mm is None else float(rec.precip_sum_mm)
    for metric in ("wettest", "driest"):
        w = windows.get((metric, period))
        if w is None:
            results.append(
                in_min_max_range(window=_empty_window(metric, "monthly", rec.date.month, period), field="precip_sum_mm",
                                 value=v_precip))
        else:
            results.append(in_min_max_range(window=w, field="precip_sum_mm", value=v_precip))

    return results


def check_decadal_record_with_windows(
        *,
        rec: DecadalRecord,
        windows: dict[tuple[str, str], RankWindow],  # (scale="decadal", month=rec.date.month)
) -> list[CheckResult]:
    period = f"{rec.dekad_no}D"
    results: list[CheckResult] = []

    for metric in ("warmest", "coldest"):
        w = windows.get((metric, period))
        if w is None:
            results.append(
                in_min_max_range(window=_empty_window(metric, "decadal", rec.date.month, period), field="t_mean_c",
                                 value=rec.t_mean_c))
        else:
            results.append(in_min_max_range(window=w, field="t_mean_c", value=rec.t_mean_c))

    v_precip = None if rec.precip_sum_mm is None else float(rec.precip_sum_mm)
    for metric in ("wettest", "driest"):
        w = windows.get((metric, period))
        if w is None:
            results.append(
                in_min_max_range(window=_empty_window(metric, "decadal", rec.date.month, period), field="precip_sum_mm",
                                 value=v_precip))
        else:
            results.append(in_min_max_range(window=w, field="precip_sum_mm", value=v_precip))

    return results


def _empty_window(metric: str, scale: str, month: int, period: str) -> RankWindow:
    return RankWindow(
        dataset="",
        metric=metric,
        scale=scale,
        month=month,
        period=period,
        values=[],
        min_value=None,
        max_value=None,
    )
