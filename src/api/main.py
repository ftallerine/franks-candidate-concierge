import os
os.makedirs("logs", exist_ok=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.models.qa_model import QAModel
from datetime import datetime
import logging

# Import database initialization
from startup import init_database

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

# Initialize database before creating the FastAPI app
init_database()

app = FastAPI(
    title="Frank's Candidate Concierge API",
    description="API for answering questions about Frank's resume using DistilBERT",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the QA model
qa_model = QAModel()

class Question(BaseModel):
    text: str

class Answer(BaseModel):
    answer: str
    confidence: float

@app.get("/")
async def root():
    return {"message": "Welcome to Frank's Candidate Concierge API"}

@app.get("/health")
async def health_check():
    """Simple health check."""
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    """Get an answer to a question about Frank's resume."""
    try:
        logger.info(f"Question received: {question.text}")
        
        # Get answer from QA model
        answer_text, confidence, source = qa_model.answer_question(question.text)
        
        logger.info(f"Answer generated - Confidence: {confidence}, Source: {source}")
        
        return Answer(
            answer=answer_text,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 