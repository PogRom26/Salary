from config import BRAND_BONUS_BASE

import pandas as pd


class BrandParser:

    def __init__(self, df):
        self.df = df

    def _is_employee(self, value):

        if pd.isna(value):
            return False

        value = str(value).strip()

        if value == "":
            return False

        words = value.split()

        if len(words) < 3:
            return False

        if "Параметры" in value:
            return False

        if "Отбор" in value:
            return False

        if "Сотрудник" in value:
            return False

        if "Март" in value:
            return False

        return True

    def get_employees(self):

        employees = set()

        for _, row in self.df.iterrows():

            value = row.iloc[0]

            if self._is_employee(value):
                employees.add(str(value).strip())

        return employees

    def get_employee_kpi(self, employee):

        brands = []

        total_bonus = 0

        current_employee = None

        for _, row in self.df.iterrows():

            col_a = row.iloc[0]

            if self._is_employee(col_a):

                current_employee = str(col_a).strip()
                continue

            if current_employee != employee:
                continue

            brand = row.iloc[3]

            if pd.isna(brand):
                continue

            plan = row.iloc[5]
            fact = row.iloc[7]
            percent = row.iloc[8]

            try:

                plan = float(plan)

                if pd.isna(fact):
                    fact = 0

                fact = float(fact)

                if pd.isna(percent):
                    percent = 0

                percent = float(percent)

                bonus = (
                    percent / 100
                ) * BRAND_BONUS_BASE

                brands.append(
                    {
                        "brand": str(brand),
                        "plan": plan,
                        "fact": fact,
                        "percent": percent,
                        "bonus": bonus,
                    }
                )

                total_bonus += bonus

            except Exception:
                pass

        return {
            "brands": brands,
            "bonus_total": total_bonus,
        }