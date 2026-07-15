import json
from pathlib import Path

from sqlalchemy.orm import Session

from generators.chief_pdf_generator import generate_chief_pdf
from generators.pdf_generator import generate_pdf
from services.report_io import report_stem
from services.rounding import round_half_up
from salary_web.config import GENERATED_DIR
from salary_web.models import Calculation


def load_snapshot(calculation: Calculation) -> dict:
    if not calculation.snapshot_json:
        raise ValueError("У расчета еще нет JSON-снимка")
    return json.loads(calculation.snapshot_json)


def save_snapshot(calculation: Calculation, report: dict) -> None:
    _normalize_additional_payments(report)
    _recalculate_totals(report)
    calculation.snapshot_json = json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
        allow_nan=False,
    )
    calculation.status = "edited"


def save_snapshot_text(calculation: Calculation, snapshot_text: str) -> None:
    try:
        report = json.loads(snapshot_text)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON заполнен некорректно: {error}") from error
    save_snapshot(calculation, report)


def update_debt_large_item_comment(
    calculation: Calculation,
    item_index: int,
    comment: str,
) -> None:
    report = load_snapshot(calculation)
    large_items = report.setdefault("debt", {}).setdefault("large_items", [])
    if item_index < 0 or item_index >= len(large_items):
        raise ValueError("Строка ПДЗ не найдена")
    large_items[item_index]["comment"] = comment
    save_snapshot(calculation, report)


def append_additional_payment(calculation: Calculation, description: str, amount: float) -> None:
    report = load_snapshot(calculation)
    additional_payments = report.setdefault("additional_payments", {})
    items = additional_payments.setdefault("items", [])
    _append_or_fill_empty_payment(items, description, amount)
    save_snapshot(calculation, report)


def update_additional_payment(
    calculation: Calculation,
    old_description: str,
    old_amount: float,
    new_description: str,
    new_amount: float,
) -> None:
    report = load_snapshot(calculation)
    items = report.setdefault("additional_payments", {}).setdefault("items", [])
    item = _find_payment_item(items, old_description, old_amount)
    if item is None:
        _append_or_fill_empty_payment(items, new_description, new_amount)
    else:
        item["description"] = new_description
        item["amount"] = new_amount
    save_snapshot(calculation, report)


def remove_additional_payment(
    calculation: Calculation,
    description: str,
    amount: float,
) -> None:
    report = load_snapshot(calculation)
    items = report.setdefault("additional_payments", {}).setdefault("items", [])
    item = _find_payment_item(items, description, amount)
    if item is not None:
        items.remove(item)
    save_snapshot(calculation, report)


def _append_or_fill_empty_payment(items: list[dict], description: str, amount: float) -> None:
    for item in items:
        if not item.get("description") and item.get("amount") is None:
            item["description"] = description
            item["amount"] = amount
            return
    items.append({"description": description, "amount": amount})


def _find_payment_item(items: list[dict], description: str, amount: float) -> dict | None:
    for item in items:
        if _text_matches(item.get("description"), description) and _amount_matches(item.get("amount"), amount):
            return item
    return None


def _text_matches(left: object, right: object) -> bool:
    return str(left or "").strip() == str(right or "").strip()


def _amount_matches(left: object, right: object) -> bool:
    try:
        return abs(float(left or 0) - float(right or 0)) < 0.005
    except (TypeError, ValueError):
        return False


def _normalize_additional_payments(report: dict) -> None:
    additional_payments = report.setdefault("additional_payments", {})
    items = additional_payments.setdefault("items", [])
    filled_items = [
        item for item in items
        if item.get("description") or item.get("amount") is not None
    ]
    empty_rows_count = max(2 - len(filled_items), 0)
    additional_payments["items"] = filled_items + [
        {"description": "", "amount": None}
        for _ in range(empty_rows_count)
    ]


def append_adjustment(
    calculation: Calculation,
    section_code: str,
    adjustment_type: str,
    amount: float,
    comment: str,
) -> None:
    report = load_snapshot(calculation)
    adjustments = report.setdefault("manual_adjustments", [])
    adjustments.append({
        "section_code": section_code,
        "adjustment_type": adjustment_type,
        "amount": amount,
        "comment": comment,
    })

    additional_payments = report.setdefault("additional_payments", {})
    items = additional_payments.setdefault("items", [])
    description_parts = []
    if comment:
        description_parts.append(comment)
    else:
        description_parts.append("Корректировка")
    _append_or_fill_empty_payment(
        items,
        " / ".join(part for part in description_parts if part),
        amount,
    )
    save_snapshot(calculation, report)


