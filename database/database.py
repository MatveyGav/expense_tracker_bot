from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
from .crud import create_default_categories

SQLALCHEMY_DATABASE_URL = "sqlite:///./expense_tracker.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_default_categories(db)
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()