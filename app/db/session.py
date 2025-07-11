from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./logistic.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models here to ensure they are registered with SQLAlchemy
    from app.models import logistic
    Base.metadata.create_all(bind=engine)
