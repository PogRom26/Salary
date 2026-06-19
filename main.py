import os
import pandas as pd
from fpdf import FPDF


# Путь к данным
DATA_DIR = "data"

# Месяцы для отображения в PDF
MONTH_NAMES = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}


def read_employees():
    try:
        from setting import employees
        return employees
    except ImportError:
        print("Файл setting.py не найден.")
        return []
    except AttributeError:
        print("В файле setting.py отсутствует переменная 'employees'.")
        return []


def find_report_path(year, month, report_type):
    base = os.path.join(DATA_DIR, str(year), str(month))
    files = {
        "profit": os.path.join(base, "profit.xls"),
        "kpi": os.path.join(base, "brand_sales.xls"),
        "debt": os.path.join(base, "debt.xls")
    }
    return files[report_type]


def get_profit_bonus(employee, year, month):
    path = find_report_path(year, month, "profit")
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return 0, 0
    encodings = ['cp1251', 'utf-8', 'latin1']
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, sep='\t', encoding=enc, on_bad_lines='skip')
            print(f"✅ Успешно прочитан profit.xls с кодировкой: {enc}")
            break
        except Exception:
            try:
                df = pd.read_csv(path, sep=';', encoding=enc, on_bad_lines='skip')
                print(f"✅ Успешно прочитан profit.xls с разделителем ';' и кодировкой: {enc}")
                break
            except:
                continue
    if df is None:
        print(f"❌ Не удалось прочитать файл profit.xls ни с одной кодировкой.")
        return 0, 0
    df.columns = [chr(65 + i) for i in range(len(df.columns))]
    row = df[df['A'].str.contains(employee, na=False, case=False)]
    if row.empty:
        return 0, 0
    income = row.iloc[0]['F']
    bonus = income * 0.05
    return round(income, 2), round(bonus, 2)


def get_kpi_bonuses(employee, year, month):
    path = find_report_path(year, month, "kpi")
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return [], 0
    encodings = ['cp1251', 'utf-8', 'latin1']
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, sep='\t', encoding=enc, on_bad_lines='skip')
            print(f"✅ Успешно прочитан brand_sales.xls с кодировкой: {enc}")
            break
        except Exception:
            try:
                df = pd.read_csv(path, sep=';', encoding=enc, on_bad_lines='skip')
                print(f"✅ Успешно прочитан brand_sales.xls с ';' и кодировкой: {enc}")
                break
            except:
                continue
    if df is None:
        print(f"❌ Не удалось прочитать brand_sales.xls")
        return [], 0
    df.columns = [chr(65 + i) for i in range(len(df.columns))]
    rows = df[df['A'].str.contains(employee, na=False, case=False)]
    bonuses = []
    total_bonus = 0
    for _, row in rows.iterrows():
        kpi_name = row['D']
        target = row['F']
        actual = row['H']
        if pd.isna(target) or pd.isna(actual) or target == 0:
            continue
        performance = (actual / target) * 100
        kpi_bonus = (performance / 100) * 10000
        kpi_bonus = round(kpi_bonus, 2)
        total_bonus += kpi_bonus
        bonuses.append({
            "kpi": kpi_name,
            "target": round(target, 2),
            "actual": round(actual, 2),
            "performance": round(performance, 1),
            "bonus": kpi_bonus
        })
    return bonuses, round(total_bonus, 2)


def get_debt_info(employee, year, month):
    path = find_report_path(year, month, "debt")
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return [], 0, 0
    encodings = ['cp1251', 'utf-8', 'latin1']
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, sep='\t', encoding=enc, on_bad_lines='skip')
            print(f"✅ Успешно прочитан debt.xls с кодировкой: {enc}")
            break
        except Exception:
            try:
                df = pd.read_csv(path, sep=';', encoding=enc, on_bad_lines='skip')
                print(f"✅ Успешно прочитан debt.xls с ';' и кодировкой: {enc}")
                break
            except:
                continue
    if df is None:
        print(f"❌ Не удалось прочитать debt.xls")
        return [], 0, 0
    df.columns = [chr(65 + i) for i in range(len(df.columns))]
    rows = df[df['B'].str.contains(employee, na=False, case=False)]
    debts = []
    total_debt = 0
    for _, row in rows.iterrows():
        counterparty = row['A']
        debt_val = row['B']
        if pd.isna(debt_val):
            continue
        total_debt += debt_val
        debts.append({
            "counterparty": counterparty,
            "debt": round(debt_val, 2)
        })
    penalty = total_debt * 0.01
    return debts, round(total_debt, 2), round(penalty, 2)


def generate_pdf(employee, year, month, profit_data, kpi_data, debt_data):
    pdf = FPDF()
    pdf.add_page()

    # Подключаем шрифт с поддержкой кириллицы
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        print(f"❗ Шрифт не найден: {font_path}. Скачайте его по ссылке:")
        print("https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/DejaVuSans.ttf")
        return
    pdf.add_font("DejaVu", fname=font_path)
    pdf.set_font("DejaVu", size=12)

    month_str = MONTH_NAMES.get(month, str(month))
    pdf.cell(0, 10, text=f"Отчёт по сотруднику: {employee}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 10, text=f"Период: {month_str} {year}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)

    # Прибыль
    income, bonus = profit_data
    pdf.cell(0, 10, text="1. Доход и бонус по прибыли", new_x="LMARGIN", new_y="NEXT", bold=True)
    pdf.cell(0, 10, text=f"Общий доход: {income} руб.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, text=f"Бонус (5%): {bonus} руб.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # KPI
    kpi_list, kpi_total = kpi_data
    pdf.cell(0, 10, text="2. Выполнение KPI", new_x="LMARGIN", new_y="NEXT", bold=True)
    if kpi_list:
        for item in kpi_list:
            pdf.cell(0, 10, text=f"- {item['kpi']}: {item['actual']} из {item['target']} ({item['performance']}%) → Бонус: {item['bonus']} руб.", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, text=f"Итого по KPI: {kpi_total} руб.", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 10, text="KPI не найдены.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Дебиторская задолженность
    debts, total_debt, penalty = debt_data
    pdf.cell(0, 10, text="3. Дебиторская задолженность", new_x="LMARGIN", new_y="NEXT", bold=True)
    if debts:
        for item in debts:
            pdf.cell(0, 10, text=f"- {item['counterparty']}: {item['debt']} руб.", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, text=f"Общая задолженность: {total_debt} руб.", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 10, text=f"Штраф (1%): {penalty} руб.", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 10, text="Задолженности не найдены.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Итог
    total_payout = bonus + kpi_total - penalty
    pdf.set_font("DejaVu", size=14, style="B")
    pdf.cell(0, 10, text=f"ИТОГО к выплате: {round(total_payout, 2)} руб.", new_x="LMARGIN", new_y="NEXT", bold=True)

    # Сохранение
    output_dir = "Reports"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{employee}.pdf")
    pdf.output(filename)
    print(f"✅ Отчёт сохранён: {filename}")


def main():
    employees = read_employees()
    year = 2026
    month = 3

    for emp in employees:
        print(f"\n🔹 Обработка сотрудника: {emp}")
        profit_data = get_profit_bonus(emp, year, month)
        kpi_data = get_kpi_bonuses(emp, year, month)
        debt_data = get_debt_info(emp, year, month)
        generate_pdf(emp, year, month, profit_data, kpi_data, debt_data)


if __name__ == "__main__":
    main()