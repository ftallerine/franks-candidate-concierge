"""
Standalone version of Frank's Candidate Concierge API
Now with database logging capabilities
"""

import sys
import os
from typing import Optional

# This block MUST come BEFORE any `from src...` imports.
# It fixes the Python path to be able to find the `src` module in deployment.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Local application imports (changed to relative)
from .models.qa_model import QAModel
from .models.gpt_service import GPTService
from .config.data_loader import RESUME_DATA
from .services.logging_config import logger, get_log_viewer_html
from .models.database.session import get_db
from .models.database.operations import DatabaseOperations
from .models.database.models import Feedback

# --- Global Variables ---
# Create logs directory
os.makedirs("logs", exist_ok=True)

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

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    global model, gpt_service
    logger.info("Application starting up...")
    model = QAModel()
    
    # Initialize GPT service (will be None if OPENAI_API_KEY is not set)
    try:
        gpt_service = GPTService()
        logger.info("GPT service initialized successfully")
    except ValueError as e:
        logger.warning(f"GPT service not available: {e}")
        gpt_service = None
    
    yield
    logger.info("Application shutting down...")

# --- App Initialization ---
app = FastAPI(
    title="Frank's Candidate Concierge API",
    description="An API for a question-answering chatbot about Frank's qualifications.",
    version="1.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model: Optional[QAModel] = None
gpt_service: Optional[GPTService] = None

class Question(BaseModel):
    """A question about Frank's qualifications."""
    text: str = Field(
        ...,
        description="The question to ask about Frank's experience, skills, or qualifications",
        example="What certifications do you have?"
    )

class Answer(BaseModel):
    """An answer to a question about Frank's qualifications."""
    answer: str = Field(
        ...,
        description="The detailed answer to the question"
    )
    confidence: float = Field(
        ...,
        description="Confidence score for the answer (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    answer_id: int = Field(
        None,
        description="Database ID of the answer (for feedback purposes)"
    )

class FeedbackRequest(BaseModel):
    """Feedback on an answer."""
    answer_id: int = Field(
        ...,
        description="The ID of the answer being rated"
    )
    score: int = Field(
        ...,
        description="Rating score (1-5)",
        ge=1,
        le=5
    )
    was_helpful: bool = Field(
        ...,
        description="Whether the answer was helpful"
    )
    comment: str = Field(
        None,
        description="Optional feedback comment"
    )

@app.get("/",
    summary="Welcome Message",
    description="Returns a welcome message to confirm the API is running.",
    response_description="A simple welcome message"
)
async def root():
    """Get a welcome message."""
    return {"message": "Welcome to Frank's Candidate Concierge API"}

@app.get("/health",
    summary="Health Check",
    description="Check if the API is healthy and running.",
    response_description="Health status and timestamp"
)
async def health_check():
    """Check if the API is healthy."""
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/ask", tags=["Q&A"])
async def ask_question(question: Question, db: Session = Depends(get_db)):
    """
    Receives a question, gets an answer from the QA model with GPT fallback, and logs the interaction.
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model is not available")

    # Try the local QA model first
    answer_text, confidence = model.answer_question(question.text)
    answer_source = "qa_model"
    
    # If confidence is low (< 0.3) and GPT service is available, use GPT as fallback
    if confidence < 0.3 and gpt_service:
        logger.info(f"Low confidence ({confidence:.3f}), trying GPT fallback")
        try:
            # Create a context-aware prompt for GPT
            gpt_prompt = f"""You are Frank's professional assistant. Answer this question about Frank's qualifications, experience, and skills based on his resume.

Question: {question.text}

Resume Context: {RESUME_DATA}

Provide a professional, concise answer. If you cannot find specific information, say so politely."""

            gpt_answer = gpt_service.get_completion(gpt_prompt, max_tokens=200, temperature=0.3)
            
            if gpt_answer and not gpt_answer.startswith("[Error:"):
                answer_text = gpt_answer
                confidence = 0.85  # Set higher confidence for GPT responses
                answer_source = "gpt_fallback"
                logger.info("Successfully used GPT fallback")
            else:
                logger.warning("GPT fallback failed or returned error")
                
        except Exception as e:
            logger.error(f"GPT fallback error: {e}")
            # Continue with the original QA model answer
    
    db_ops = DatabaseOperations(db)
    question_id = db_ops.log_question(question.text)
    answer_id = db_ops.log_answer(question_id, answer_text, answer_source, confidence)
    
    return {
        "question": question.text,
        "answer": answer_text,
        "confidence": confidence,
        "answer_id": answer_id
    }

@app.post("/feedback",
    summary="Submit Feedback",
    description="""
    Submit feedback on an answer to help improve the system.
    
    Feedback is used to:
    * Train and improve the AI model
    * Identify areas for improvement
    * Measure user satisfaction
    """,
    response_description="Confirmation that feedback was recorded"
)
async def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    """Submit feedback on an answer."""
    try:
        logger.info(f"Feedback received for answer_id: {feedback.answer_id}")
        
        db_ops = DatabaseOperations(db)
        
        feedback_obj = db_ops.store_feedback(
            answer_id=feedback.answer_id,
            score=feedback.score,
            was_helpful=feedback.was_helpful,
            comment=feedback.comment
        )
        
        logger.info(f"Feedback stored with ID: {feedback_obj.id}")
        
        return {
            "status": "success",
            "message": "Thank you for your feedback!",
            "feedback_id": feedback_obj.id
        }
        
    except Exception as e:
        logger.error(f"Error in submit_feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 