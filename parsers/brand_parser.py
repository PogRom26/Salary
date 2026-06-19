import pandas as pd

from config import BRAND_BONUS_BASE


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

        # ожидаем ФИО
        if len(words) < 3:
            return False

        return True

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

        brands = []

        total_bonus = 0

        current_employee = None

        for _, row in self.df.iterrows():

            col_a = row.iloc[0]

            # найден новый сотрудник
            if self._is_employee(col_a):

                current_employee = str(col_a).strip()
                continue

            if current_employee != employee:
                continue

            try:

                brand = row.iloc[3]

                if pd.isna(brand):
                    continue

                brand = str(brand).strip()

                if not brand:
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

                bonus = (
                    percent / 100
                ) * BRAND_BONUS_BASE

                brands.append(
                    {
                        "brand": brand,
                        "plan": plan,
                        "fact": fact,
                        "percent": percent,
                        "bonus": bonus,
                    }
                )

                total_bonus += bonus

            except Exception:
                continue

        return {
            "brands": brands,
            "bonus_total": total_bonus,
        }

    # ==================================================
    # Отладка
    # ==================================================

    def print_employee_count(self):

        employees = self.get_employees()

        print(
            f"Найдено сотрудников: {len(employees)}"
        )

        for employee in sorted(employees):
            print(employee)