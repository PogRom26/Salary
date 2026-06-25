import pandas as pd
from config import ZIC_BONUS_BASE, OTHER_BONUS_BASE, OTHER_KPI_WEIGHTS


class BrandParser:

    def __init__(self, df: pd.DataFrame):

        self.df = df

    # ==================================================
    # Проверка строки сотрудника
    # ==================================================

    def _is_employee(self, value):

        if pd.isna(value):
            return False

        value = str(value).strip()

        if not value:
            return False

        forbidden = [
            "параметры",
            "отбор",
            "сотрудник",
            "итого",
            "январ",
            "феврал",
            "март",
            "апрел",
            "май",
            "июн",
            "июл",
            "август",
            "сентябр",
            "октябр",
            "ноябр",
            "декабр",
        ]

        lower_value = value.lower()

        for item in forbidden:
            if item in lower_value:
                return False

        words = value.split()

        return len(words) >= 3

    # ==================================================
    # Получить сотрудников
    # ==================================================

    def get_employees(self):

        employees = set()

        for _, row in self.df.iterrows():

            value = row.iloc[0]

            if self._is_employee(value):

                employees.add(
                    str(value).strip()
                )

        return employees

    # ==================================================
    # Получить KPI сотрудника
    # ==================================================

    def get_employee_kpi(self, employee):

        employee = str(employee).strip()

        zic = []
        other = []

        zic_bonus_total = 0
        other_bonus_total = 0

        lukoil = None
        lukoil_bonus = 0

        current_employee = None

        for _, row in self.df.iterrows():

            col_a = row.iloc[0]

            if self._is_employee(col_a):

                current_employee = (
                    str(col_a).strip()
                )

                continue

            if current_employee != employee:
                continue

            try:

                kpi_name = row.iloc[3]

                if pd.isna(kpi_name):
                    continue

                kpi_name = str(
                    kpi_name
                ).strip()

                if not kpi_name:
                    continue

                plan = row.iloc[5]
                fact = row.iloc[7]
                percent = row.iloc[8]

                if pd.isna(plan):
                    plan = 0

                if pd.isna(fact):
                    fact = 0

                if pd.isna(percent):
                    percent = 0

                plan = float(plan)
                fact = float(fact)
                percent = float(percent)

                # =========================
                # KPI ZIC
                # =========================

                if "zic" in kpi_name.lower():

                    bonus = (
                        percent
                        / 100
                        * ZIC_BONUS_BASE
                    )

                    item = {
                        "brand": kpi_name,
                        "plan": plan,
                        "fact": fact,
                        "percent": percent,
                        "bonus": bonus,
                    }

                    zic.append(item)

                    zic_bonus_total += bonus

                # =========================
                # Лукойл
                # =========================

                elif "лукойл" in kpi_name.lower():

                    kg = fact

                    if kg < 500:
                        rate = 0

                    elif kg < 2000:
                        rate = 5

                    elif kg < 5000:
                        rate = 8

                    else:
                        rate = 10

                    lukoil_bonus = kg * rate

                    lukoil = {
                        "kg": kg,
                        "rate": rate,
                        "bonus": lukoil_bonus,
                    }

                    continue


                # =========================
                # Остальные KPI
                # =========================

                else:

                    name = kpi_name.lower()

                    if "поляр" in name:
                        weight = 22.5

                    elif "vega" in name:
                        weight = 50.0

                    elif "gsk" in name:
                        weight = 27.5

                    else:
                        weight = 0

                    weighted_percent = (
                            percent
                            * weight
                            / 100
                    )

                    item = {
                        "brand": kpi_name,
                        "plan": plan,
                        "fact": fact,
                        "percent": percent,
                        "weight": weight,
                        "weighted_percent": weighted_percent,
                    }

                    other.append(item)

            except Exception:
                continue

        other_total_percent = sum(
            item["weighted_percent"]
            for item in other
        )

        other_ratio = (
                other_total_percent / 100
        )

        if other_ratio > 1.2:
            other_ratio = 1.2

        elif other_ratio < 0.1:
            other_ratio = 0

        other_bonus_total = (
                OTHER_BONUS_BASE
                * other_ratio
        )

        return {

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
        }

    # ==================================================
    # Отладка
    # ==================================================

    def print_employee_count(self):

        employees = self.get_employees()

        print(
            f"Найдено сотрудников: "
            f"{len(employees)}"
        )

        for employee in sorted(
            employees
        ):
            print(employee)