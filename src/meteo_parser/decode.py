from __future__ import annotations

from datetime import date
from typing import Optional, Tuple

ROUND_VAL = 2

def month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def dekad_start(year: int, month: int, dekad_no: int) -> date:
    day = 1 if dekad_no == 1 else 11 if dekad_no == 2 else 21
    return date(year, month, day)


# 1 P0 P0 P0 P0
def decode_p_station_hpa(code: str) -> Optional[float]:
    if not code or "/" in code:
        return None
    if len(code) != 4 or not code.isdigit():
        return None

    value = int(code)
    return round(1000.0 + value * 0.1, ROUND_VAL) if code[0] == "0" else round(value * 0.1, ROUND_VAL)


# 2 P P P P
def decode_p_sea_hpa(code: str) -> Optional[float]:
    if not code or "/" in code:
        return None
    if len(code) != 4 or not code.isdigit():
        return None
    value = int(code)
    if value >= 1000:
        if 1000 <= value < 2300:
            return 850
        elif 2300 <= value < 3700:
            return 700
        elif value >= 3700:
            return 500
        else:
            return None
    else:
        return round(1000 + value * 0.1, ROUND_VAL) if code[0] == "0" else round(value * 0.1, ROUND_VAL)


# 3 Sn T T T s1 s1 s1
def decode_t_mean_deviation(code: str) -> Optional[Tuple[Optional[float], Optional[float]]]:
    if len(code) != 7:
        return None

    ttt = code[:4]
    sss = code[4:7]

    temp = None if ttt == "///" else (int(ttt) if ttt.isdigit() else None)
    deviation = None if sss == "///" else (int(sss) if sss.isdigit() else None)

    sign = -1 if code[0] == "1" else 1
    if temp is not None:
        temp = sign * temp * 0.1
    if deviation is not None:
        deviation = deviation * 0.1
    return round(temp, ROUND_VAL), round(deviation, ROUND_VAL)


# 4 Sn Tx Tx Tx Sn Tn Tn Tn
def decode_t_daily(code: str) -> Optional[Tuple[Optional[float], Optional[float]]]:
    if not code or "/" in code:
        return None
    if len(code) != 8 or not code.isdigit():
        return None

    min_sign = -1 if code[4] == "1" else 1
    max_sign = -1 if code[0] == "1" else 1

    min_temp = int(code[5:8])
    max_temp = int(code[0:4])

    min_temp = min_sign * min_temp * 0.1
    max_temp = max_sign * max_temp * 0.1

    return round(min_temp, ROUND_VAL), round(max_temp, ROUND_VAL),


# 5 e e e
def decode_p_water(code: str) -> Optional[float]:
    if not code or "/" in code:
        return None
    if len(code) != 3 or not code.isdigit():
        return None

    value = int(code)
    return round(value * 0.1, ROUND_VAL)


# 6 R1 R1 R1 R1 Rd nr nr
def decode_precipitation(code: str) -> Optional[Tuple[int, Optional[int], int]]:
    if len(code) != 7:
        return None

    precip_sum_mm = int(code[:4])
    precip_repeatability = None if code[4] == "/" else (int(code[4]) if code[4].isdigit() else None)
    precip_days = int(code[5:7])

    return precip_sum_mm, precip_repeatability, precip_days


# 7 S1 S1 S1 Ps Ps Ps
def decode_sunshine(code: str) -> Optional[Tuple[Optional[int], Optional[int]]]:
    if len(code) != 6:
        return None

    sss = code[:3]
    ppp = code[3:6]

    sunshine_hours = None if sss == "///" else (int(sss) if sss.isdigit() else None)
    sunshine_pct_norm = None if ppp == "///" else (int(ppp) if ppp.isdigit() else None)

    return sunshine_hours, sunshine_pct_norm

# dekad
# 1 P0 P0 P0 P0
# 2 P P P P

# 3 Sn T T T
def decode_t_mean(code: str) -> Optional[float]:
    if len(code) != 4:
        return None

    temp = None if code[1:4] == "///" else int(code[1:4])

    sign = -1 if code[0] == "1" else 1
    if temp is not None:
        temp = sign * temp * 0.1
    return round(temp, ROUND_VAL)

# 5 e e e
# 6 R1 R1 R1 R1 Rd nr nr
def decode_precipitation_decade(code: str) -> Optional[Tuple[int, Optional[int], int]]:
    if len(code) != 6:
        return None

    precip_sum_mm = int(code[:4])
    precip_repeatability = None if code[4] == "/" else (int(code[4]) if code[4].isdigit() else None)
    precip_days = int(code[5:7])

    return precip_sum_mm, precip_repeatability, precip_days

