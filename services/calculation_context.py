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

    return {
        "year": int(period_folder.parent.name),
        "month": int(period_folder.name),
        "profit": ProfitParser(read_excel(files["profit"])),
        "brand": BrandParser(read_excel(files["brand"])),
        "debt": DebtParser(read_excel(files["debt"])),
        "communications": CommParser(read_excel(files["communications"])),
        "cycle": CycleParser(read_excel(files["cycle"])),
        "timesheet": TimesheetParser(pd.concat(
            [read_excel(path) for path in files["timesheet"]], ignore_index=True
        )),
    }
