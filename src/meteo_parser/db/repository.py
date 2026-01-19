# src/meteo_parser/db/repository.py
from __future__ import annotations

from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.meteo_parser.db.models import RankRow


def fetch_rank_values_for_month(
    session: Session,
    *,
    dataset: str,
    scale: str,   # "monthly" | "decadal"
    month: int,   # 1..12
    metrics: tuple[str, ...] = ("warmest", "coldest", "wettest", "driest"),
) -> dict[tuple[str, str], list[float]]:
    """
    Возвращает словарь:
      key = (metric, period)  например ("warmest","M") или ("coldest","3D")
      value = [v1..v10] отсортированные по rank

    Это ОДИН запрос в БД на весь месяц.
    """
    stmt = (
        select(RankRow.metric, RankRow.period, RankRow.rank, RankRow.value)
        .where(
            RankRow.dataset == dataset,
            RankRow.scale == scale,
            RankRow.month == month,
            RankRow.metric.in_(metrics),
        )
        .order_by(RankRow.metric.asc(), RankRow.period.asc(), RankRow.rank.asc(), RankRow.id.asc())
    )

    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    for metric, period, _rank, value in session.execute(stmt).all():
        buckets[(metric, period)].append(float(value))

    return dict(buckets)
