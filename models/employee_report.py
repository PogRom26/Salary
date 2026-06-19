from dataclasses import dataclass, field


@dataclass
class BrandKPI:
    brand: str
    plan: float
    fact: float
    percent: float
    bonus: float


@dataclass
class DebtItem:
    contractor: str
    overdue: float


@dataclass
class EmployeeReport:

    employee: str

    income: float = 0
    income_bonus: float = 0

    brands: list = field(default_factory=list)

    kpi_bonus_total: float = 0

    debts: list = field(default_factory=list)

    overdue_total: float = 0

    debt_indicator: float = 0

    total_bonus: float = 0