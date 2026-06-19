import pandas as pd

from config import OVERDUE_DEBT_PERCENT


class DebtParser:

    def __init__(self, df: pd.DataFrame):

        self.df = df

        self.manager_col = None
        self.overdue_col = None

        self._detect_columns()

    def _detect_columns(self):

        for idx, col in enumerate(self.df.columns):

            col_name = str(col).strip().lower()

            if "менеджер" in col_name:
                self.manager_col = idx

            elif "просроч" in col_name:
                self.overdue_col = idx

        if self.manager_col is None:
            raise ValueError(
                "Не найдена колонка менеджера"
            )

        if self.overdue_col is None:
            raise ValueError(
                "Не найдена колонка просрочки"
            )

    # --------------------------------------------------

    def get_employees(self):

        employees = set()

        for _, row in self.df.iterrows():

            manager = row.iloc[self.manager_col]

            if pd.isna(manager):
                continue

            manager = str(manager).strip()

            if not manager:
                continue

            employees.add(manager)

        return employees

    # --------------------------------------------------

    def get_data(self, employee):

        total_overdue = 0.0

        for _, row in self.df.iterrows():

            manager = row.iloc[self.manager_col]

            if pd.isna(manager):
                continue

            manager = str(manager).strip()

            if manager != employee:
                continue

            overdue = row.iloc[self.overdue_col]

            if pd.isna(overdue):
                continue

            try:
                total_overdue += float(overdue)
            except Exception:
                pass

        indicator = (
            total_overdue
            * OVERDUE_DEBT_PERCENT
        )

        return {
            "total": total_overdue,
            "indicator": indicator,
        }