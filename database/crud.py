from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from .models import User, Expense, ReceiptData


# User operations
def get_or_create_user(db: Session, telegram_id: int, username: str, first_name: str, last_name: str):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            join_date=datetime.now()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# Expense operations
def create_expense(db: Session, user_id: int, amount: float, category: str = None, description: str = None, receipt_data: dict = None):
    expense = Expense(
        user_id=user_id,
        amount=amount,
        category=category,
        description=description,
        date=datetime.now(),
        receipt_data=json.dumps(receipt_data) if receipt_data else None
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

def get_user_expenses(db: Session, user_id: int, period_days: int = 30):
    date_from = datetime.now() - timedelta(days=period_days)
    return db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= date_from
    ).order_by(Expense.date.desc()).all()

# Receipt operations
def create_receipt_data(db: Session, expense_id: int, fn: str, fd: str, fp: str, raw_data: dict, shop_name: str, shop_inn: str, purchase_date: str):
    receipt = ReceiptData(
        expense_id=expense_id,
        fn=fn,
        fd=fd,
        fp=fp,
        raw_data=json.dumps(raw_data),
        shop_name=shop_name,
        shop_inn=shop_inn,
        purchase_date=purchase_date
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt