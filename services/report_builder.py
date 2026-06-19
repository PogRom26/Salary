def build_employee_report(
    employee,
    profit_parser,
    brand_parser,
    debt_parser,
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

    zic_bonus_total = kpi_data[
        "zic_bonus_total"
    ]

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
    # Общий итог
    # ==========================================

    total_bonus = (
        income_bonus
        + zic_bonus_total
        + other_bonus_total
        - responsibility
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

            "other": other,

            "zic_bonus_total":
                zic_bonus_total,

            "other_bonus_total":
                other_bonus_total,

            "bonus_total":
                zic_bonus_total
                + other_bonus_total,
        },

        "debt": {

            "total": overdue_total,

            "responsibility":
                responsibility,

            "ratio":
                debt_ratio,
        },

        "total_bonus":
            total_bonus,
    }