#!/usr/bin/env python3
"""
Lightweight startup script for Frank's Candidate Concierge
Optimized for Render deployment with faster startup times.
"""

import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables if they don't exist."""
    try:
        from src.models.database.models import Base
        from src.models.database.session import get_db_url
        
        logger.info("Checking database tables...")
        engine = create_engine(get_db_url())
        inspector = inspect(engine)
        
        # Check if tables exist
        existing_tables = inspector.get_table_names()
        required_tables = ['questions', 'answers', 'feedback']
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            logger.info(f"Creating missing tables: {missing_tables}")
            Base.metadata.create_all(engine)
            logger.info("Database tables created successfully!")
        else:
            logger.info("All required database tables exist!")
            
        return True
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        return False

def main():
    """Main startup function with optimized initialization."""
    try:
        logger.info("Starting Frank's Candidate Concierge...")
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Initialize database first
        if not init_database():
            logger.error("Failed to initialize database. Starting anyway...")
        
        # Import and start the FastAPI app
        from src.api.main import app
        import uvicorn
        
        # Get port from environment (Render sets PORT)
        port = int(os.environ.get("PORT", 8000))
        host = "0.0.0.0"
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 