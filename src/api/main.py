from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from src.models.qa_model import QAModel
from src.models.database.session import get_db
from src.models.database.operations import DatabaseOperations
from typing import List, Optional
from datetime import datetime
import logging
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Frank's Candidate Concierge API",
    description="API for answering questions about Frank's resume using DistilBERT",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the QA model
qa_model = QAModel()

class Question(BaseModel):
    text: str

class Answer(BaseModel):
    id: int = None
    answer: str
    confidence: float

class FeedbackRequest(BaseModel):
    answer_id: int
    score: int
    was_helpful: bool
    comment: Optional[str] = None

class QAHistory(BaseModel):
    question_id: int
    question_text: str
    question_timestamp: datetime
    answer_id: int = None
    answer_text: str = None
    confidence: float = None
    source: str = None
    answer_timestamp: datetime = None

class FeedbackHistory(BaseModel):
    feedback_id: int
    answer_id: int
    score: int
    was_helpful: bool
    comment: str = None
    timestamp: datetime
    answer_text: str = None

@app.get("/")
async def root():
    return {"message": "Welcome to Frank's Candidate Concierge API"}

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question, db: Session = Depends(get_db)):
    try:
        logger.info(f"Question received: {question.text}")
        db_ops = DatabaseOperations(db)
        answer_text, confidence = qa_model.answer_question(question.text)
        
        # Store the interaction
        _, answer_record = db_ops.store_qa_interaction(
            question_text=question.text,
            answer_text=answer_text,
            confidence=confidence,
            source='qa_model' if confidence > 0.7 else 'structured'
        )
        
        logger.info(f"Answer generated - ID: {answer_record.id}, Confidence: {confidence}")
        
        return Answer(
            id=answer_record.id,
            answer=answer_text,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[QAHistory])
async def get_qa_history(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent question and answer history."""
    try:
        from src.models.database.models import Question, Answer
        
        # Query the database for recent Q&A pairs
        results = db.query(Question, Answer).join(
            Answer, Question.id == Answer.question_id, isouter=True
        ).order_by(Question.timestamp.desc()).limit(limit).all()
        
        history = []
        for question, answer in results:
            history.append(QAHistory(
                question_id=question.id,
                question_text=question.text,
                question_timestamp=question.timestamp,
                answer_id=answer.id if answer else None,
                answer_text=answer.text if answer else None,
                confidence=answer.confidence if answer else None,
                source=answer.source if answer else None,
                answer_timestamp=answer.timestamp if answer else None
            ))
        
        logger.info(f"Retrieved {len(history)} Q&A history records")
        return history
    except Exception as e:
        logger.error(f"Error in get_qa_history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback", response_model=List[FeedbackHistory])
async def get_feedback_history(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent feedback history."""
    try:
        from src.models.database.models import Feedback, Answer
        
        # Query the database for feedback records
        results = db.query(Feedback, Answer).join(
            Answer, Feedback.answer_id == Answer.id, isouter=True
        ).order_by(Feedback.timestamp.desc()).limit(limit).all()
        
        feedback_history = []
        for feedback, answer in results:
            feedback_history.append(FeedbackHistory(
                feedback_id=feedback.id,
                answer_id=feedback.answer_id,
                score=feedback.score,
                was_helpful=feedback.was_helpful,
                comment=feedback.comment,
                timestamp=feedback.timestamp,
                answer_text=answer.text if answer else None
            ))
        
        logger.info(f"Retrieved {len(feedback_history)} feedback records")
        return feedback_history
    except Exception as e:
        logger.error(f"Error in get_feedback_history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Feedback received: answer_id={feedback.answer_id}, score={feedback.score}, helpful={feedback.was_helpful}, comment={feedback.comment}")
        
        # Detailed validation logging
        logger.info(f"Feedback validation - answer_id type: {type(feedback.answer_id)}")
        logger.info(f"Feedback validation - score type: {type(feedback.score)}")
        logger.info(f"Feedback validation - was_helpful type: {type(feedback.was_helpful)}")
        logger.info(f"Feedback validation - comment type: {type(feedback.comment)}")
        
        db_ops = DatabaseOperations(db)
        feedback_record = db_ops.store_feedback(
            answer_id=feedback.answer_id,
            score=feedback.score,
            was_helpful=feedback.was_helpful,
            comment=feedback.comment
        )
        
        logger.info(f"Feedback stored successfully - ID: {feedback_record.id}")
        return {"status": "success", "feedback_id": feedback_record.id}
        
    except ValidationError as ve:
        logger.error(f"Validation error in submit_feedback: {str(ve)}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        logger.error(f"Error in submit_feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 