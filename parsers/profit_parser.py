import pandas as pd

from config import PROFIT_BONUS_PERCENT


class ProfitParser:

    def __init__(self, df: pd.DataFrame):
        self.df = df

        self.manager_col = None
        self.income_col = None

        self._detect_columns()

    # ==================================================
    # Поиск нужных колонок
    # ==================================================

    def _detect_columns(self):

        for _, row in self.df.iterrows():

            for idx, value in enumerate(row):

                if pd.isna(value):
                    continue

                value = str(value).strip().lower()

                if "менеджер" in value:
                    self.manager_col = idx

                if "доход текущий" in value:
                    self.income_col = idx

            if (
                self.manager_col is not None
                and self.income_col is not None
            ):
                return

        raise ValueError(
            "Не удалось найти колонки "
            "'Менеджер' и 'Доход текущий'"
        )

    # ==================================================
    # Проверка строки сотрудника
    # ==================================================

    def _is_employee_row(self, row):

        try:

            name = row.iloc[self.manager_col]

            income = row.iloc[self.income_col]

            if pd.isna(name):
                return False

            name = str(name).strip()

            if not name:
                return False

            words = name.split()

            # ожидаем ФИО
            if len(words) < 3:
                return False

            # доход должен быть числом
            if pd.isna(income):
                return False

            float(income)

            return True

        except Exception:
            return False

    # ==================================================
    # Получить список сотрудников
    # ==================================================

    def get_employees(self):

        employees = set()

        for _, row in self.df.iterrows():

            if self._is_employee_row(row):

                employees.add(
                    str(
                        row.iloc[self.manager_col]
                    ).strip()
                )

        return employees

    # ==================================================
    # Получить данные по сотруднику
    # ==================================================

    def get_income(self, employee):

        employee = str(employee).strip()

        for _, row in self.df.iterrows():

            if not self._is_employee_row(row):
                continue

            name = str(
                row.iloc[self.manager_col]
            ).strip()

            if name != employee:
                continue

            try:

                income = float(
                    row.iloc[self.income_col]
                )

            except Exception:

                income = 0

            bonus = (
                income
                * PROFIT_BONUS_PERCENT
            )

            return {
                "income": income,
                "bonus": bonus
            }

        return {
            "income": 0,
            "bonus": 0
        }

    # ==================================================
    # Отладочная информация
    # ==================================================

    def print_columns(self):

        print(
            f"Менеджер: {self.manager_col}"
        )

        print(
            f"Доход текущий: {self.income_col}"
        )