"""Simple database initialization script for the Candidate Concierge."""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "concierge_db")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

Base = declarative_base()

# Define models directly in this script
class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    answers = relationship("Answer", back_populates="question")

class Answer(Base):
    __tablename__ = 'answers'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    source = Column(String(50))  # 'structured' or 'qa_model'
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    question = relationship("Question", back_populates="answers")
    feedback = relationship("Feedback", back_populates="answer")

class Feedback(Base):
    __tablename__ = 'feedback'
    
    id = Column(Integer, primary_key=True)
    answer_id = Column(Integer, ForeignKey('answers.id'))
    score = Column(Integer)  # 1-5 rating
    was_helpful = Column(Boolean)
    comment = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    answer = relationship("Answer", back_populates="feedback")

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