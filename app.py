"""
Standalone version of Frank's Candidate Concierge API
No database dependencies, using only structured data responses
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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
    
    # Certifications
    if any(term in q for term in ["certification", "certified", "cert"]):
        return f"Frank holds the following certifications:\n" + "\n".join(f"• {cert}" for cert in RESUME_DATA["certifications"]), 1.0
    
    # Current role
    if any(term in q for term in ["current role", "current position", "current job", "work", "do for work", "do for a living"]):
        return f"Frank's current role is {RESUME_DATA['current_role']}", 1.0
    
    # Location
    if any(term in q for term in ["where", "location", "based", "live", "located", "from"]):
        return f"Frank is located in {RESUME_DATA['contact']['location']}", 1.0
    
    # Contact
    if any(term in q for term in ["contact", "email", "reach", "get in touch"]):
        contact = RESUME_DATA["contact"]
        return f"You can contact Frank via email at {contact['email']}", 1.0
    
    # Skills
    if any(term in q for term in ["skill", "technology", "tool", "tech", "know", "can do", "expertise", "proficiency"]):
        if "cloud" in q or "azure" in q:
            skills = RESUME_DATA["skills"]["cloud"]
            return f"Frank's cloud and Azure skills include:\n" + "\n".join(f"• {skill}" for skill in skills), 1.0
        elif "programming" in q or "language" in q or "code" in q:
            skills = RESUME_DATA["skills"]["programming"]
            return f"Frank's programming skills include:\n" + "\n".join(f"• {skill}" for skill in skills), 1.0
        elif "tool" in q:
            skills = RESUME_DATA["skills"]["tools"]
            return f"Frank's technical tools expertise includes:\n" + "\n".join(f"• {skill}" for skill in skills), 1.0
        elif "business" in q:
            skills = RESUME_DATA["skills"]["business"]
            return f"Frank's business and process skills include:\n" + "\n".join(f"• {skill}" for skill in skills), 1.0
        else:
            # All skills
            all_skills = {
                "Cloud & Azure": RESUME_DATA["skills"]["cloud"],
                "Programming": RESUME_DATA["skills"]["programming"],
                "Tools": RESUME_DATA["skills"]["tools"],
                "Business": RESUME_DATA["skills"]["business"]
            }
            response = "Frank's skills by category:\n\n"
            for category, skills in all_skills.items():
                response += f"{category}:\n" + "\n".join(f"• {skill}" for skill in skills) + "\n\n"
            return response.strip(), 1.0
    
    # Experience
    if any(term in q for term in ["experience", "how long", "years", "time"]):
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