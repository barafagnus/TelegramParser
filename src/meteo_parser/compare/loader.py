from __future__ import annotations

from src.meteo_parser.compare.models import RankWindow
from src.meteo_parser.db.repository import fetch_rank_values_for_month
from sqlalchemy.orm import Session


def load_month_windows(
    session: Session,
    *,
    dataset: str,
    scale: str,   # "monthly"|"decadal"
    month: int,
) -> dict[tuple[str, str], RankWindow]:
    """
    Вернёт окна для месяца:
      windows[("warmest","M")] -> RankWindow(...)
      windows[("coldest","3D")] -> RankWindow(...)
    """
    raw = fetch_rank_values_for_month(session, dataset=dataset, scale=scale, month=month)

    out: dict[tuple[str, str], RankWindow] = {}
    for (metric, period), values in raw.items():
        out[(metric, period)] = RankWindow(
            dataset=dataset,
            metric=metric,
            scale=scale,
            month=month,
            period=period,
            values=values,
            min_value=min(values) if values else None,
            max_value=max(values) if values else None,
        )
    return out
