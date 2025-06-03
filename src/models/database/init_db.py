"""Database initialization script for the Candidate Concierge."""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.database import DATABASE_URL
from src.models.database.models import Base
from sqlalchemy import create_engine

def init_database():
    """Create all database tables."""
    print("Connecting to database...")
    print(f"Database URL: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    
    print("✅ Database tables created successfully!")
    print("Tables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    init_database() 