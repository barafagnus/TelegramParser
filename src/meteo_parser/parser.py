from __future__ import annotations

import pprint
from dataclasses import dataclass
from typing import List, Optional
from decode import *

from models import MonthlyRecord, DecadalRecord

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

def parse_monthly_block(block):
    dt = month_start(block.year, block.month)
    result: List[MonthlyRecord] = []

    for raw in block.station_lines:
        parts = raw.split()
        if not parts:
            continue

        station_id = int(parts[0])
        groups = parts[1:]

        rec = MonthlyRecord(date=dt, station_id=station_id, raw_line=raw)

        for code in groups:
            if code == "111" or not code:
                continue

            lead = code[0]

            # 1 P0 P0 P0 P0
            if lead == "1" and len(code) >= 5:
                rec.p_station_hpa = decode_p_station_hpa(code[1:5])

            # 2 P P P P
            elif lead == "2" and len(code) >= 5:
                rec.p_sea_hpa = decode_p_sea_hpa(code[1:5])

            # 3 Sn T T T s1 s1 s1
            elif lead == "3" and len(code) >= 8:
                decoded = decode_t_mean_deviation(code[1:])
                if decoded is not None:
                    rec.t_mean_c, rec.t_daily_std_c = decoded

            # 4 Sn Tx Tx Tx Sn Tn Tn Tn
            elif lead == "4" and len(code) == 9:
                decoded = decode_t_daily(code[1:10])
                if decoded is not None:
                    rec.t_min_daily_c, rec.t_max_daily_c = decoded

            # 5 e e e
            elif lead == "5" and len(code) == 4:
                rec.e_vapor_hpa = decode_p_water(code[1:])

            # 6 R1 R1 R1 R1 Rd nr nr
            elif lead == "6" and len(code) == 8:
                decoded = decode_precipitation(code[1:])
                if decoded is not None:
                    rec.precip_sum_mm, rec.precip_repeatability, rec.precip_days = decoded

            # 7 S1 S1 S1 Ps Ps Ps
            elif lead == "7" and len(code) == 7:
                decoded = decode_sunshine(code[1:])
                if decoded is not None:
                    rec.sunshine_hours, rec.sunshine_pct_norm = decoded

        result.append(rec)

    return result

def parse_decadal_block(block, year: int):
    dt = dekad_start(year, block.month, block.dekad_no)
    result: List[DecadalRecord] = []

    for raw_line in block.station_lines:
        parts = raw_line.split()
        if not parts:
            continue

        station_id = int(parts[0])
        groups = parts[1:]

        rec = DecadalRecord(date=dt, dekad_no=block.dekad_no, station_id=station_id, raw_line=raw_line)

        for code in groups:
            if not code:
                continue

            lead = code[0]

            # 1PPPP (в декаде: 19966 => lead=1, полезно "9966")
            if lead == "1" and len(code) == 5:
                rec.p_station_hpa = decode_p_station_hpa(code[1:])

            # 2PPPP
            elif lead == "2" and len(code) == 5:
                rec.p_sea_hpa = decode_p_sea_hpa(code[1:])

            # 3SnTTT
            elif lead == "3" and len(code) == 5:
                rec.t_mean_c = decode_t_mean(code[1:])  # 4 символа

            # 5eee
            elif lead == "5" and len(code) == 4:
                rec.e_vapor_hpa = decode_p_water(code[1:])

            # 6RRRrdd
            elif lead == "6" and len(code) == 7:
                decoded = decode_precipitation_decade(code[1:])
                if decoded is not None:
                    rec.precip_sum_mm, rec.precip_repeatability, rec.precip_days = decoded

        result.append(rec)

    return result

mocka =  parse_monthly_block(
    MonthlyBlock(
        month=6,
        year=2025,
        station_lines=[
            '22113 111 10019 20080 30096036 401360062 5081 60054315 7200088',
            '22217 111 10045 20076 30112025 401560071 5091 60050306 7213078',
            '22235 111 19887 20076 30092033 401340051 5084 60045/09 7141058'
        ],
        header='CLIMAT 06025'
    )
)

#pprint.pprint(mocka, sort_dicts=False)


mockdecadal = parse_decadal_block(
    DecadalBlock(
        month=9,
        dekad_no=3,
        station_lines=[
            '20107 19966 20062 30014 5058 6002204',
            '22004 10004 20133 30079 5084 6004904',
            '22127 19927 20125 30064 5083 6003605',
            '22212 19972 20132 30087 5089 6003403',
            '22214 19966 20142 30077 5094 6002903',
            '22324 10094 20142 30084 5095 6001502'
        ],
        header='DEKADA 093'), 1
)
pprint.pprint(mockdecadal, sort_dicts=False)
