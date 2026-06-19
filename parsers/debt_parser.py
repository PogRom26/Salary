from config import OVERDUE_DEBT_PERCENT


class DebtParser:

    def __init__(self, df):
        self.df = df

    def get_employees(self):

        return set(
            self.df.iloc[:,1]
            .dropna()
            .astype(str)
            .str.strip()
        )

    def get_data(self, employee):

        rows = self.df[
            self.df.iloc[:,1].astype(str).str.strip() == employee
        ]

        debts = []

        total = 0

        for _, row in rows.iterrows():

            contractor = str(row.iloc[0])

            overdue = row.iloc[3]

            if overdue != overdue:
                overdue = 0

            overdue = float(overdue)

            debts.append({
                "contractor": contractor,
                "overdue": overdue
            })

            total += overdue

        return {
            "debts": debts,
            "total": total,
            "indicator": total * OVERDUE_DEBT_PERCENT
        }