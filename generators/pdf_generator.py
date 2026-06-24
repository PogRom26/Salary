from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle

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
    cycle_data,
    communications,
    timesheet_data,
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

    justified_style = ParagraphStyle(
        "Justified",
        parent=styles["BodyText"],
        fontName="DejaVuSans",
        alignment=TA_JUSTIFY,
    )

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
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
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

    story.append(
        Paragraph(
            "Показатель работы по KPI ZIC. Базовый размер бонуса 40.000 руб. зависит от % выполнения. ",
            justified_style
        )
    )

    story.append(
        Spacer(1, 10)
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

    zic_table = Table(zic_rows)

    zic_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgoldenrodyellow),
            ]
        )
    )

    story.append(zic_table)

    story.append(
        Spacer(1, 10)
    )

    # ==================================================
    # Лукойл
    # ==================================================

    story.append(
        Paragraph(
            "3. Лукойл",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "Размер бонусирования при продаже "
            "от 0 до 499 кг — 0 рублей за кг., "
            "от 500 до 1999 кг — 5 рублей за кг., "
            "от 2000 до 4999 кг — 8 рублей за кг., "
            "от 5000 кг — 10 рублей за кг.",
            justified_style
        )
    )

    story.append(
        Spacer(1, 10)
    )

    if brand_data["lukoil"]:
        lukoil_table = Table(
            [
                ["Показатель", "Значение"],

                [
                    "Объём продаж, кг",
                    money(
                        brand_data["lukoil"]["kg"]
                    ),
                ],

                [
                    "Ставка, руб./кг",
                    money(
                        brand_data["lukoil"]["rate"]
                    ),
                ],

                [
                    "Бонус",
                    money(
                        brand_data["lukoil"]["bonus"]
                    ),
                ],
            ],
            colWidths=[90 * mm, 50 * mm],
        )

        lukoil_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.Color(1, 0.9, 0.9)),
                ]
            )
        )

        story.append(lukoil_table)

    story.append(
        Spacer(1, 10)
    )

    # ==================================================
    # Другие KPI
    # ==================================================

    story.append(
        Paragraph(
            "4.Другие KPI",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "Итоговый показатель «Другие KPI» определяется как сумма "
            "результатов выполнения отдельных KPI с учётом их весов в общей "
            "структуре оценки. Для расчёта бонуса применяется ограничение: "
            "максимальное учитываемое выполнение — 120%, минимальное — 10%. "
            "Базовый размер бонуса — 30 000 руб.",
            justified_style
        )
    )

    story.append(
        Spacer(1, 10)
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
            30 * mm,
            25 * mm,
            25 * mm,
        ]
    )

    other_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgreen),
            ]
        )
    )

    story.append(other_table)

    story.append(
        Spacer(1, 50)
    )

    # ==================================================
    # Дебиторская задолженность
    # ==================================================

    story.append(
        Paragraph(
            "5.Дебиторская задолженность",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "Общая сумма просроченной дебиторской задолженности определяется по состоянию на 23:59:59 последнего дня отчетного месяца.",
            justified_style
        )
    )

    story.append(
        Spacer(1, 10)
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
                ("BACKGROUND", (0, 0), (-1, 0), colors.beige),
            ]
        )
    )

    story.append(debt_table)

    story.append(
        Spacer(1, 5)
    )


    # ==================================================
    # Цикл сделки
    # ==================================================

    story.append(
        Paragraph(
            "6. Цикл сделки",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "Показатель отражает скорость прохождения сделок по воронке продаж. "
            "Для расчёта определяется средний цикл успешно завершённых сделок («Отгрузка и доставка») и средний возраст текущих активных сделок. "
            "Размер бонуса зависит от соотношения этих показателей: чем быстрее текущие сделки проходят этапы воронки относительно исторического цикла продаж, тем выше бонус.",
            justified_style
        )
    )

    story.append(
        Spacer(1, 5)
    )

    cycle_table = Table(
        [
            ["Показатель", "Значение"],

            [
                "Сделок в расчете плана",
                str(
                    cycle_data["plan_count"]
                )
            ],

            [
                "Сделок в расчете факта",
                str(
                    cycle_data["fact_count"]
                )
            ],

            [
                "Цикл сделки, план",
                f"{cycle_data['plan']:.1f} дн."
            ],

            [
                "Цикл сделки, факт",
                f"{cycle_data['fact']:.1f} дн."
            ],

            [
                "Соотношение",
                f"{cycle_data['ratio'] * 100:.2f}%"
            ],

            [
                "Размер бонуса",
                money(
                    cycle_data["bonus"]
                )
            ],

        ],
        colWidths=[90 * mm, 50 * mm],
    )

    cycle_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightyellow),
            ]
        )
    )

    story.append(cycle_table)

    story.append(
        Spacer(1, 5)
    )




    # ==================================================
    # Коммуникации за месяц
    # ==================================================

    story.append(
        Paragraph(
            "7.Коммуникации за месяц",
            styles["Heading2"]
        )
    )

    comm_rows = [
        [
            "Тип коммуникации",
            "Всего",
            "Успешно",
            "Неудачно",
        ]
    ]

    for name, data in communications.items():
        comm_rows.append(
            [
                name.capitalize(),
                str(data["total"]),
                str(data["success"]),
                str(data["failed"]),
            ]
        )

    comm_table = Table(
        comm_rows,
        colWidths=[
            70 * mm,
            25 * mm,
            25 * mm,
            25 * mm,
        ]
    )

    comm_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ]
        )
    )

    story.append(comm_table)

    story.append(
        Spacer(1, 5)
    )


    # ==================================================
    # Итог
    # ==================================================

    total_bonus = (
            profit_data["bonus"]
            + brand_data["zic_bonus_total"]
            + brand_data["lukoil_bonus"]
            + brand_data["other_bonus_total"]
            + cycle_data["bonus"]
            - debt_data["responsibility"]
    )

    salary_total = (
            total_bonus
            + timesheet_data["salary"]
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
                "Бонус Лукойл",
                money(
                    brand_data["lukoil_bonus"]
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
                "Бонус за цикл сделки",
                money(
                    cycle_data["bonus"]
                ),
            ],

            [
                "ИТОГО, премия за месяц к выплате",
                money(total_bonus),
            ],

            [
                "Отработано часов",
                f"{timesheet_data['hours']:.2f}",
            ],

            [
                "Оклад",
                money(
                    timesheet_data["salary"]
                ),
            ],

            [
                "Размер заработной платы",
                money(
                    total_bonus
                    + timesheet_data["salary"]
                ),
            ],
        ],
        colWidths=[90 * mm, 50 * mm],
    )

    total_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),

                # ИТОГО
                ("BACKGROUND", (0, -4), (-1, -4), colors.Color(1, 0.9, 0.9)),
                ("TEXTCOLOR", (0, -4), (-1, -4), colors.Color(1, 0, 0)),

                # Оклад
                # ("BACKGROUND", (0, -2), (-1, -2), colors.lightyellow),

                # Размер заработной платы
                ("BACKGROUND", (0, -1), (-1, -1),
                 colors.Color(0.85, 1, 0.85)),

                ("TEXTCOLOR", (0, -1), (-1, -1),
                 colors.darkgreen),

                # ("FONTSIZE", (0, -1), (-1, -1), 12),
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