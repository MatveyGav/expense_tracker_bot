from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta
from .models import User, Expense, Category, ReceiptData, ReceiptItem

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
    return user

def create_expense(db: Session, user_id: int, amount: float, description: str = None, receipt_data: str = None):
    expense = Expense(
        user_id=user_id,
        amount=amount,
        description=description,
        receipt_data=receipt_data,
        date=datetime.now()
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

def create_default_categories(db: Session):
    default_categories = ["Продукты", "Транспорт", "Кафе", "Здоровье", "Развлечения", "Одежда", "Жилье", "Другое"]
    for name in default_categories:
        if not db.query(Category).filter_by(name=name, is_default=True).first():
            category = Category(name=name, is_default=True)
            db.add(category)
    db.commit()

def get_or_create_category(db: Session, name: str, user_id: int = None):
    category = db.query(Category).filter(
        Category.name == name,
        or_(Category.user_id == user_id, Category.user_id.is_(None))
    ).first()
    if not category:
        category = Category(name=name, user_id=user_id)
        db.add(category)
        db.commit()
    return category

def get_user_categories(db: Session, user_id: int):
    return db.query(Category).filter(
        or_(Category.user_id == user_id, Category.is_default == True)
    ).all()

def create_receipt_data(db: Session, user_id: int, expense_id: int, fn: str, fd: str, fp: str,
                       raw_data: str, shop_name: str, shop_inn: str, purchase_date: datetime, items: list):
    receipt = ReceiptData(
        user_id=user_id,
        expense_id=expense_id,
        fn=fn,
        fd=fd,
        fp=fp,
        raw_data=raw_data,
        shop_name=shop_name,
        shop_inn=shop_inn,
        purchase_date=purchase_date
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    for item in items:
        db_item = ReceiptItem(
            receipt_id=receipt.id,
            user_id=user_id,
            name=item.get('name', 'Без названия'),
            price=float(item.get('price', 0)) / 100,
            quantity=float(item.get('quantity', 1)),
            sum=float(item.get('sum', 0)) / 100
        )
        db.add(db_item)
    db.commit()
    return receipt