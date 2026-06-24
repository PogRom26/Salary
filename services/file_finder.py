from pathlib import Path


def find_files(folder):

    files = {}

    for file in Path(folder).iterdir():

        name = file.name.lower()

        if "profit" in name:
            files["profit"] = file

        elif "debt" in name:
            files["debt"] = file

        elif "brand" in name:
            files["brand"] = file

        elif "коммуникации" in name:
            files["communications"] = file

        elif "цикл" in name:
            files["cycle"] = file

        elif "табель" in name:
            files["timesheet"] = file

    return files