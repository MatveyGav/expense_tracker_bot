from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from services.receipt_parser import parse_receipt_from_qr
from database import get_db, create_expense, create_receipt_data, get_user_categories, get_or_create_category, Expense, ReceiptData, ReceiptItem
import json
from datetime import datetime
import os

router = Router()


class ReceiptStates(StatesGroup):
    waiting_category = State()


async def make_categories_keyboard(user_id: int):
    db = next(get_db())
    categories = get_user_categories(db, user_id)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=cat.name)] for cat in categories
        ],
        resize_keyboard=True
    )
    return keyboard


@router.message(F.photo)
async def handle_qr_photo(message: types.Message, state: FSMContext):
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
            receipt_data=json.dumps(receipt_data)
        )

        receipt = create_receipt_data(
            db=db,
            user_id=message.from_user.id,
            expense_id=expense.id,
            fn=receipt_data['fiscalDriveNumber'],
            fd=receipt_data['fiscalDocumentNumber'],
            fp=receipt_data['fiscalSign'],
            raw_data=json.dumps(receipt_data),
            shop_name=receipt_data.get('user', 'Неизвестно'),
            shop_inn=receipt_data.get('userInn', '').strip(),
            purchase_date=datetime.strptime(receipt_data['dateTime'], '%Y-%m-%dT%H:%M:%S'),
            items=receipt_data.get('items', [])
        )

        await state.update_data(expense_id=expense.id)
        await state.set_state(ReceiptStates.waiting_category)

        await message.answer(
            "Выберите категорию для этого чека:",
            reply_markup=await make_categories_keyboard(message.from_user.id)
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка обработки чека: {str(e)}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


@router.message(ReceiptStates.waiting_category)
async def process_category_selection(message: types.Message, state: FSMContext):
    db = next(get_db())
    user_data = await state.get_data()

    expense = db.query(Expense).get(user_data['expense_id'])
    category = get_or_create_category(db, message.text, message.from_user.id)
    receipt_data = db.query(ReceiptData).filter_by(expense_id=expense.id).first()
    items = db.query(ReceiptItem).filter_by(receipt_id=receipt_data.id).all()

    purchase_date = receipt_data.purchase_date.strftime('%d.%m.%Y %H:%M')

    items_text = "\n".join(
        f"• {item.name} - {item.quantity} x {item.price:.2f}₽ = {item.sum:.2f}₽"
        for item in items
    )

    message_text = (
        f"✅ Чек отнесен к категории '{category.name}'\n\n"
        f"🏪 Магазин: {receipt_data.shop_name or 'Не указан'}\n"
        f"📅 Дата: {purchase_date}\n"
        f"💳 Сумма: {expense.amount:.2f}₽\n\n"
        f"🛍️ Товары ({len(items)}):\n{items_text}"
    )

    expense.category_id = category.id
    db.commit()

    await state.clear()
    await message.answer(
        message_text,
        reply_markup=ReplyKeyboardRemove()
    )