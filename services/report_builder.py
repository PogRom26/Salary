from models.employee_report import EmployeeReport


def build_employee_report(
    employee,
    profit_parser,
    brand_parser,
    debt_parser,
):

    report = EmployeeReport(
        employee=employee
    )

    # ==========================================
    # Доход
    # ==========================================

    income_data = profit_parser.get_income(
        employee
    )

    report.income = income_data["income"]

    report.income_bonus = income_data["bonus"]

    # ==========================================
    # KPI
    # ==========================================

    kpi_data = brand_parser.get_employee_kpi(
        employee
    )

    report.brands = kpi_data["brands"]

    report.kpi_bonus_total = (
        kpi_data["bonus_total"]
    )

    # ==========================================
    # Дебиторка
    # ==========================================

    debt_data = debt_parser.get_data(
        employee
    )

    report.overdue_total = (
        debt_data["total"]
    )

    report.debt_indicator = (
        debt_data["indicator"]
    )

    # ==========================================
    # Общий итог
    # ==========================================

    report.total_bonus = (
        report.income_bonus
        + report.kpi_bonus_total
        + report.debt_indicator
    )

    return {
        "employee": employee,

        "profit": {
            "income": report.income,
            "bonus": report.income_bonus,
        },

        "brand": {
            "brands": report.brands,
            "bonus_total": report.kpi_bonus_total,
        },

        "debt": {
            "total": report.overdue_total,
            "indicator": report.debt_indicator,
        },

        "total_bonus": report.total_bonus,
    }