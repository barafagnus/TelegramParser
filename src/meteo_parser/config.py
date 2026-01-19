from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DB_URL = "postgresql+psycopg2://meteo_user:meteo_password@localhost:5432/meteo"

BASE_DIR: Path = Path(__file__).resolve().parent

# ---- Файлы ----
DATA_DIR: Path = BASE_DIR / "data"
FILE_PATTERN: str = "*.txt"

# ---- Кодировка ----
FILE_ENCODING: str = "utf-8"
FILE_ERRORS: str = "strict"  # можно "replace" если встречаются битые символы

# ---- Дефолтный год декад при отсутствии у CLIMAT ----
DEFAULT_DECADAL_YEAR: int = 2025


@dataclass(frozen=True)
class AppConfig:
    data_dir: Path = DATA_DIR
    file_pattern: str = FILE_PATTERN
    encoding: str = FILE_ENCODING
    errors: str = FILE_ERRORS
    default_decadal_year: int = DEFAULT_DECADAL_YEAR
    dataset: str = "murmansk"
    ranks_repo_dir: Path = BASE_DIR / "repository" / "murmansk"
    db_url: str = DB_URL
