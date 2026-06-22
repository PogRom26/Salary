import re
import pandas as pd


class CommParser:

    COMM_TYPES = [
        "визит к клиенту",
        "звонок",
        "отправить данные",
        "подписание документов",
    ]

    def __init__(self, df: pd.DataFrame):

        self.df = df

    def get_employee_stats(self, employee):

        surname = employee.split()[0].lower()
        name = employee.split()[1].lower()

        result = {
            "визит к клиенту": {
                "total": 0,
                "success": 0,
                "failed": 0,
            },
            "звонок": {
                "total": 0,
                "success": 0,
                "failed": 0,
            },
            "отправить данные": {
                "total": 0,
                "success": 0,
                "failed": 0,
            },
            "подписание документов": {
                "total": 0,
                "success": 0,
                "failed": 0,
            },
        }

        employee_found = False
        current_comm = None

        for _, row in self.df.iterrows():

            value = row.iloc[0]

            if pd.isna(value):
                continue

            value = str(value).strip()
            lower_value = value.lower()

            # =====================================
            # Нашли сотрудника
            # =====================================

            if (
                    lower_value.startswith(">> группа:")
                    and surname in lower_value
                    and name in lower_value
            ):
                employee_found = True
                current_comm = None

                continue

            # =====================================
            # Следующий сотрудник
            # =====================================

            if (
                    employee_found
                    and lower_value.startswith(">> группа:")
                    and surname not in lower_value
                    and name not in lower_value
                    and any(
                x in lower_value
                for x in [
                    "аверкиева",
                    "володьков",
                    "провальный",
                    "севостьянов",
                ]
            )
            ):
                break

            if not employee_found:
                continue

            # =====================================
            # Коммуникации
            # =====================================

            for comm in result.keys():

                if (
                        lower_value.startswith(">> группа:")
                        and comm in lower_value
                ):

                    current_comm = comm

                    match = re.search(
                        r"\((\d+)\)",
                        value
                    )

                    if match:
                        result[comm]["total"] = int(
                            match.group(1)
                        )

                    break

            if current_comm is None:
                continue

            # =====================================
            # Неудачно
            # =====================================

            if "завершено неудачно" in lower_value:

                match = re.search(
                    r"\((\d+)\)",
                    value
                )

                if match:
                    result[current_comm][
                        "failed"
                    ] = int(
                        match.group(1)
                    )

            # =====================================
            # Успешно
            # =====================================

            if "завершено успешно" in lower_value:

                match = re.search(
                    r"\((\d+)\)",
                    value
                )

                if match:
                    result[current_comm][
                        "success"
                    ] = int(
                        match.group(1)
                    )

        # print(employee)
        # print(result)
        return result