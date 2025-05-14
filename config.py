import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROVERKA_CHEKA_API_KEY = os.getenv("PROVERKA_CHEKA_API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    QUICKCHART_API_URL = "https://quickchart.io/chart/create"
    PROVERKA_CHEKA_API_URL = "https://proverkacheka.com/api/v1/check/get"