from __future__ import annotations

from datetime import date
from typing import Optional, Tuple

"""
Набор функций-декодеров для групп кодов телеграмм CLIMAT / DEKADA.

Назначение:
- Parser получает группы кодов вида "10019", "30096036", "60054315", ...
- В parser.py первая цифра группы определяет "тип" (1..7),
  а в decode.py передаётся уже "полезная часть" (без лидирующей цифры группы)
  
- Каждая функция возвращает либо:
    * число/кортеж чисел в физических единицах
    * либо None, если код пустой/некорректный/нет данных (например '///' или '/')

Единицы измерения:
- давление: гПа
- температура: C
- осадки: мм
- солнечное сияние: часы, проценты
"""

ROUND_VAL = 2
SCALE_0_1 = 0.1


def month_start(year: int, month: int) -> date:
    """
    Возвращает дату начала месяца для месячных записей (YYYY-MM-01).
    """
    return date(year, month, 1)


def dekad_start(year: int, month: int, dekad_no: int) -> date:
    """
    Возвращает дату начала декады:
    - 1 декада: 1 число
    - 2 декада: 11 число
    - 3 декада: 21 число
    """
    day = 1 if dekad_no == 1 else 11 if dekad_no == 2 else 21
    return date(year, month, day)


def _round(x: Optional[float]) -> Optional[float]:
    """Округляет float до ROUND_VAL, None оставляет None"""
    return None if x is None else round(x, ROUND_VAL)


def _is_digits(s: str) -> bool:
    """True если строка непустая и состоит только из цифр"""
    return bool(s) and s.isdigit()


def _invalid(code: str, expected_len: int, allow_slash: bool = False) -> bool:
    """
    Проверка кода на базовую валидность

    Args:
        code: строка кода
        expected_len: ожидаемая длина кода
        allow_slash: разрешать ли '/' внутри кода (в некоторых кодах встречается)

    Returns:
        True если код невалиден (пустой/не та длина/содержит '/' при allow_slash=False)
    """
    if not code or len(code) != expected_len:
        return True
    if (not allow_slash) and ("/" in code):
        return True
    return False


def _sign(sn: str) -> int:
    """
    Знак температуры:
    - '1' -> отрицательная
    - '0' -> положительная или 0
    """
    return -1 if sn == "1" else 1


def _parse_int_or_none(s: str, missing: str = "///") -> Optional[int]:
    """
    Парсит число или возвращает None
    """
    if s == missing:
        return None
    return int(s) if s.isdigit() else None



# Monthly decoders

def decode_p_station_hpa(code: str) -> Optional[float]:
    """PPPP: давление на уровне станции (гПа)"""
    if _invalid(code, 4) or not _is_digits(code):
        return None

    value = int(code)
    res = 1000.0 + value * SCALE_0_1 if code[0] == "0" else value * SCALE_0_1
    return _round(res)


def decode_p_sea_hpa(code: str) -> Optional[float]:
    """PPPP: давление на уровне моря (гПа)"""
    if _invalid(code, 4) or not _is_digits(code):
        return None

    value = int(code)

    if value >= 1000:
        if 1000 <= value < 2300:
            return 850.0
        if 2300 <= value < 3700:
            return 700.0
        return 500.0

    res = 1000.0 + value * SCALE_0_1 if code[0] == "0" else value * SCALE_0_1
    return _round(res)


def decode_t_mean_deviation(code: str) -> Optional[Tuple[Optional[float], Optional[float]]]:
    """
    SnTTTSSS:
    - Sn: знак средней
    - TTT: средняя температура (C)
    - SSS: СКО среднесуточной (C)
    """
    if _invalid(code, 7, allow_slash=True):
        return None

    sn = code[0]
    ttt = code[1:4]
    sss = code[4:7]

    t_raw = _parse_int_or_none(ttt)
    s_raw = _parse_int_or_none(sss)

    t = None if t_raw is None else _sign(sn) * t_raw * SCALE_0_1
    s = None if s_raw is None else s_raw * SCALE_0_1

    return _round(t), _round(s)


def decode_t_daily(code: str) -> Optional[Tuple[Optional[float], Optional[float]]]:
    """
    SnTTTSnTTT: экстремальные суточные (макс/мин) (C).
    """
    if _invalid(code, 8) or not _is_digits(code):
        return None

    sn_max = code[0]
    tx = int(code[1:4])
    sn_min = code[4]
    tn = int(code[5:8])

    t_min = _sign(sn_min) * tn * SCALE_0_1
    t_max = _sign(sn_max) * tx * SCALE_0_1

    return _round(t_min), _round(t_max)


def decode_p_water(code: str) -> Optional[float]:
    """eee: парциальное давление водяного пара (гПа)."""
    if _invalid(code, 3) or not _is_digits(code):
        return None
    return _round(int(code) * SCALE_0_1)


def decode_precipitation(code: str) -> Optional[Tuple[int, Optional[int], int]]:
    """
    RRRRrdd:
    - RRRR: сумма осадков (мм)
    - r: повторяемость (цифра или '/')
    - dd: число суток (2 цифры)
    """
    if _invalid(code, 7, allow_slash=True):
        return None

    r_sum = code[:4]
    r_rep = code[4]
    r_days = code[5:7]

    if not (r_sum.isdigit() and r_days.isdigit()):
        return None

    precip_sum_mm = int(r_sum)
    precip_repeatability = None if r_rep == "/" else (int(r_rep) if r_rep.isdigit() else None)
    precip_days = int(r_days)

    return precip_sum_mm, precip_repeatability, precip_days


def decode_sunshine(code: str) -> Optional[Tuple[Optional[int], Optional[int]]]:
    """
    HHHPPP:
    - HHH: часы солнечного сияния или '///'
    - PPP: % от нормы или '///'
    """
    if _invalid(code, 6, allow_slash=True):
        return None

    hhh = code[:3]
    ppp = code[3:6]

    sunshine_hours = _parse_int_or_none(hhh)
    sunshine_pct_norm = _parse_int_or_none(ppp)

    return sunshine_hours, sunshine_pct_norm



# Decadal

def decode_t_mean_deviation_decade(code: str) -> Optional[float]:
    """SnTTT: средняя температура декады (C)."""
    if _invalid(code, 4, allow_slash=True):
        return None

    sn = code[0]
    ttt = code[1:4]
    t_raw = _parse_int_or_none(ttt)
    if t_raw is None:
        return None

    return _round(_sign(sn) * t_raw * SCALE_0_1)


def decode_precipitation_decade(code: str) -> Optional[Tuple[int, Optional[int], Optional[int]]]:
    """
    Осадки декадные
    RRRRrd:
    - RRRR: сумма осадков (мм)
    - r: повторяемость (цифра или '/')
    - d: число суток (1 цифра) или не цифра -> None
    """
    if _invalid(code, 6, allow_slash=True):
        return None

    r_sum = code[:4]
    r_rep = code[4]
    r_day = code[5]

    if not r_sum.isdigit():
        return None

    precip_sum_mm = int(r_sum)
    precip_repeatability = None if r_rep == "/" else (int(r_rep) if r_rep.isdigit() else None)
    precip_days = int(r_day) if r_day.isdigit() else None

    return precip_sum_mm, precip_repeatability, precip_days
