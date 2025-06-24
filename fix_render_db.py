#!/usr/bin/env python3
"""
Simple script to fix the database schema on Render.
This script will rename timestamp columns to created_at.
"""

import os
import psycopg2
from dotenv import load_dotenv

def fix_database():
    """Fix the database schema by renaming timestamp columns."""
    load_dotenv()
    
    # Get database URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment variables")
        return False
    
    print("Connecting to database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✓ Database connection successful")
        
        # Check and fix each table
        tables_to_fix = ['questions', 'answers', 'feedback']
        
        for table in tables_to_fix:
            try:
                # Check if timestamp column exists
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = 'timestamp'
                """, (table,))
                
                if cursor.fetchone():
                    print(f"Fixing {table} table...")
                    cursor.execute(f"ALTER TABLE {table} RENAME COLUMN timestamp TO created_at;")
                    print(f"✓ {table} table fixed")
                else:
                    print(f"⚠ {table} table already correct")
                    
            except Exception as e:
                print(f"Error fixing {table}: {e}")
                conn.rollback()
                continue
        
        # Create prompt_versions table if it doesn't exist
        try:
            cursor.execute("""
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
            """)
            print("✓ prompt_versions table created/verified")
        except Exception as e:
            print(f"Error creating prompt_versions table: {e}")
        
        # Commit all changes
        conn.commit()
        print("✓ All database changes committed successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("\n🎉 Database schema fixed successfully!")
        print("Your app should now work correctly.")
    else:
        print("\n❌ Database fix failed.")
        print("Please check your DATABASE_URL and try again.") 