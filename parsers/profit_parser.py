from config import PROFIT_BONUS_PERCENT

import pandas as pd


class ProfitParser:

    def __init__(self, df):
        self.df = df

    def _is_employee_row(self, row):

        name = row.iloc[0]

        income = row.iloc[5]

        if pd.isna(name):
            return False

        name = str(name).strip()

        if name == "":
            return False

        words = name.split()

        # ФИО
        if len(words) < 3:
            return False

        try:
            float(income)
        except Exception:
            return False

        return True

    def get_employees(self):

        employees = set()

        for _, row in self.df.iterrows():

            if self._is_employee_row(row):

                employees.add(
                    str(row.iloc[0]).strip()
                )

        return employees

    def get_income(self, employee):

        for _, row in self.df.iterrows():

            if not self._is_employee_row(row):
                continue

            name = str(row.iloc[0]).strip()

            if name != employee:
                continue

            income = float(row.iloc[5])

            return {
                "income": income,
                "bonus": income * PROFIT_BONUS_PERCENT
            }

        return {
            "income": 0,
            "bonus": 0
        }