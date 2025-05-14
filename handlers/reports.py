from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database import get_db, get_user_expenses
from services.quickchart import generate_expense_chart
from datetime import datetime, timedelta
from aiogram.fsm.state import State, StatesGroup

router = Router()

class ReportPeriod(StatesGroup):
    waiting_period = State()

@router.message(Command("report"))
async def cmd_report(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="За неделю")],
            [KeyboardButton(text="За месяц")],
            [KeyboardButton(text="За год")],
            [KeyboardButton(text="Произвольный период")]
        ],
        resize_keyboard=True
    )
    await state.set_state(ReportPeriod.waiting_period)
    await message.answer("Выберите период для отчета:", reply_markup=keyboard)

@router.message(ReportPeriod.waiting_period, F.text.in_(["За неделю", "За месяц", "За год"]))
async def handle_period_selection(message: Message, state: FSMContext):
    db = next(get_db())
    user_id = message.from_user.id
    period_map = {"За неделю": 7, "За месяц": 30, "За год": 365}
    period_days = period_map[message.text]

    expenses = get_user_expenses(db, user_id, period_days)
    if not expenses:
        await message.answer(f"Нет расходов за выбранный период.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return

    try:
        chart_url = generate_expense_chart(expenses)
        await message.answer_photo(
            chart_url,
            caption=f"Ваши расходы за {message.text.lower()}",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        await message.answer("Ошибка при генерации отчета", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

@router.message(ReportPeriod.waiting_period, F.text == "Произвольный период")
async def ask_custom_period(message: Message, state: FSMContext):
    await message.answer(
        "Введите количество дней для отчета (например: 14):",
        reply_markup=types.ReplyKeyboardRemove()
    )

@router.message(ReportPeriod.waiting_period, F.text.regexp(r'^\d+$'))
async def handle_custom_period(message: Message, state: FSMContext):
    db = next(get_db())
    user_id = message.from_user.id

    try:
        period_days = int(message.text)
        if period_days <= 0:
            raise ValueError

        expenses = get_user_expenses(db, user_id, period_days)
        if not expenses:
            await message.answer(f"Нет расходов за последние {period_days} дней.")
            await state.clear()
            return

        chart_url = generate_expense_chart(expenses)
        await message.answer_photo(
            chart_url,
            caption=f"Ваши расходы за последние {period_days} дней"
        )
    except ValueError:
        await message.answer("Пожалуйста, введите положительное число дней")
        return
    await state.clear()