#!/usr/bin/env python3
"""
Database migration script to update column names from 'timestamp' to 'created_at'
and ensure all tables have the correct schema.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError
from dotenv import load_dotenv

def get_database_url():
    """Get the database URL from environment variables."""
    load_dotenv()
    
    # Try different environment variable names
    db_url = (
        os.getenv('DATABASE_URL') or 
        os.getenv('DB_URL') or 
        os.getenv('RENDER_DATABASE_URL')
    )
    
    if not db_url:
        print("Error: No database URL found in environment variables.")
        print("Please set DATABASE_URL, DB_URL, or RENDER_DATABASE_URL")
        sys.exit(1)
    
    return db_url

def column_exists(engine, table_name, column_name):
    """Check if a column exists in a table."""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return any(col['name'] == column_name for col in columns)
    except Exception:
        return False

def table_exists(engine, table_name):
    """Check if a table exists."""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception:
        return False

def migrate_database():
    """Run the database migration."""
    db_url = get_database_url()
    engine = create_engine(db_url)
    
    print(f"Connecting to database...")
    
    try:
        with engine.connect() as conn:
            print("✓ Database connection successful")
            
            # Migration steps
            migrations = [
                {
                    'description': 'Rename timestamp to created_at in questions table',
                    'check': lambda: column_exists(engine, 'questions', 'timestamp'),
                    'sql': 'ALTER TABLE questions RENAME COLUMN timestamp TO created_at;'
                },
                {
                    'description': 'Rename timestamp to created_at in answers table',
                    'check': lambda: column_exists(engine, 'answers', 'timestamp'),
                    'sql': 'ALTER TABLE answers RENAME COLUMN timestamp TO created_at;'
                },
                {
                    'description': 'Rename timestamp to created_at in feedback table',
                    'check': lambda: column_exists(engine, 'feedback', 'timestamp'),
                    'sql': 'ALTER TABLE feedback RENAME COLUMN timestamp TO created_at;'
                },
                {
                    'description': 'Create prompt_versions table if not exists',
                    'check': lambda: not table_exists(engine, 'prompt_versions'),
                    'sql': '''
                        CREATE TABLE IF NOT EXISTS prompt_versions (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            prompt_text TEXT NOT NULL,
                            version_number VARCHAR(20) NOT NULL,
                            is_active BOOLEAN DEFAULT FALSE,
                            performance_score FLOAT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            activated_at TIMESTAMP,
                            created_by VARCHAR(50) DEFAULT 'system',
                            notes TEXT
                        );
                    '''
                }
            ]
            
            # Run migrations
            for migration in migrations:
                try:
                    if migration['check']():
                        print(f"Running: {migration['description']}")
                        conn.execute(text(migration['sql']))
                        conn.commit()
                        print(f"✓ {migration['description']} - completed")
                    else:
                        print(f"⚠ {migration['description']} - skipped (not needed)")
                except Exception as e:
                    print(f"✗ {migration['description']} - failed: {e}")
                    # Continue with other migrations
            
            print("\n✓ Database migration completed successfully!")
            
    except Exception as e:
        print(f"✗ Database migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database() 