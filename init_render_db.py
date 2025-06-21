"""Initialize Render PostgreSQL database with tables."""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Render database connection
# Replace with your actual Render DATABASE_URL
DATABASE_URL = "postgresql://franks_concierge_db_user:REMOVED_DATABASE_PASSWORD@dpg-d16bau2dbo4c73evikqg-a.oregon-postgres.render.com:5432/franks_concierge_db"

Base = declarative_base()

# Define models
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

def init_render_database():
    """Create all database tables on Render."""
    print("Connecting to Render database...")
    print(f"Database URL: {DATABASE_URL}")
    
    # Add SSL requirement for Render
    engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
    
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    
    print("✅ Database tables created successfully on Render!")
    print("Tables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    print("🚀 Initializing Render PostgreSQL Database")
    print("=" * 50)
    
    # Prompt user to update DATABASE_URL
    print("⚠️  IMPORTANT: Please update the DATABASE_URL in this script with your actual Render credentials!")
    print("   Replace 'YOUR_PASSWORD' with your real database password")
    print()
    
    response = input("Have you updated the DATABASE_URL? (y/n): ")
    if response.lower() == 'y':
        init_render_database()
    else:
        print("Please update the DATABASE_URL first, then run this script again.") 