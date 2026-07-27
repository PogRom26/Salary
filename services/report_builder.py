from services.rounding import round_half_up


def build_employee_report(
    employee,
    profit_parser,
    brand_parser,
    debt_parser,
    comm_parser,
    cycle_parser,
    timesheet_parser,
    year,
    month,
):

    # ==========================================
    # Доход
    # ==========================================

    profit_data = profit_parser.get_income(
        employee
    )

    sales = profit_data["sales"]

    income = profit_data["income"]

    profitability = profit_data[
        "profitability"
    ]

    income_bonus = profit_data["bonus"]

    # ==========================================
    # KPI
    # ==========================================

    kpi_data = brand_parser.get_employee_kpi(
        employee
    )

    zic = kpi_data["zic"]

    other = kpi_data["other"]

    lukoil = kpi_data["lukoil"]

    zic_bonus_total = kpi_data[
        "zic_bonus_total"
    ]

    lukoil_bonus = kpi_data["lukoil_bonus"]


    other_bonus_total = kpi_data[
        "other_bonus_total"
    ]

    # ==========================================
    # Дебиторка
    # ==========================================

    debt_data = debt_parser.get_data(
        employee
    )

    overdue_total = debt_data["total"]

    responsibility = debt_data[
        "indicator"
    ]

    # ==========================================
    # Отношение ПДЗ к обороту
    # ==========================================

    if sales > 0:

        debt_ratio = (
            overdue_total
            / sales
            * 100
        )

    else:

        debt_ratio = 0

    # ==========================================
    # Цикл сделки
    # ==========================================

    cycle_data = (
        cycle_parser.get_cycle_data(
            employee,
            year,
            month,
        )
    )


    # ==========================================
    # Коммуникации за месяц
    # ==========================================

    comm_data = (
        comm_parser.get_employee_stats(
            employee
        )
    )

    # ==========================================
    # Общий итог
    # ==========================================

    additional_payments = {
        "items": [
            {"description": "", "amount": None},
            {"description": "", "amount": None},
        ],
        "total": 0.0,
    }

    total_bonus = round_half_up(
            income_bonus
            + zic_bonus_total
            + lukoil_bonus
            + other_bonus_total
            + cycle_data["bonus"]
            + additional_payments["total"]
            - responsibility
    )

    # ==========================================
    # Оклад
    # ==========================================

    timesheet_data = (
        timesheet_parser.get_data(
            employee
        )
    )

    # ==========================================
    # Результат
    # ==========================================

    return {

        "employee": employee,

        "profit": {

            "sales": sales,

            "income": income,

            "profitability": profitability,

            "bonus": income_bonus,
        },

        "brand": {

            "zic": zic,

            "lukoil": lukoil,

            "other": other,

            "zic_bonus_total":
                zic_bonus_total,

            "lukoil_bonus":
                lukoil_bonus,

            "other_bonus_total":
                other_bonus_total,

            "bonus_total":
                zic_bonus_total
                + lukoil_bonus
                + other_bonus_total,
        },

        "debt": {

            "total": overdue_total,

            "responsibility":
                responsibility,

            "ratio":
                debt_ratio,

            "threshold":
                debt_data["threshold"],

            "large_items":
                debt_data["large_items"],

            "contractor_column_found":
                debt_data["contractor_column_found"],
        },

        "communications":
            comm_data,

        "additional_payments":
            additional_payments,

        "total_bonus":
            total_bonus,

        "salary_total":
            round_half_up(
                total_bonus
                + timesheet_data["salary"]
            ),

        "cycle":
            cycle_data,

        "timesheet":
            timesheet_data,
    }
