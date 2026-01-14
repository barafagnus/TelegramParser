import parser
import pprint
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

PATTERN = "*.txt"
DIR: Path = Path("data")


@dataclass
class NormalizedTelegram:
    """Дата-класс нормализованного текста телеграммы"""
    source_path: Path
    raw_text: str
    lines: List[str]


def iter_telegram_files(directory: Path, pattern: str = PATTERN) -> Iterable[Path]:
    if not directory.exists():
        raise FileNotFoundError(directory)
    if not directory.is_dir():
        raise NotADirectoryError(directory)
    yield from sorted(directory.glob(pattern))


def read_file_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="cp1251")
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8", errors="replace")


def normalize_file_text(text: str) -> List[str]:
    """
    Приведение телеграммы к единому виду:
    - унифицирует переносы строк
    - убирает лишние пробелы, пустые строки и '='
    - приводит ключевые слова к латинским CLIMAT, DEKADA, ZCZC
    """
    out_lines: List[str] = []
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    replacements = {
        "КЛИМАТ": "CLIMAT",
        "ДЕКАДА": "DEKADA",
        "ЗЦЗЦ": "ZCZC",
        "ЦСРС": "CSRS",
    }

    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue

        line = " ".join(line.split())

        if line.endswith("="):
            line = line[:-1].rstrip()

        upper = line.upper()
        for src, dst in replacements.items():
            upper = upper.replace(src, dst)

        out_lines.append(upper)

    return out_lines


def read_telegrams_from_dir(directory: Path, pattern: str = PATTERN) -> List[NormalizedTelegram]:
    telegrams: List[NormalizedTelegram] = []
    for path in iter_telegram_files(directory, pattern):
        raw = read_file_text(path)
        lines = normalize_file_text(raw)
        telegrams.append(NormalizedTelegram(source_path=path, raw_text=raw, lines=lines))
    return telegrams

def _parse_climat_header(line: str) -> Optional[Tuple[int, int]]:
    # CLIMAT 06025 -> (6, 2025)
    parts = line.split()
    if len(parts) != 2 or parts[0] != "CLIMAT":
        return None

    code = parts[1]
    if len(code) != 5 or not code.isdigit():
        return None

    month = int(code[:2])
    year = 2000 + int(code[2:])
    return month, year

def _parse_decade_header(line: str) -> Optional[Tuple[int, int]]:
    # DEKADA 093 -> (9, 3)
    parts = line.split()
    if len(parts) != 2 or parts[0] != "DEKADA":
        return None

    code = parts[1]
    if len(code) != 3 or not code.isdigit():
        return None

    month = int(code[:2])
    decade = int(code[2])
    if decade not in (1, 2, 3):
        return None

    return month, decade

def _is_station_line(line: str) -> bool:
    head = line.split()[0] if line.split() else ""
    return len(head) == 5 and head.isdigit()


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

def split_blocks(lines: List[str]):
    """CLIMAT DEKADA"""
    headers = []

    # [(номер строки, тип телеграммы)..]
    # [(2, 'CLIMAT'), (9, 'CLIMAT'), (21, 'DEKADA'), (31, 'DEKADA')]
    for i, line in enumerate(lines):
        if _parse_climat_header(line) is not None:
            headers.append((i, "CLIMAT"))
        elif _parse_decade_header(line) is not None:
            headers.append((i, "DEKADA"))

    monthly: List[MonthlyBlock] = []
    decadal: List[DecadalBlock] = []

    for index,(start, kind) in enumerate(headers):
        end = headers[index + 1][0] if index + 1 < len(headers) else len(lines)

        header_line = lines[start]
        segment = lines[start + 1 : end]
        station_lines = [ln for ln in segment if _is_station_line(ln)]

        #print(header_line, segment, station_lines)

        if kind == "CLIMAT":
            mm, yy = _parse_climat_header(header_line)
            monthly.append(
                MonthlyBlock(
                    month = mm,
                    year = yy,
                    station_lines = station_lines,
                    header = header_line,
                )
            )
        else:
            mm, dek = _parse_decade_header(header_line)
            decadal.append(
                DecadalBlock(
                    month = mm,
                    dekad_no=dek,
                    station_lines = station_lines,
                    header = header_line,
                )
            )

    return monthly, decadal

for t in read_telegrams_from_dir(DIR, PATTERN):
    for i in split_blocks(t.lines):
        print(i)
