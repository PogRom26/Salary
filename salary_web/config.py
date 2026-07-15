from pathlib import Path
import os


WEB_DIR = Path(__file__).resolve().parent
DATA_DIR = WEB_DIR / "service_data"
UPLOADS_DIR = DATA_DIR / "uploads"
GENERATED_DIR = DATA_DIR / "generated"
DB_PATH = DATA_DIR / "salary.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

MONTHS = {
    1: "январь",
    2: "февраль",
    3: "март",
    4: "апрель",
    5: "май",
    6: "июнь",
    7: "июль",
    8: "август",
    9: "сентябрь",
    10: "октябрь",
    11: "ноябрь",
    12: "декабрь",
}

REPORT_TYPES = {
    "profit": "Отчет по прибыли",
    "brand_sales": "Отчет по продажам брендов / KPI",
    "debt": "Отчет по дебиторской задолженности",
    "timesheet": "Табель рабочего времени",
    "cycle": "Отчет по циклу сделки",
    "communications": "Отчет по коммуникациям",
}

REPORT_DESCRIPTIONS = {
    "profit": {
        "description": "Отчет 1С по продажам, доходу и рентабельности.",
        "filename_hint": "profit.xls или profit.xlsx",
    },
    "brand_sales": {
        "description": "Отчет 1С по брендам, планам, факту и KPI.",
        "filename_hint": "brand_sales.xlsx",
    },
    "debt": {
        "description": "Отчет 1С по просроченной дебиторской задолженности.",
        "filename_hint": "debt.xlsx",
    },
    "timesheet": {
        "description": "Табель рабочего времени. Можно загрузить несколько файлов.",
        "filename_hint": "Табель.xlsx, Табель 2.xlsx и т.п.",
    },
    "cycle": {
        "description": "Отчет CRM по циклу сделки.",
        "filename_hint": "файл с названием, содержащим «цикл»",
    },
    "communications": {
        "description": "Отчет CRM по коммуникациям за месяц.",
        "filename_hint": "файл с названием, содержащим «коммуникации»",
    },
}

REQUIRED_REPORT_TYPES = {
    "profit",
    "brand_sales",
    "debt",
    "timesheet",
    "cycle",
    "communications",
}
