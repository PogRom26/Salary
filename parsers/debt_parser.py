import pandas as pd

from config import OVERDUE_DEBT_PERCENT, OVERDUE_DEBT_THRESHOLD


class DebtParser:

    def __init__(self, df: pd.DataFrame):

        self.df = df

        self.manager_col = None
        self.overdue_col = None
        self.contractor_col = None
        self.contract_col = None

        self._detect_columns()

    def _detect_columns(self):

        for idx, col in enumerate(self.df.columns):

            col_name = str(col).strip().lower()

            if "менеджер" in col_name:
                self.manager_col = idx

            elif "просроч" in col_name:
                self.overdue_col = idx

            elif col_name == "контрагент" or "наименование контрагента" in col_name:
                self.contractor_col = idx

            elif "договор контрагента" in col_name:
                self.contract_col = idx

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

    def get_data(self, employee, threshold=OVERDUE_DEBT_THRESHOLD):

        total_overdue = 0.0
        large_items = []

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
                overdue = float(overdue)
            except Exception:
                continue

            total_overdue += overdue
            if overdue < threshold:
                continue

            contractor = None
            if self.contractor_col is not None:
                value = row.iloc[self.contractor_col]
                if not pd.isna(value) and str(value).strip():
                    contractor = str(value).strip()
            large_items.append({
                "contractor": contractor,
                "overdue": overdue,
                "comment": "",
            })

        indicator = (
            total_overdue
            * OVERDUE_DEBT_PERCENT
        )

        return {
            "total": total_overdue,
            "indicator": indicator,
            "threshold": threshold,
            "large_items": large_items,
            "contractor_column_found": self.contractor_col is not None,
        }

    def get_direction_data(self, threshold=100000):
        total = 0.0
        large_items = []

        for _, row in self.df.iterrows():
            if pd.isna(row.iloc[self.overdue_col]):
                continue
            try:
                overdue = float(row.iloc[self.overdue_col])
            except (TypeError, ValueError):
                continue
            total += overdue
            if overdue < threshold:
                continue

            contractor = None
            if self.contractor_col is not None:
                value = row.iloc[self.contractor_col]
                if not pd.isna(value) and str(value).strip():
                    contractor = str(value).strip()
            large_items.append({
                "contractor": contractor,
                "overdue": overdue,
                "comment": "",
            })

        return {
            "total": total,
            "large_items": large_items,
            "contractor_column_found": self.contractor_col is not None,
        }