def update_adjustment(
    calculation: Calculation,
    old_section_code: str,
    old_adjustment_type: str,
    old_amount: float,
    old_comment: str,
    new_section_code: str,
    new_adjustment_type: str,
    new_amount: float,
    new_comment: str,
) -> None:
    report = load_snapshot(calculation)
    adjustments = report.setdefault("manual_adjustments", [])
    adjustment = _find_adjustment(
        adjustments,
        old_section_code,
        old_adjustment_type,
        old_amount,
        old_comment,
    )
    if adjustment is not None:
        adjustment["section_code"] = new_section_code
        adjustment["adjustment_type"] = new_adjustment_type
        adjustment["amount"] = new_amount
        adjustment["comment"] = new_comment

    update_additional_payment(
        calculation,
        _adjustment_description(old_comment),
        old_amount,
        _adjustment_description(new_comment),
        new_amount,
    )
    if adjustment is not None:
        report = load_snapshot(calculation)
        adjustments = report.setdefault("manual_adjustments", [])
        adjustment = _find_adjustment(
            adjustments,
            old_section_code,
            old_adjustment_type,
            old_amount,
            old_comment,
        )
        if adjustment is not None:
            adjustment["section_code"] = new_section_code
            adjustment["adjustment_type"] = new_adjustment_type
            adjustment["amount"] = new_amount
            adjustment["comment"] = new_comment
        save_snapshot(calculation, report)


def remove_adjustment(
    calculation: Calculation,
    section_code: str,
    adjustment_type: str,
    amount: float,
    comment: str,
) -> None:
    report = load_snapshot(calculation)
    adjustments = report.setdefault("manual_adjustments", [])
    adjustment = _find_adjustment(
        adjustments,
        section_code,
        adjustment_type,
        amount,
        comment,
    )
    if adjustment is not None:
        adjustments.remove(adjustment)
    items = report.setdefault("additional_payments", {}).setdefault("items", [])
    payment_item = _find_payment_item(items, _adjustment_description(comment), amount)
    if payment_item is not None:
        items.remove(payment_item)
    save_snapshot(calculation, report)


def _adjustment_description(comment: str) -> str:
    return str(comment or "").strip() or "Корректировка"


def _find_adjustment(
    adjustments: list[dict],
    section_code: str,
    adjustment_type: str,
    amount: float,
    comment: str,
) -> dict | None:
    for adjustment in adjustments:
        if (
            _text_matches(adjustment.get("section_code"), section_code)
            and _text_matches(adjustment.get("adjustment_type"), adjustment_type)
            and _amount_matches(adjustment.get("amount"), amount)
            and _text_matches(adjustment.get("comment"), comment)
        ):
            return adjustment
    return None


def generate_pdf_for_calculation(db: Session, calculation: Calculation) -> Path:
    report = load_snapshot(calculation)
    period = calculation.period
    output_dir = GENERATED_DIR / str(period.year) / f"{period.month:02d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{report_stem(report['employee'], period.year, period.month)}.pdf"

    if report.get("report_type") == "chief":
        generate_chief_pdf(pdf_path, report, period.year, period.month)
    elif report.get("report_type") == "manager":
        generate_pdf(
            pdf_path,
            report["employee"],
            report["profit"],
            report["brand"],
            report["debt"],
            report["cycle"],
            report["communications"],
            report["timesheet"],
            report["additional_payments"],
            period.year,
            period.month,
        )
    else:
        raise ValueError(f"Неизвестный тип расчета: {report.get('report_type')}")

    calculation.pdf_path = str(pdf_path)
    db.flush()
    return pdf_path


def _additional_total(report: dict) -> float:
    return round_half_up(sum(
        float(item.get("amount") or 0)
        for item in report.get("additional_payments", {}).get("items", [])
    ))


def _recalculate_totals(report: dict) -> None:
    additional_payments = report.setdefault("additional_payments", {})
    additional_payments["total"] = _additional_total(report)

    if report.get("report_type") == "chief":
        _recalculate_chief_totals(report)
    else:
        _recalculate_manager_totals(report)


def _recalculate_manager_totals(report: dict) -> None:
    total_bonus = round_half_up(
        float(report["profit"]["bonus"])
        + float(report["brand"]["zic_bonus_total"])
        + float(report["brand"].get("lukoil_bonus") or 0)
        + float(report["brand"]["other_bonus_total"])
        + float(report["cycle"]["bonus"])
        + float(report["additional_payments"]["total"])
        - float(report["debt"]["responsibility"])
    )
    report["total_bonus"] = total_bonus
    report["salary_total"] = round_half_up(total_bonus + float(report["timesheet"]["salary"]))


def _recalculate_chief_totals(report: dict) -> None:
    total_bonus = round_half_up(
        float(report["profit"]["kpi"]["bonus"])
        + float(report["cycle"]["bonus"])
        + float(report["zic"]["bonus"])
        + float(report["other"]["bonus"])
        + float(report["lukoil"]["bonus"])
        + float(report["key_clients_profit"]["bonus"])
        + float(report["additional_payments"]["total"])
        - float(report["debt"]["responsibility"])
    )
    report["total_bonus"] = total_bonus
    report["salary_total"] = round_half_up(total_bonus + float(report["timesheet"]["salary"]))
