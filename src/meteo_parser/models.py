from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional
from pathlib import Path
from typing import List

"""
- Reader возвращает MonthlyBlock/DecadalBlock
- Parser преобразует блоки в MonthlyRecord/DecadalRecord
"""


@dataclass
class NormalizedTelegram:
    source_path: Path
    raw_text: str
    lines: List[str]


@dataclass
class MonthlyBlock:
    month: int
    year: int
    station_lines: List[str]
    header: str


@dataclass
class DecadalBlock:
    month: int
    dekad_no: int
    station_lines: List[str]
    header: str


@dataclass
class MonthlyRecord:
    """
    Запись месячных данных по одной станции за один месяц

    Attributes:
        date: дата начала месяца (YYYY-MM-01)
        station_id: номер станции (5 цифр в телеграмме)

        p_station_hpa: среднее давление на уровне станции (гПа)
        p_sea_hpa: среднее давление на уровне моря (гПа)

        t_mean_c: средняя температура за месяц (C)
        t_daily_std_c: среднеквадратическое отклонение среднесуточной температуры (C)

        t_min_daily_c: средняя за месяц экстремальная минимальная суточная температура (C)
        t_max_daily_c: средняя за месяц экстремальная максимальная суточная температура (C)

        e_vapor_hpa: среднее парциальное давление водяного пара (гПа)

        precip_sum_mm: сумма осадков за месяц (мм)
        precip_repeatability: повторяемость (цифра) или None если '/' (нет рядов)
        precip_days: число суток повторяемости (дни)

        sunshine_hours: суммарная продолжительность солнечного сияния (часы)
        sunshine_pct_norm: % от нормы (проценты)

        raw_line: исходная строка станции (после нормализации)
    """
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
    """
    Запись декадных данных по одной станции за одну декаду

    Attributes:
        date: дата начала декады (YYYY-MM-01 / 11 / 21)
        dekad_no: номер декады (1..3)
        station_id: номер станции (5 цифр в телеграмме)

        p_station_hpa: среднее давление на уровне станции (гПа)
        p_sea_hpa: среднее давление на уровне моря (гПа)

        t_mean_c: средняя температура декады (C)
        e_vapor_hpa: среднее парциальное давление водяного пара (гПа)

        precip_sum_mm: сумма осадков за декаду (мм)
        precip_repeatability: повторяемость (цифра) или None если '/'
        precip_days: число суток повторяемости (в декадном формате 1 цифра)

        raw_line: исходная строка станции (после нормализации)
    """
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
