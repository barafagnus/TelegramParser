from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Numeric, SmallInteger


class Base(DeclarativeBase):
    pass


class RankRow(Base):
    __tablename__ = "rank_rows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    dataset: Mapped[str] = mapped_column(String, nullable=False)
    metric: Mapped[str] = mapped_column(String, nullable=False)   # warmest/coldest/wettest/driest
    scale: Mapped[str] = mapped_column(String, nullable=False)    # decadal/monthly
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1..12
    period: Mapped[str] = mapped_column(String, nullable=False)   # 1D/2D/3D/M
    rank: Mapped[int] = mapped_column(SmallInteger, nullable=False)   # 1..10

    value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
