import os
os.makedirs("logs", exist_ok=True)

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
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
from pathlib import Path

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

class TrainingRequest(BaseModel):
    force_retrain: bool = False
    min_feedback_score: int = 4
    min_confidence: float = 0.7

class TrainingStatus(BaseModel):
    status: str
    last_training_date: Optional[datetime] = None
    training_samples: int = 0
    satisfaction_rate: float = 0.0
    is_training: bool = False

@app.get("/")
async def root():
    return {"message": "Welcome to Frank's Candidate Concierge API"}

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    try:
        logger.info(f"Question received: {question.text}")
        
        # Get answer without database
        answer_text, confidence, source = qa_model.answer_question(question.text)
        
        logger.info(f"Answer generated - Confidence: {confidence}, Source: {source}")
        
        return Answer(
            id=0,  # Dummy ID since we're not using database
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

@app.get("/training/status", response_model=TrainingStatus)
async def get_training_status(db: Session = Depends(get_db)):
    """Get current training status and model performance metrics."""
    try:
        db_ops = DatabaseOperations(db)
        
        # Get feedback statistics
        feedback_stats = db_ops.get_feedback_stats()
        
        total_feedback = sum(count for _, count in feedback_stats)
        positive_feedback = sum(count for score, count in feedback_stats if score >= 4)
        satisfaction_rate = positive_feedback / total_feedback if total_feedback > 0 else 0.0
        
        # Check for latest training metadata
        models_dir = Path("models")
        latest_training = None
        training_samples = 0
        
        if models_dir.exists():
            training_dirs = [d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith("fine_tuned_")]
            if training_dirs:
                latest_dir = max(training_dirs, key=lambda x: x.stat().st_mtime)
                metadata_file = latest_dir / "training_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        latest_training = datetime.fromisoformat(metadata["training_date"])
                        training_samples = metadata["training_samples"]
        
        return TrainingStatus(
            status="ready",
            last_training_date=latest_training,
            training_samples=training_samples,
            satisfaction_rate=satisfaction_rate,
            is_training=False
        )
        
    except Exception as e:
        logger.error(f"Error in get_training_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/training/start")
async def start_training(
    training_request: TrainingRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """Start model training in the background."""
    try:
        logger.info("Training request received")
        
        # Check if we have enough feedback data
        db_ops = DatabaseOperations(db)
        training_data = db_ops.get_training_data(
            min_feedback_score=training_request.min_feedback_score,
            min_confidence=training_request.min_confidence
        )
        
        if len(training_data) < 3 and not training_request.force_retrain:
            logger.warning(f"Insufficient training data: {len(training_data)} samples")
            return {
                "status": "insufficient_data",
                "message": f"Need at least 3 high-quality feedback samples to train. Currently have {len(training_data)}.",
                "suggestion": "Collect more user feedback or use force_retrain=true to train with synthetic data."
            }
        
        # Start training in background
        background_tasks.add_task(run_training_task, training_request.dict())
        
        logger.info("Training started in background")
        return {
            "status": "training_started",
            "message": "Model training has been started in the background.",
            "training_samples": len(training_data)
        }
        
    except Exception as e:
        logger.error(f"Error in start_training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_training_task(training_params: dict):
    """Background task to run model training."""
    try:
        logger.info("Background training task started")
        
        # Import here to avoid circular imports
        from src.models.training import run_training_pipeline
        
        # Run the training pipeline
        success = run_training_pipeline()
        
        if success:
            logger.info("Background training completed successfully")
        else:
            logger.error("Background training failed")
            
    except Exception as e:
        logger.error(f"Background training error: {str(e)}")

@app.get("/health")
async def health_check():
    """Simple health check that doesn't require database or ML model."""
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health/full")
async def full_health_check(db: Session = Depends(get_db)):
    """Full health check including database connectivity."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "ml_model": "lazy_loaded",
        "timestamp": datetime.now().isoformat()
    } 