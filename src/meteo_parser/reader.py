from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from models import NormalizedTelegram, MonthlyBlock, DecadalBlock



class TelegramReader:
    """
    Подготовка данных телеграмм к парсингу.
    - читает все файлы из директории
    - нормализует текст в единый формат
    - разделяет нормализованные строки на блоки:
        - MonthlyBlock: начинается с 'CLIMAT MMyyy'
        - DedcadalBlock: начинается с 'DEKADA MMd'

    - load_blocks(): вернуть все monthly/decadal блоки из всех файлов
    - load_telegrams(): вернуть все телеграммы в нормализованном виде
    """

    def __init__(
        self,
        directory: Path,
        pattern: str = "*.txt",
        encoding: str = "utf-8",
        errors: str = "strict",
        replacements: Optional[Dict[str, str]] = None,
    ) -> None:
        self.directory = directory
        self.pattern = pattern
        self.encoding = encoding
        self.errors = errors
        self.replacements = replacements or {
            "КЛИМАТ": "CLIMAT",
            "ДЕКАДА": "DEKADA",
            "ЗЦЗЦ": "ZCZC",
            "ЦСРС": "CSRS",
        }

        self._validate_directory()


    def load_blocks(self) -> Tuple[List[MonthlyBlock], List[DecadalBlock]]:
        """
        Читает все телеграммы из директории, нормализует их и возвращает список блоков
        MonthlyBlock, DecadalBlock по всем файлам в директории
        :return: (monthly_blocks, decadal_blocks)
            monthly_blocks: список всех CLIMAT-блоков (месячные данные)
            decadal_blocks: список всех DEKADA-блоков (декадные данные)
        """
        monthly_all: List[MonthlyBlock] = []
        decadal_all: List[DecadalBlock] = []

        for tel in self._read_and_normalize():
            m, d = self._split_blocks(tel.lines)
            monthly_all.extend(m)
            decadal_all.extend(d)

        return monthly_all, decadal_all

    def load_telegrams(self) -> List[NormalizedTelegram]:
        """
        Возвращает телеграммы в нормализованном виде без разделения на блоки
        :return: NormalizedTelegram
        """
        return list(self._read_and_normalize())


    def _read_and_normalize(self) -> Iterable[NormalizedTelegram]:
        """Читает файлы -> нормализует -> returns: yield NormalizedTelegram"""
        for path in self._iter_files():
            raw = self._read_text(path)
            lines = self._normalize_text(raw)
            yield NormalizedTelegram(source_path=path, raw_text=raw, lines=lines)

    def _validate_directory(self) -> None:
        """Проверяет, что directory существует и является папкой"""
        if not self.directory.exists():
            raise FileNotFoundError(self.directory)
        if not self.directory.is_dir():
            raise NotADirectoryError(self.directory)

    def _iter_files(self) -> Iterable[Path]:
        """Итерирует файлы в directory"""
        yield from sorted(self.directory.glob(self.pattern))

    def _read_text(self, path: Path) -> str:
        """Читает файл целиком в строку с заданной кодировкой"""
        return path.read_text(encoding=self.encoding, errors=self.errors)

    def _normalize_text(self, text: str) -> List[str]:
        """
        Нормализация текста в список строк для последующего парсинга
        - переносы строк приводятся к '\\n'
        - пустые строки удаляются
        - повторные пробелы схлопываются
        - завершающий '=' удаляется
        - строка приводится в UPPERCASE
        - заменяем ключевые слова из replacements в единый формат 'КЛИМАТ' в 'CLIMAT' и тд
        """
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        out: List[str] = []
        for raw in text.split("\n"):
            line = raw.strip()
            if not line:
                continue

            line = " ".join(line.split())
            if line.endswith("="):
                line = line[:-1].rstrip()

            line = line.upper()
            for src, dst in self.replacements.items():
                line = line.replace(src, dst)

            out.append(line)

        return out

    def _split_blocks(self, lines: List[str]) -> Tuple[List[MonthlyBlock], List[DecadalBlock]]:
        """
        Делит нормализованные строки на блоки CLIMAT и DEKADA
        - находим заголовки 'CLIMAT...' и 'DEKADA...'
        - открываем сегмент до следующего заголовка
        - внутри сегмента берем только строки станции (первая группа 5 цифр)
        :param lines:
        :return:
        """
        headers: List[Tuple[int, str]] = []

        for i, line in enumerate(lines):
            if self._parse_climat_header(line) is not None:
                headers.append((i, "CLIMAT"))
            elif self._parse_decade_header(line) is not None:
                headers.append((i, "DEKADA"))

        monthly: List[MonthlyBlock] = []
        decadal: List[DecadalBlock] = []

        for index, (start, kind) in enumerate(headers):
            end = headers[index + 1][0] if index + 1 < len(headers) else len(lines)

            header_line = lines[start]
            segment = lines[start + 1 : end]
            station_lines = [ln for ln in segment if self._is_station_line(ln)]

            if kind == "CLIMAT":
                parsed = self._parse_climat_header(header_line)
                if parsed is None:
                    continue
                mm, yy = parsed
                monthly.append(MonthlyBlock(mm, yy, station_lines, header_line))
            else:
                parsed = self._parse_decade_header(header_line)
                if parsed is None:
                    continue
                mm, dek = parsed
                decadal.append(DecadalBlock(mm, dek, station_lines, header_line))

        return monthly, decadal


    def _parse_climat_header(self, line: str) -> Optional[Tuple[int, int]]:
        """
        Парсит заголовки месячного блока
        Формат: CLIMAT MMyyy | Climat 06025 -> (6, 2025)
        :return: (month, year) или None, если строка не CLIMAT
        """
        parts = line.split()
        if len(parts) != 2 or parts[0] != "CLIMAT":
            return None
        code = parts[1]
        if len(code) != 5 or not code.isdigit():
            return None
        return int(code[:2]), 2000 + int(code[2:])

    def _parse_decade_header(self, line: str) -> Optional[Tuple[int, int]]:
        """
        Парсит заголовок декадного блока
        Формат: DEKADA MMd | DEKADA 093 -> (9, 3)
        :return: (month, dekad_no) или None
        """
        parts = line.split()
        if len(parts) != 2 or parts[0] != "DEKADA":
            return None
        code = parts[1]
        if len(code) != 3 or not code.isdigit():
            return None
        mm = int(code[:2])
        dek = int(code[2])
        if dek not in (1, 2, 3):
            return None
        return mm, dek

    def _is_station_line(self, line: str) -> bool:
        """
        Является ли строка строкой станции (первая группа до пробила состоит из 5 цифр)
        """
        head = line.split()[0] if line.split() else ""
        return len(head) == 5 and head.isdigit()
