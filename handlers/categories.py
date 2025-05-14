from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_db, get_user_categories, get_or_create_category

router = Router()


class CategoryStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_new_category = State()


async def make_categories_keyboard(user_id: int):
    db = next(get_db())
    categories = get_user_categories(db, user_id)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
                     [KeyboardButton(text=cat.name)] for cat in categories
                 ] + [
                     [KeyboardButton(text="➕ Создать новую категорию")]
                 ],
        resize_keyboard=True
    )
    return keyboard


@router.message(Command("categories"))
async def cmd_categories(message: Message):
    keyboard = await make_categories_keyboard(message.from_user.id)
    await message.answer("Ваши категории расходов:", reply_markup=keyboard)


@router.message(F.text == "➕ Создать новую категорию")
async def add_new_category(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.waiting_for_new_category)
    await message.answer("Введите название новой категории:", reply_markup=ReplyKeyboardRemove())


@router.message(CategoryStates.waiting_for_new_category)
async def process_new_category(message: Message, state: FSMContext):
    db = next(get_db())
    if not message.text.strip():
        await message.answer("Название категории не может быть пустым!")
        return

    if len(message.text) > 30:
        await message.answer("Название категории слишком длинное (макс. 30 символов)")
        return

    category = get_or_create_category(db, message.text.strip(), message.from_user.id)
    await state.clear()
    await message.answer(
        f"Категория '{category.name}' успешно добавлена!",
        reply_markup=await make_categories_keyboard(message.from_user.id)
    )