from pathlib import Path

from services.period_finder import get_latest_period
from services.file_finder import find_files

from parsers.excel_reader import read_excel

from parsers.profit_parser import ProfitParser
from parsers.brand_parser import BrandParser
from parsers.debt_parser import DebtParser

from services.report_builder import build_employee_report

from generators.pdf_generator import generate_pdf


def main():

    print("Поиск последнего периода...")

    period_folder = get_latest_period()

    print(f"Найден период: {period_folder}")

    files = find_files(period_folder)
    year = int(period_folder.parent.name)
    month = int(period_folder.name)

    required = ["profit", "brand", "debt"]

    for file_type in required:

        if file_type not in files:
            raise FileNotFoundError(
                f"Не найден файл: {file_type}"
            )

    print("Чтение Excel файлов...")

    profit_df = read_excel(files["profit"])
    brand_df = read_excel(files["brand"])
    debt_df = read_excel(files["debt"])

    print("Инициализация парсеров...")

    profit_parser = ProfitParser(profit_df)
    brand_parser = BrandParser(brand_df)
    debt_parser = DebtParser(debt_df)

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
            )

            safe_name = (
                employee
                .replace("/", "_")
                .replace("\\", "_")
                .replace(":", "_")
            )

            pdf_file = (
                report_dir
                / f"{safe_name}.pdf"
            )

            generate_pdf(
                pdf_file,
                employee,
                report["profit"],
                report["brand"],
                report["debt"],
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