from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.receipt_parser import parse_receipt_from_qr
from database import get_db, create_expense, create_receipt_data
import json
from datetime import datetime
import os

router = Router()  # Создаем экземпляр роутера


class ExpenseStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()


@router.message(Command("add_expense"))
async def cmd_add_expense(message: types.Message, state: FSMContext):
    await state.set_state(ExpenseStates.waiting_for_amount)
    await message.answer("Введите сумму расхода:")


@router.message(ExpenseStates.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await state.set_state(ExpenseStates.waiting_for_category)
        await message.answer("Введите категорию расхода:")
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму (число)")


@router.message(ExpenseStates.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    db = next(get_db())

    expense = create_expense(
        db=db,
        user_id=message.from_user.id,
        amount=user_data['amount'],
        category=message.text,
        date=datetime.now()
    )

    await state.clear()
    await message.answer(f"Расход на сумму {user_data['amount']}₽ успешно добавлен в категорию '{message.text}'")


@router.message(F.photo)
async def handle_qr_photo(message: types.Message):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    downloaded_file = await message.bot.download_file(file.file_path)

    temp_file = f"temp_{message.from_user.id}.jpg"
    try:
        with open(temp_file, 'wb') as f:
            f.write(downloaded_file.read())

        receipt_data = await parse_receipt_from_qr(temp_file)
        db = next(get_db())

        expense = create_expense(
            db=db,
            user_id=message.from_user.id,
            amount=receipt_data['totalSum'] / 100,
            receipt_data=json.dumps(receipt_data),
            date=datetime.strptime(receipt_data['dateTime'], '%Y-%m-%dT%H:%M:%S')
        )

        create_receipt_data(
            db=db,
            expense_id=expense.id,
            fn=receipt_data['fiscalDriveNumber'],
            fd=receipt_data['fiscalDocumentNumber'],
            fp=receipt_data['fiscalSign'],
            raw_data=json.dumps(receipt_data),
            shop_name=receipt_data['user'],
            shop_inn=receipt_data['userInn'],
            purchase_date=receipt_data['dateTime']
        )

        await message.answer(f"Чек на сумму {receipt_data['totalSum'] / 100}₽ успешно добавлен!")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)