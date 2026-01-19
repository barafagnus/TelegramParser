from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.meteo_parser.core.decode import month_start, decode_p_station_hpa, decode_p_sea_hpa, decode_t_mean_deviation, \
    decode_t_daily, decode_p_water, decode_precipitation, decode_sunshine, dekad_start, decode_t_mean_deviation_decade, \
    decode_precipitation_decade
from src.meteo_parser.core.models import MonthlyRecord, DecadalRecord, MonthlyBlock, DecadalBlock


@dataclass
class ParseResult:
    monthly: List[MonthlyRecord]
    decadal: List[DecadalRecord]


class TelegramParser:
    """
    Парсер блоков CLIMAT / DEKADA
    - получает на вход блоки из TelegramReader
    - разбирает каждую строку станции, распознает коды, расшифровывает ф-ями из decode.py
    - формирует дата-классы
    """

    def parse_blocks(
            self,
            monthly_blocks: List[MonthlyBlock],
            decadal_blocks: List[DecadalBlock],
            default_decadal_year: int,
    ) -> ParseResult:
        """
        Args:
            monthly_blocks: список блоков CLIMAT (месячные данные)
            decadal_blocks: список блоков DEKADA (декадные данные)
            default_decadal_year: год по умолчанию для DEKADA, если в данных нет CLIMAT

        Returns:
            ParseResult с двумя списками записей: monthly и decadal
        """
        monthly_records: List[MonthlyRecord] = []
        for b in monthly_blocks:
            monthly_records.extend(self.parse_monthly_block(b))

        dec_year = self._choose_decadal_year(monthly_blocks, default_decadal_year)

        decadal_records: List[DecadalRecord] = []
        for b in decadal_blocks:
            decadal_records.extend(self.parse_decadal_block(b, year=dec_year))

        return ParseResult(monthly=monthly_records, decadal=decadal_records)

    def parse_monthly_block(self, block: MonthlyBlock) -> List[MonthlyRecord]:
        dt = month_start(block.year, block.month)
        records: List[MonthlyRecord] = []

        for raw_line in block.station_lines:
            parts = raw_line.split()
            if not parts:
                continue

            station_id = int(parts[0])
            groups = parts[1:]

            rec = MonthlyRecord(date=dt, station_id=station_id, raw_line=raw_line)

            for code in groups:
                if not code or code == "111":
                    continue

                lead = code[0]

                if lead == "1" and len(code) >= 5:
                    rec.p_station_hpa = decode_p_station_hpa(code[1:5])

                elif lead == "2" and len(code) >= 5:
                    rec.p_sea_hpa = decode_p_sea_hpa(code[1:5])

                elif lead == "3" and len(code) >= 8:
                    decoded = decode_t_mean_deviation(code[1:])
                    if decoded is not None:
                        rec.t_mean_c, rec.t_daily_std_c = decoded

                elif lead == "4" and len(code) == 9:
                    decoded = decode_t_daily(code[1:])
                    if decoded is not None:
                        rec.t_min_daily_c, rec.t_max_daily_c = decoded

                elif lead == "5" and len(code) == 4:
                    rec.e_vapor_hpa = decode_p_water(code[1:])

                elif lead == "6" and len(code) == 8:
                    decoded = decode_precipitation(code[1:])
                    if decoded is not None:
                        rec.precip_sum_mm, rec.precip_repeatability, rec.precip_days = decoded

                elif lead == "7" and len(code) == 7:
                    decoded = decode_sunshine(code[1:])
                    if decoded is not None:
                        rec.sunshine_hours, rec.sunshine_pct_norm = decoded

            records.append(rec)

        return records

    def parse_decadal_block(self, block: DecadalBlock, year: int) -> List[DecadalRecord]:
        dt = dekad_start(year, block.month, block.dekad_no)
        records: List[DecadalRecord] = []

        for raw_line in block.station_lines:
            parts = raw_line.split()
            if not parts:
                continue

            station_id = int(parts[0])
            groups = parts[1:]

            rec = DecadalRecord(
                date=dt,
                dekad_no=block.dekad_no,
                station_id=station_id,
                raw_line=raw_line,
            )

            for code in groups:
                if not code:
                    continue

                lead = code[0]

                if lead == "1" and len(code) == 5:
                    rec.p_station_hpa = decode_p_station_hpa(code[1:])

                elif lead == "2" and len(code) == 5:
                    rec.p_sea_hpa = decode_p_sea_hpa(code[1:])

                elif lead == "3" and len(code) == 5:
                    rec.t_mean_c = decode_t_mean_deviation_decade(code[1:])

                elif lead == "5" and len(code) == 4:
                    rec.e_vapor_hpa = decode_p_water(code[1:])

                elif lead == "6" and len(code) == 7:
                    decoded = decode_precipitation_decade(code[1:])
                    if decoded is not None:
                        rec.precip_sum_mm, rec.precip_repeatability, rec.precip_days = decoded

            records.append(rec)

        return records

    def _choose_decadal_year(self, monthly_blocks: List[MonthlyBlock], default_year: int) -> int:
        """
        Выбор года для декадных блоков

        - если есть monthly_blocks (CLIMAT), берём год из первого блока
        - иначе возвращаем default_year
        """
        return monthly_blocks[0].year if monthly_blocks else default_year
