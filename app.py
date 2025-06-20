"""
Standalone version of Frank's Candidate Concierge API
No database dependencies, using only structured data responses
"""

import sys
import os

# This block MUST come BEFORE any `from src...` imports.
# It fixes the Python path to be able to find the `src` module in deployment.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json

from src.models.resume_data import RESUME_DATA
from src.models.gpt_service import GPTService

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

# Initialize FastAPI
app = FastAPI(
    title="Frank's Candidate Concierge API",
    description="""
    An API for answering questions about Frank's professional experience and qualifications.
    
    ## Available Topics
    * Certifications
    * Current Role
    * Skills (Cloud, Programming, Tools, Business)
    * Experience
    * Contact Information
    
    ## Example Questions
    * "What certifications do you have?"
    * "What is your current role?"
    * "What are your cloud skills?"
    * "How much experience do you have with Azure?"
    * "Where are you located?"
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Frank Tallerine",
        "email": "REDACTED_EMAIL@example.com ",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GPT Service for fallback
try:
    gpt_service = GPTService()
    GPT_ENABLED = True
except ValueError:
    gpt_service = None
    GPT_ENABLED = False
    logger.warning("OPENAI_API_KEY not set. GPT fallback is disabled.")

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

def get_structured_answer(question: str) -> tuple[str, float]:
    """Get answer from structured data based on question type."""
    # Normalize question text to handle pronouns consistently
    q = question.lower()
    q = q.replace("your", "frank's")
    q = q.replace("you", "frank")
    q = q.replace("his", "frank's")
    q = q.replace("he", "frank")
    q = q.replace("my", "frank's")
    q = q.replace("i", "frank")
    
    # Fallback to GPT if no structured answer is found
    if GPT_ENABLED:
        logger.info("No structured answer found. Falling back to GPT.")
        # Create a detailed prompt for the GPT model
        prompt = f"""
        You are an AI assistant answering questions about a job candidate named Frank based on his resume data.
        Answer the following question concisely, as if you are Frank's helpful assistant.
        Do not mention that you are using his resume data.
        If the question is unrelated to Frank's professional background, politely decline to answer.

        Resume Data:
        {json.dumps(RESUME_DATA, indent=2)}

        Question: "{question}"

        Answer:
        """
        try:
            answer = gpt_service.get_completion(prompt)
            return answer, 0.7  # Lower confidence for AI-generated answers
        except Exception as e:
            logger.error(f"Error during GPT fallback: {e}")
            return "I encountered an error trying to answer your question. Please try again.", 0.0

    return "I can provide information about Frank's certifications, skills, experience, current role, or contact details. Please ask about any of these topics.", 0.5

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

@app.post("/ask",
    response_model=Answer,
    summary="Ask a Question",
    description="""
    Ask a question about Frank's qualifications, experience, or skills.
    
    The API will analyze your question and provide a relevant answer based on Frank's:
    * Professional certifications
    * Current role and responsibilities
    * Technical skills (Cloud, Programming, Tools)
    * Business skills
    * Years of experience
    * Contact information
    """,
    response_description="The answer to your question with a confidence score"
)
async def ask_question(question: Question):
    """Get an answer to a question about Frank's resume."""
    try:
        logger.info(f"Question received: {question.text}")
        
        # Get answer from structured data
        answer_text, confidence = get_structured_answer(question.text)
        
        logger.info(f"Answer generated - Confidence: {confidence}")
        
        return Answer(
            answer=answer_text,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 