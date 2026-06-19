from pathlib import Path


def get_latest_period(data_dir="Data"):

    data_dir = Path(data_dir)

    years = [
        int(x.name)
        for x in data_dir.iterdir()
        if x.is_dir() and x.name.isdigit()
    ]

    latest_year = max(years)

    months_path = data_dir / str(latest_year)

    months = [
        int(x.name)
        for x in months_path.iterdir()
        if x.is_dir() and x.name.isdigit()
    ]

    latest_month = max(months)

    return months_path / str(latest_month)