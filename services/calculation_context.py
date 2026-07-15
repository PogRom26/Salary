import pandas as pd

from services.file_finder import find_files
from services.period_finder import get_latest_period
from parsers.excel_reader import read_excel
from parsers.profit_parser import ProfitParser
from parsers.brand_parser import BrandParser
from parsers.debt_parser import DebtParser
from parsers.comm_parser import CommParser
from parsers.cycle_parser import CycleParser
from parsers.timesheet_parser import TimesheetParser


REQUIRED_FILES = ("profit", "brand", "debt", "communications", "cycle", "timesheet")


def load_context():
    period_folder = get_latest_period()
    files = find_files(period_folder)
    missing = [name for name in REQUIRED_FILES if name not in files]
    if missing:
        raise FileNotFoundError("Не найдены файлы: " + ", ".join(missing))

    return load_context_from_files(
        year=int(period_folder.parent.name),
        month=int(period_folder.name),
        files=files,
    )


def load_context_from_files(year, month, files):
    normalized_files = dict(files)
    if "brand_sales" in normalized_files and "brand" not in normalized_files:
        normalized_files["brand"] = normalized_files["brand_sales"]

    missing = [name for name in REQUIRED_FILES if name not in normalized_files]
    if missing:
        raise FileNotFoundError("Не найдены файлы: " + ", ".join(missing))

    timesheet_files = normalized_files["timesheet"]
    if not isinstance(timesheet_files, (list, tuple)):
        timesheet_files = [timesheet_files]

    return {
        "year": int(year),
        "month": int(month),
        "profit": ProfitParser(read_excel(normalized_files["profit"])),
        "brand": BrandParser(read_excel(normalized_files["brand"])),
        "debt": DebtParser(read_excel(normalized_files["debt"])),
        "communications": CommParser(read_excel(normalized_files["communications"])),
        "cycle": CycleParser(read_excel(normalized_files["cycle"])),
        "timesheet": TimesheetParser(pd.concat(
            [read_excel(path) for path in timesheet_files], ignore_index=True
        )),
    }
