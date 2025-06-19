"""
Standalone version of Frank's Candidate Concierge API
No database dependencies, using only structured data responses
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import logging

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
    description="API for answering questions about Frank's resume",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured resume data
RESUME_DATA = {
    "contact": {
        "name": "Frank Tallerine",
        "location": "Montgomery, TX",
        "email": "REDACTED_EMAIL@example.com "
    },
    "current_role": "Technical Business Analyst at The Marker Group",
    "certifications": [
        "Azure Administrator Associate (AZ-104)",
        "Professional Scrum Master I (PSM I)",
        "Azure Fundamentals (AZ-900)"
    ],
    "skills": {
        "cloud": ["Azure", "Azure DevOps", "Azure Functions", "Azure SQL"],
        "programming": ["Python", "SQL", "JavaScript", "TypeScript"],
        "tools": ["Power BI", "JIRA", "Git", "VS Code"],
        "business": ["Agile", "Scrum", "Business Analysis", "Requirements Gathering"]
    },
    "experience": {
        "total_ba": "6+ years",
        "azure": "3+ years",
        "sql": "3+ years",
        "scrum": "4+ years"
    }
}

class Question(BaseModel):
    text: str

class Answer(BaseModel):
    answer: str
    confidence: float

def get_structured_answer(question: str) -> tuple[str, float]:
    """Get answer from structured data based on question type."""
    q = question.lower()
    
    # Certifications
    if any(term in q for term in ["certification", "certified", "cert"]):
        return f"Frank holds the following certifications:\n" + "\n".join(f"• {cert}" for cert in RESUME_DATA["certifications"]), 1.0
    
    # Current role
    if any(term in q for term in ["current role", "current position", "current job"]):
        return f"Frank's current role is {RESUME_DATA['current_role']}", 1.0
    
    # Location
    if any(term in q for term in ["where", "location", "based", "live"]):
        return f"Frank is located in {RESUME_DATA['contact']['location']}", 1.0
    
    # Contact
    if any(term in q for term in ["contact", "email", "reach"]):
        contact = RESUME_DATA["contact"]
        return f"You can contact Frank via email at {contact['email']}", 1.0
    
    # Skills
    if "skill" in q or "technology" in q or "tool" in q:
        if "cloud" in q or "azure" in q:
            skills = RESUME_DATA["skills"]["cloud"]
        elif "programming" in q or "language" in q or "code" in q:
            skills = RESUME_DATA["skills"]["programming"]
        elif "tool" in q:
            skills = RESUME_DATA["skills"]["tools"]
        elif "business" in q:
            skills = RESUME_DATA["skills"]["business"]
        else:
            # All skills
            skills = (
                RESUME_DATA["skills"]["cloud"] +
                RESUME_DATA["skills"]["programming"] +
                RESUME_DATA["skills"]["tools"] +
                RESUME_DATA["skills"]["business"]
            )
        return "Frank's relevant skills include:\n" + "\n".join(f"• {skill}" for skill in skills), 1.0
    
    # Experience
    if "experience" in q:
        if "business" in q or "ba" in q:
            return f"Frank has {RESUME_DATA['experience']['total_ba']} of Business Analysis experience.", 1.0
        elif "azure" in q:
            return f"Frank has {RESUME_DATA['experience']['azure']} of Azure experience.", 1.0
        elif "sql" in q:
            return f"Frank has {RESUME_DATA['experience']['sql']} of SQL experience.", 1.0
        elif "scrum" in q:
            return f"Frank has {RESUME_DATA['experience']['scrum']} of Scrum experience.", 1.0
        else:
            exp = RESUME_DATA["experience"]
            return f"Frank's experience includes:\n• Business Analysis: {exp['total_ba']}\n• Azure: {exp['azure']}\n• SQL: {exp['sql']}\n• Scrum: {exp['scrum']}", 1.0
    
    return "I'm not sure about that. Try asking about Frank's certifications, skills, experience, or current role.", 0.5

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
        
        # Get answer from structured data
        answer_text, confidence = get_structured_answer(question.text)
        
        logger.info(f"Answer generated - Confidence: {confidence}")
        
        return Answer(
            answer=answer_text,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 