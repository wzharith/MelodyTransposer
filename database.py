from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Create database engine
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
