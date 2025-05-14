from aiogram import Router, types
from aiogram.filters import Command
from database import get_db, get_or_create_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    db = next(get_db())
    user = get_or_create_user(
        db=db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    await message.answer(
        "Привет! Я помогу тебе учитывать расходы.\n\n"
        "Доступные команды:\n"
        "/add_expense - добавить расход\n"
        "/report - получить отчет\n"
        "/categories - управление категориями"
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - начать работу\n"
        "/add_expense - добавить расход\n"
        "/report - получить отчет\n"
        "/categories - управление категориями\n"
        "/help - справка"
    )