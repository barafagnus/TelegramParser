# scripts/test_compare_bulk_month.py
from __future__ import annotations

from collections import defaultdict

from src.meteo_parser.compare.checks import check_monthly_record_with_windows, check_decadal_record_with_windows
from src.meteo_parser.config import AppConfig
from src.meteo_parser.core.reader import TelegramReader
from src.meteo_parser.core.parser import TelegramParser
from src.meteo_parser.db.engine import make_engine, make_session_factory
from src.meteo_parser.compare.loader import load_month_windows


def main() -> None:
    cfg = AppConfig()
    dataset = getattr(cfg, "dataset", "murmansk")

    parsed = TelegramParser().parse_blocks(
        *TelegramReader(
            directory=cfg.data_dir,
            pattern=cfg.file_pattern,
            encoding=cfg.encoding,
            errors=cfg.errors,
        ).load_blocks(),
        default_decadal_year=cfg.default_decadal_year,
    )

    engine = make_engine(cfg.db_url)
    SessionFactory = make_session_factory(engine)

    monthly_by_month = defaultdict(list)
    for r in parsed.monthly:
        monthly_by_month[r.date.month].append(r)

    decadal_by_month = defaultdict(list)
    for r in parsed.decadal:
        decadal_by_month[r.date.month].append(r)

    with SessionFactory() as session:
        # MONTHLY
        for month, recs in sorted(monthly_by_month.items()):
            windows = load_month_windows(session, dataset=dataset, scale="monthly", month=month)
            for rec in recs:  # пример
                checks = check_monthly_record_with_windows(rec=rec, windows=windows)
                print(f"\nMONTHLY {rec.date} st={rec.station_id} t_mean={rec.t_mean_c} precip={rec.precip_sum_mm}")
                for c in checks:
                    print(" ", c.metric, c.field, c.ok, "value=", c.value, "range=", c.rng)

        # DECADAL
        for month, recs in sorted(decadal_by_month.items()):
            windows = load_month_windows(session, dataset=dataset, scale="decadal", month=month)
            for rec in recs:
                checks = check_decadal_record_with_windows(rec=rec, windows=windows)
                print(f"\nDECADAL {rec.date} {rec.dekad_no}D st={rec.station_id} t_mean={rec.t_mean_c} precip={rec.precip_sum_mm}")
                for c in checks:
                    print(" ", c.metric, c.field, c.ok, "value=", c.value, "range=", c.rng)


if __name__ == "__main__":
    main()
