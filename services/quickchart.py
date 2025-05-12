import requests
import json
from collections import defaultdict
from typing import List
from database.models import Expense


def generate_expense_chart(expenses: List[Expense]) -> str:
    """Генерирует URL графика расходов с помощью QuickChart API"""

    # Группируем расходы по категориям
    categories = defaultdict(float)
    for expense in expenses:
        category = expense.category if expense.category else "Другое"
        categories[category] += expense.amount

    # Сортируем по убыванию суммы
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    # Подготавливаем данные для графика
    chart_config = {
        "type": "bar",
        "data": {
            "labels": [cat[0] for cat in sorted_categories],
            "datasets": [{
                "label": "Сумма расходов (руб)",
                "data": [cat[1] for cat in sorted_categories],
                "backgroundColor": [
                    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0",
                    "#9966FF", "#FF9F40", "#8AC249", "#EA3546"
                ]
            }]
        },
        "options": {
            "scales": {
                "y": {
                    "beginAtZero": True
                }
            },
            "plugins": {
                "legend": {
                    "display": False
                }
            }
        }
    }

    response = requests.post(
        "https://quickchart.io/chart/create",
        json={"chart": chart_config, "width": 600, "height": 400}
    )

    if response.status_code == 200:
        return response.json().get('url')
    else:
        raise Exception("Ошибка при генерации графика")