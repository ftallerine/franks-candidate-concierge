"""SQLAlchemy models for the Candidate Concierge database."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

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