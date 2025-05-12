import logging
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher
from config import Config
from handlers import start_router, expenses_router, reports_router
from database import init_db
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def main():
    # Инициализация бота
    bot = Bot(
        token=Config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение роутеров
    dp.include_router(start_router)
    dp.include_router(expenses_router)
    dp.include_router(reports_router)

    # Инициализация БД
    init_db()

    # Уведомление админа
    if Config.ADMIN_ID:
        try:
            await bot.send_message(
                chat_id=Config.ADMIN_ID,
                text="🟢 Бот успешно запущен"
            )
        except Exception as e:
            logging.error(f"Admin notification failed: {e}")

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())