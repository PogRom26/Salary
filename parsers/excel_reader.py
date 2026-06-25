import pandas as pd


def read_excel(file_path):

    print(f"Открываю: {file_path}")

    try:

        return pd.read_excel(
            file_path,
            engine="openpyxl"
        )

    except Exception:

        try:

            return pd.read_excel(
                file_path,
                engine="xlrd"
            )

        except Exception as e:

            raise Exception(
                f"Не удалось открыть файл "
                f"{file_path}\n{e}"
            )