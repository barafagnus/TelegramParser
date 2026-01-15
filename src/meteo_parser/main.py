from __future__ import annotations

from parser import TelegramParser
from reader import TelegramReader
from config import AppConfig


def run(cfg: AppConfig):
    reader = TelegramReader(
        directory=cfg.data_dir,
        pattern=cfg.file_pattern,
        encoding=cfg.encoding,
        errors=cfg.errors,
    )
    monthly_blocks, decadal_blocks = reader.load_blocks()

    parser = TelegramParser()

    return parser.parse_blocks(
        monthly_blocks=monthly_blocks,
        decadal_blocks=decadal_blocks,
        default_decadal_year=cfg.default_decadal_year,
    )


if __name__ == "__main__":
    cfg = AppConfig()
    result = run(cfg)

    print(f"MONTHLY records: {len(result.monthly)}")
    print(f"DECADAL records: {len(result.decadal)}")

    if result.monthly:
        print("\nMonthly:")
        for rec in result.monthly:
            print(rec)

    if result.decadal:
        print("\nDecadal:")
        for rec in result.decadal:
            print(rec)