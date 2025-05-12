from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from database import get_user_expenses, get_db
from services.quickchart import generate_expense_chart
import logging

router = Router()


class ReportStates(StatesGroup):
    waiting_custom_period = State()


class ReportPeriods:
    WEEK = 7
    MONTH = 30
    YEAR = 365


@router.message(Command("report"))
async def cmd_report(message: types.Message):
    await message.answer(
        "Выберите период для отчета:\n"
        "/week - за неделю\n"
        "/month - за месяц\n"
        "/year - за год\n"
        "/custom - произвольный период"
    )


@router.message(Command("week"))
async def weekly_report(message: types.Message):
    await generate_report(message, ReportPeriods.WEEK)


@router.message(Command("month"))
async def monthly_report(message: types.Message):
    await generate_report(message, ReportPeriods.MONTH)


@router.message(Command("year"))
async def yearly_report(message: types.Message):
    await generate_report(message, ReportPeriods.YEAR)


@router.message(Command("custom"))
async def custom_period_start(message: types.Message, state: FSMContext):
    await message.answer("Введите количество дней для отчета:")
    await state.set_state(ReportStates.waiting_custom_period)


@router.message(ReportStates.waiting_custom_period)
async def handle_custom_period(message: types.Message, state: FSMContext):
    try:
        days = int(message.text)
        if days <= 0:
            raise ValueError
        await generate_report(message, days)
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите целое число больше 0")


async def generate_report(message: types.Message, period_days: int):
    db = next(get_db())
    expenses = get_user_expenses(
        db=db,
        user_id=message.from_user.id,
        period_days=period_days
    )

    if not expenses:
        await message.answer("Нет данных о расходах за выбранный период.")
        return

    try:
        chart_url = generate_expense_chart(expenses)
        await message.answer_photo(
            chart_url,
            caption=f"Ваши расходы за последние {period_days} дней"
        )
    except Exception as e:
        logging.error(f"Ошибка генерации отчета: {e}")
        await message.answer("Произошла ошибка при генерации отчета")