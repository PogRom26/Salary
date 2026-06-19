from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ==================================================
# Регистрация шрифта
# ==================================================

FONT_PATH = (
    Path(__file__).parent.parent
    / "fonts"
    / "DejaVuSans.ttf"
)

pdfmetrics.registerFont(
    TTFont(
        "DejaVuSans",
        str(FONT_PATH)
    )
)


# ==================================================
# Форматирование денег
# ==================================================

def money(value):

    try:
        return f"{float(value):,.2f}".replace(",", " ")
    except Exception:
        return "0.00"


# ==================================================
# Генерация PDF
# ==================================================

def generate_pdf(
    pdf_path,
    employee,
    profit_data,
    brand_data,
    debt_data,
):

    pdf_path = Path(pdf_path)

    pdf_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    doc = SimpleDocTemplate(
        str(pdf_path),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    for style in styles.byName.values():
        style.fontName = "DejaVuSans"

    story = []

    # ==================================================
    # Заголовок
    # ==================================================

    story.append(
        Paragraph(
            "Расчёт сотрудника",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            employee,
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 10)
    )

    # ==================================================
    # Доход
    # ==================================================

    story.append(
        Paragraph(
            "Доход",
            styles["Heading2"]
        )
    )

    profit_table = Table(
        [
            ["Показатель", "Значение"],
            ["Доход", money(profit_data["income"])],
            ["Бонус 5%", money(profit_data["bonus"])],
        ],
        colWidths=[90 * mm, 50 * mm],
    )

    profit_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ]
        )
    )

    story.append(profit_table)

    story.append(
        Spacer(1, 10)
    )

    # ==================================================
    # KPI
    # ==================================================

    story.append(
        Paragraph(
            "KPI",
            styles["Heading2"]
        )
    )

    kpi_rows = [
        [
            "Бренд",
            "План",
            "Факт",
            "%",
            "Бонус",
        ]
    ]

    for item in brand_data["brands"]:

        kpi_rows.append(
            [
                item["brand"],
                money(item["plan"]),
                money(item["fact"]),
                f"{item['percent']:.2f}",
                money(item["bonus"]),
            ]
        )

    kpi_rows.append(
        [
            "",
            "",
            "",
            "ИТОГО",
            money(
                brand_data["bonus_total"]
            ),
        ]
    )

    kpi_table = Table(kpi_rows)

    kpi_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ]
        )
    )

    story.append(kpi_table)

    story.append(
        Spacer(1, 10)
    )

    # ==================================================
    # Дебиторская задолженность
    # ==================================================

    story.append(
        Paragraph(
            "Дебиторская задолженность",
            styles["Heading2"]
        )
    )

    debt_table = Table(
        [
            ["Показатель", "Значение"],
            [
                "Общая просроченная задолженность",
                money(
                    debt_data["total"]
                ),
            ],
            [
                "Показатель (1%)",
                money(
                    debt_data["indicator"]
                ),
            ],
        ],
        colWidths=[90 * mm, 50 * mm],
    )

    debt_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ]
        )
    )

    story.append(debt_table)

    story.append(
        Spacer(1, 15)
    )

    # ==================================================
    # Итог
    # ==================================================

    total_bonus = (
        profit_data["bonus"]
        + brand_data["bonus_total"]
        + debt_data["indicator"]
    )

    total_table = Table(
        [
            ["Показатель", "Сумма"],
            [
                "Бонус по прибыли",
                money(
                    profit_data["bonus"]
                ),
            ],
            [
                "Бонус KPI",
                money(
                    brand_data["bonus_total"]
                ),
            ],
            [
                "Показатель дебиторки",
                money(
                    debt_data["indicator"]
                ),
            ],
            [
                "ИТОГО",
                money(total_bonus),
            ],
        ],
        colWidths=[90 * mm, 50 * mm],
    )

    total_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
            ]
        )
    )

    story.append(
        Paragraph(
            "Итоговый расчёт",
            styles["Heading2"]
        )
    )

    story.append(total_table)

    doc.build(story)