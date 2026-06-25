from pathlib import Path

from services.period_finder import get_latest_period
from services.file_finder import find_files

from parsers.excel_reader import read_excel

from parsers.profit_parser import ProfitParser
from parsers.brand_parser import BrandParser
from parsers.debt_parser import DebtParser
from parsers.comm_parser import CommParser
from parsers.cycle_parser import CycleParser
from parsers.timesheet_parser import TimesheetParser


from services.report_builder import build_employee_report

from generators.pdf_generator import generate_pdf
from generators.docx_generator import generate_docx


def main():

    print("Поиск последнего периода...")

    period_folder = get_latest_period()

    print(f"Найден период: {period_folder}")

    files = find_files(period_folder)
    year = int(period_folder.parent.name)
    month = int(period_folder.name)

    required = [
        "profit",
        "brand",
        "debt",
        "communications",
        "cycle",
        "timesheet",
    ]

    for file_type in required:

        if file_type not in files:
            raise FileNotFoundError(
                f"Не найден файл: {file_type}"
            )

    print("Чтение Excel файлов...")

    profit_df = read_excel(files["profit"])
    brand_df = read_excel(files["brand"])
    debt_df = read_excel(files["debt"])
    comm_df = read_excel(files["communications"])
    cycle_df = read_excel(files["cycle"])
    timesheet_df = read_excel(files["timesheet"])

    # print(comm_df.head(30))

    print("Инициализация парсеров...")

    profit_parser = ProfitParser(profit_df)
    brand_parser = BrandParser(brand_df)
    debt_parser = DebtParser(debt_df)
    comm_parser = CommParser(comm_df)
    cycle_parser = CycleParser(cycle_df)
    timesheet_parser = TimesheetParser(timesheet_df)

    print("Сбор списка сотрудников...")

    profit_employees = profit_parser.get_employees()
    brand_employees = brand_parser.get_employees()

    employees = sorted(
        profit_employees.intersection(
            brand_employees
        )
    )

    print(
        f"Найдено сотрудников: {len(employees)}"
    )

    report_dir = (
        Path("Report")
        / period_folder.parent.name
        / period_folder.name
    )

    report_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for employee in employees:

        try:

            print(
                f"Обработка: {employee}"
            )

            report = build_employee_report(
                employee=employee,
                profit_parser=profit_parser,
                brand_parser=brand_parser,
                debt_parser=debt_parser,
                comm_parser=comm_parser,
                cycle_parser=cycle_parser,
                timesheet_parser=timesheet_parser,
                year=year,
                month=month,
            )

            # print(report["brand"].keys())

            safe_name = (
                employee
                .replace("/", "_")
                .replace("\\", "_")
                .replace(":", "_")
            )

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

            surname = employee.split()[0]

            base_name = (
                f"{surname}_{year}_"
                f"{MONTHS[month]}"
            )

            pdf_file = (
                    report_dir
                    / f"{base_name}.pdf"
            )

            docx_file = (
                    report_dir
                    / f"{base_name}.docx"
            )

            generate_pdf(
                pdf_file,
                employee,
                report["profit"],
                report["brand"],
                report["debt"],
                report["cycle"],
                report["communications"],
                report["timesheet"],
                year,
                month,
            )

            generate_docx(
                docx_file,
                employee,
                report,
                year,
                month,
            )


            print(
                f"Создан отчет: {pdf_file.name}"
            )

        except Exception as ex:

            print(
                f"Ошибка для сотрудника "
                f"{employee}: {ex}"
            )

    print()
    print("Готово.")
    print(
        f"Отчеты сохранены в: "
        f"{report_dir}"
    )


if __name__ == "__main__":
    main()