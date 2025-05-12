import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    PROVERKA_CHEKA_API_KEY = os.getenv("PROVERKA_CHEKA_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./expense_tracker.db")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))