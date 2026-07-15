STATUS_LABELS = {
    "draft": "Черновик",
    "reports_loading": "Загрузка отчетов",
    "missing_reports": "Не хватает отчетов",
    "report_errors": "Ошибки в отчетах",
    "data_parsed": "Отчеты проверены",
    "ready_to_calculate": "Готово к расчету",
    "calculation_created": "Расчеты созданы",
    "closed": "Закрыт",
    "uploaded": "Загружен",
    "validated": "Проверен",
    "parsed": "Обработан",
    "error": "Ошибка",
    "calculated": "Рассчитан",
    "edited": "Изменен",
    "approved": "Подтверждено",
    "rejected": "Отклонено",
}


REPORT_TYPE_LABELS = {
    "profit": "Доход",
    "brand_sales": "Продажи по брендам",
    "debt": "Дебиторская задолженность",
    "timesheet": "Табель",
    "cycle": "Цикл сделки",
    "communications": "Коммуникации",
}


def status_label(value: str | None) -> str:
    if not value:
        return ""
    return STATUS_LABELS.get(str(value), str(value))


def report_type_label(value: str | None) -> str:
    if not value:
        return ""
    return REPORT_TYPE_LABELS.get(str(value), str(value))
