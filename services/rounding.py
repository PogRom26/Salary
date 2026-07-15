from decimal import Decimal, ROUND_HALF_UP


def round_half_up(value, places=2):
    """Excel-like arithmetic rounding, returned as float for JSON/reportlab."""
    quantum = Decimal("1").scaleb(-places)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))
