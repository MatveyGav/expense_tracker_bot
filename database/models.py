from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    join_date = Column(DateTime)

    expenses = relationship("Expense", back_populates="user")


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    category = Column(String)
    description = Column(String)
    date = Column(DateTime)
    receipt_data = Column(String)

    user = relationship("User", back_populates="expenses")


class ReceiptData(Base):
    __tablename__ = 'receipts_data'

    id = Column(Integer, primary_key=True)
    expense_id = Column(Integer, ForeignKey('expenses.id'))
    fn = Column(String)
    fd = Column(String)
    fp = Column(String)
    raw_data = Column(String)
    shop_name = Column(String)
    shop_inn = Column(String)
    purchase_date = Column(DateTime)

    expense = relationship("Expense")