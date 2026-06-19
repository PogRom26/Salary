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
    year,
    month,
):
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
            f"Расчёт сотрудника b2b-направления за "
            f"{MONTHS[month]} {year} года",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            employee,
            styles["Title"]
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
            "1.Доход",
            styles["Heading2"]
        )
    )

    profit_table = Table(
        [
            ["Показатель", "Значение"],

            [
                "Сумма продаж",
                money(profit_data["sales"]),
            ],

            [
                "Доход текущий",
                money(profit_data["income"]),
            ],

            [
                "Рентабельность текущая",
                f'{profit_data["profitability"]:.2f}%',
            ],

            [
                "Бонус от дохода 5%",
                money(profit_data["bonus"]),
            ],
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
    # KPI ZIC
    # ==================================================

    story.append(
        Paragraph(
            "2.KPI ZIC",
            styles["Heading2"]
        )
    )

    zic_rows = [
        [
            "Показатель",
            "План",
            "Факт",
            "% выполнения",
            "Размер бонуса",
        ]
    ]

    for item in brand_data["zic"]:
        zic_rows.append(
            [
                item["brand"],
                money(item["plan"]),
                money(item["fact"]),
                f"{item['percent']:.2f}",
                money(item["bonus"]),
            ]
        )

    # zic_rows.append(
    #     [
    #         "",
    #         "",
    #         "",
    #         "ИТОГО",
    #         money(
    #             brand_data["zic_bonus_total"]
    #         ),
    #     ]
    # )

    zic_table = Table(zic_rows)

    zic_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ]
        )
    )

    story.append(zic_table)

    story.append(
        Spacer(1, 10)
    )

    # ==================================================
    # Другие KPI
    # ==================================================

    # ==================================================
    # Другие KPI
    # ==================================================

    story.append(
        Paragraph(
            "3.Другие KPI",
            styles["Heading2"]
        )
    )

    other_rows = [
        [
            "Показатель",
            "План",
            "Факт",
            "% выполнения",
            "Вес KPI",
            "Итог %",
        ]
    ]

    other_total_percent = 0

    for item in brand_data["other"]:
        other_total_percent += item["weighted_percent"]

        other_rows.append(
            [
                item["brand"],
                money(item["plan"]),
                money(item["fact"]),
                f"{item['percent']:.2f}%",
                f"{item['weight']:.2f}%",
                f"{item['weighted_percent']:.2f}%",
            ]
        )

    other_rows.append(
        [
            "",
            "",
            "",
            "",
            "ИТОГО",
            f"{other_total_percent:.2f}%",
        ]
    )

    other_rows.append(
        [
            "",
            "",
            "",
            "",
            "Бонус",
            money(
                brand_data["other_bonus_total"]
            ),
        ]
    )

    other_table = Table(
        other_rows,
        colWidths=[
            45 * mm,
            22 * mm,
            22 * mm,
            25 * mm,
            25 * mm,
            25 * mm,
        ]
    )

    other_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ]
        )
    )

    story.append(other_table)

    story.append(
        Spacer(1, 10)
    )

    # ==================================================
    # Дебиторская задолженность
    # ==================================================

    story.append(
        Paragraph(
            "4.Дебиторская задолженность",
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
                "Ответственность за ПДЗ (1% от суммы)",
                f"-{money(debt_data['responsibility'])}",
            ],

            [
                "Отношение ПДЗ к обороту (справочно)",
                f"{debt_data['ratio']:.2f}%",
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
            + brand_data["zic_bonus_total"]
            + brand_data["other_bonus_total"]
            - debt_data["responsibility"]
    )

    total_table = Table(
        [
            ["Показатель", "Сумма"],

            [
                "Бонус от дохода 5%",
                money(
                    profit_data["bonus"]
                ),
            ],

            [
                "Бонус KPI ZIC",
                money(
                    brand_data["zic_bonus_total"]
                ),
            ],

            [
                "Бонус за другие KPI",
                money(
                    brand_data["other_bonus_total"]
                ),
            ],

            [
                "Ответственность за ПДЗ",
                f"-{money(debt_data['responsibility'])}",
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