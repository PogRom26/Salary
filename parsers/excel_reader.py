from pathlib import Path
import pandas as pd


def read_excel(file_path):

    ext = Path(file_path).suffix.lower()

    if ext == ".xlsx":
        return pd.read_excel(file_path, engine="openpyxl")

    if ext == ".xls":
        return pd.read_excel(file_path, engine="xlrd")

    raise Exception(f"Unknown format {ext}")