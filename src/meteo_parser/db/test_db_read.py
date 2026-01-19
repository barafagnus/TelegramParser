from __future__ import annotations

from src.meteo_parser.config import AppConfig
from src.meteo_parser.db.engine import make_engine, make_session_factory
from src.meteo_parser.compare.loader import load_rank_window


def main() -> None:
    cfg = AppConfig()
    engine = make_engine(cfg.db_url)
    SessionFactory = make_session_factory(engine)

    with SessionFactory() as session:
        w_month = load_rank_window(
            session,
            dataset="murmansk",
            metric="warmest",
            scale="monthly",
            month=6,
            period="M",
        )
        w_dec = load_rank_window(
            session,
            dataset="murmansk",
            metric="coldest",
            scale="decadal",
            month=9,
            period="3D",
        )

    print("MONTH:", len(w_month.values), w_month.min_value, w_month.max_value)
    print(" first5:", w_month.values[:5])
    print("DEC:", len(w_dec.values), w_dec.min_value, w_dec.max_value)
    print(" first5:", w_dec.values[:5])


if __name__ == "__main__":
    main()
