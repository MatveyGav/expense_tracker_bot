from aiogram import Router, types
from aiogram.filters import Command
from database import get_or_create_user, get_db

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user = get_or_create_user(
        db=next(get_db()),
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    await message.answer("Привет! Я бот для учета расходов.")