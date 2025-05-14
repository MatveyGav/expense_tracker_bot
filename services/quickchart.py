import requests
from config import Config

def generate_expense_chart(expenses, chart_type="bar", bg_color="#36A2EB"):
    categories = {}
    for expense in expenses:
        category_name = expense.category_obj.name if expense.category_obj else "Без категории"
        categories[category_name] = categories.get(category_name, 0) + expense.amount

    chart_config = {
        "type": chart_type,
        "data": {
            "labels": list(categories.keys()),
            "datasets": [{
                "label": "Сумма расходов",
                "data": list(categories.values()),
                "backgroundColor": bg_color
            }]
        },
        "options": {
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Распределение расходов по категориям"
                }
            }
        }
    }

    response = requests.post(
        Config.QUICKCHART_API_URL,
        json={"chart": chart_config, "width": 800, "height": 400},
        timeout=10
    )
    if response.status_code != 200:
        raise ValueError(f"QuickChart API error: {response.text}")
    return response.json().get('url')