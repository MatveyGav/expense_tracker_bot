from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import or_
from .base import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    join_date = Column(DateTime)
    expenses = relationship("Expense", back_populates="user")
    categories = relationship("Category", back_populates="user")
    receipts = relationship("ReceiptData", back_populates="user")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    name = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    user = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category_obj")

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    description = Column(String)
    date = Column(DateTime, default=datetime.now)
    receipt_data = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'))
    user = relationship("User", back_populates="expenses")
    category_obj = relationship("Category", back_populates="expenses")

class ReceiptData(Base):
    __tablename__ = 'receipts_data'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    expense_id = Column(Integer, ForeignKey('expenses.id'))
    fn = Column(String)
    fd = Column(String)
    fp = Column(String)
    raw_data = Column(String)
    shop_name = Column(String)
    shop_inn = Column(String)
    purchase_date = Column(DateTime)
    user = relationship("User", back_populates="receipts")
    expense = relationship("Expense")

class ReceiptItem(Base):
    __tablename__ = 'receipt_items'
    id = Column(Integer, primary_key=True)
    receipt_id = Column(Integer, ForeignKey('receipts_data.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    sum = Column(Float, nullable=False)
    receipt = relationship("ReceiptData")
    user = relationship("User")