import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers import start, expenses, categories, reports
from database.database import init_db
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def main():
    bot = Bot(
        token=Config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(expenses.router)
    dp.include_router(categories.router)
    dp.include_router(reports.router)

    init_db()

    if Config.ADMIN_ID:
        try:
            await bot.send_message(Config.ADMIN_ID, "🟢 Бот запущен")
        except Exception as e:
            logging.error(f"Admin notification failed: {e}")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())