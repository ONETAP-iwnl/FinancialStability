def calculate_coefficients(financial_row: tuple) -> dict:
    """
    Принимает кортеж из БД:
    (period, assets, liabilities, equity, profit, revenue, current_assets, current_liabilities)
    Возвращает словарь с рассчитанными коэффициентами и статусами.
    """
    (period, assets, liabilities, equity, profit, revenue, current_assets, current_liabilities) = financial_row

    # Защита от деления на ноль
    def safe_div(a, b):
        return a / b if b != 0 else 0

    # 🔸 1. Коэффициент текущей ликвидности
    current_ratio = safe_div(current_assets, current_liabilities)

    # 🔸 2. Коэффициент автономии
    autonomy_ratio = safe_div(equity, assets)

    # 🔸 3. Коэффициент финансовой зависимости
    debt_ratio = safe_div(liabilities, assets)

    # 🔸 4. Рентабельность продаж (%)
    profitability_sales = safe_div(profit, revenue) * 100

    # 🔸 5. Рентабельность активов (%)
    profitability_assets = safe_div(profit, assets) * 100

    # --- Нормативные значения ---
    norms = {
        "current_ratio": 2.0,           # >= 2
        "autonomy_ratio": 0.5,          # >= 0.5
        "debt_ratio": 0.5,              # желательно <= 0.5
        "profitability_sales": 5.0,     # условно, от 5% и выше
        "profitability_assets": 5.0     # условно, от 5% и выше
    }

    # Проверки норм
    statuses = {
        "current_ratio": current_ratio >= norms["current_ratio"],
        "autonomy_ratio": autonomy_ratio >= norms["autonomy_ratio"],
        "debt_ratio": debt_ratio <= norms["debt_ratio"],
        "profitability_sales": profitability_sales >= norms["profitability_sales"],
        "profitability_assets": profitability_assets >= norms["profitability_assets"]
    }

    # Подсчёт количества норм в порядке
    ok_count = sum(statuses.values())
    total = len(statuses)

    # Итоговая оценка устойчивости
    if ok_count == total:
        summary = "Устойчивая"
    elif ok_count >= total - 1:
        summary = "Удовлетворительная"
    elif ok_count >= total // 2:
        summary = "Нестабильная"
    else:
        summary = "Критическая"

    return {
        "period": period,
        "current_ratio": current_ratio,
        "autonomy_ratio": autonomy_ratio,
        "debt_ratio": debt_ratio,
        "profitability_sales": profitability_sales,
        "profitability_assets": profitability_assets,
        "statuses": statuses,
        "summary": summary
    }
