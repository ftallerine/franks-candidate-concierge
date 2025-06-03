"""Database session management for the Candidate Concierge."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 