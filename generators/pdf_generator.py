from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)


def money(value):
    return f"{value:,.2f} ₽".replace(",", " ")


def generate_pdf(report, output_file):

    Path(output_file).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    doc = SimpleDocTemplate(output_file)

    styles = getSampleStyleSheet()

    elements = []

    # ==========================
    # Заголовок
    # ==========================

    elements.append(
        Paragraph(
            f"<b>Расчет сотрудника</b><br/>{report.employee}",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    # ==========================
    # Доход
    # ==========================

    elements.append(
        Paragraph("1. Доход", styles["Heading2"])
    )

    income_data = [
        ["Показатель", "Значение"],
        ["Доход", money(report.income)],
        ["Бонус 5%", money(report.income_bonus)]
    ]

    income_table = Table(
        income_data,
        colWidths=[200, 200]
    )

    income_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ])
    )

    elements.append(income_table)

    elements.append(Spacer(1, 20))

    # ==========================
    # KPI брендов
    # ==========================

    elements.append(
        Paragraph(
            "2. KPI по брендам",
            styles["Heading2"]
        )
    )

    if report.brands:

        brand_data = [[
            "Бренд",
            "План",
            "Факт",
            "%",
            "Бонус"
        ]]

        for brand in report.brands:

            brand_data.append([
                str(brand["brand"]),
                f"{brand['plan']}",
                f"{brand['fact']}",
                f"{brand['percent']:.2f}",
                money(brand["bonus"])
            ])

        brand_table = Table(brand_data)

        brand_table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ])
        )

        elements.append(brand_table)

        elements.append(Spacer(1, 10))

        elements.append(
            Paragraph(
                f"<b>Итого KPI бонус:</b> "
                f"{money(report.kpi_bonus_total)}",
                styles["Normal"]
            )
        )

    else:

        elements.append(
            Paragraph(
                "Нет данных",
                styles["Normal"]
            )
        )

    elements.append(Spacer(1, 20))

    # ==========================
    # Дебиторка
    # ==========================

    elements.append(
        Paragraph(
            "3. Просроченная дебиторская задолженность",
            styles["Heading2"]
        )
    )

    if report.debts:

        debt_data = [
            ["Контрагент", "Просрочено"]
        ]

        for debt in report.debts:

            debt_data.append([
                debt["contractor"],
                money(debt["overdue"])
            ])

        debt_table = Table(
            debt_data,
            colWidths=[350, 150]
        )

        debt_table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ])
        )

        elements.append(debt_table)

        elements.append(Spacer(1, 10))

        elements.append(
            Paragraph(
                f"<b>Общая просрочка:</b> "
                f"{money(report.overdue_total)}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Показатель (1%):</b> "
                f"{money(report.debt_indicator)}",
                styles["Normal"]
            )
        )

    else:

        elements.append(
            Paragraph(
                "Нет задолженности",
                styles["Normal"]
            )
        )

    elements.append(Spacer(1, 20))

    # ==========================
    # Итог
    # ==========================

    elements.append(
        Paragraph(
            "4. Итог",
            styles["Heading2"]
        )
    )

    total_data = [
        ["Показатель", "Сумма"],
        ["Бонус по доходу", money(report.income_bonus)],
        ["KPI бонус", money(report.kpi_bonus_total)],
        ["Общий бонус", money(report.total_bonus)],
        ["Просроченная дебиторка", money(report.overdue_total)],
        ["Показатель дебиторки", money(report.debt_indicator)],
    ]

    total_table = Table(total_data)

    total_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ])
    )

    elements.append(total_table)

    doc.build(elements)