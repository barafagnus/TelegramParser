from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class MonthlyRecord:
    date: date
    station_id: int

    p_station_hpa: Optional[float] = None
    p_sea_hpa: Optional[float] = None

    t_mean_c: Optional[float] = None
    t_daily_std_c: Optional[float] = None

    t_min_daily_c: Optional[float] = None
    t_max_daily_c: Optional[float] = None

    e_vapor_hpa: Optional[float] = None

    precip_sum_mm: Optional[int] = None
    precip_repeatability: Optional[int] = None
    precip_days: Optional[int] = None

    sunshine_hours: Optional[int] = None
    sunshine_pct_norm: Optional[int] = None

    raw_line: str = ""


@dataclass
class DecadalRecord:
    date: date
    dekad_no: int
    station_id: int

    p_station_hpa: Optional[float] = None
    p_sea_hpa: Optional[float] = None

    t_mean_c: Optional[float] = None
    e_vapor_hpa: Optional[float] = None

    precip_sum_mm: Optional[int] = None
    precip_repeatability: Optional[int] = None
    precip_days: Optional[int] = None

    raw_line: str = ""
