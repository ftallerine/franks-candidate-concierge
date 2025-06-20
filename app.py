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
    
    # Job History
    if any(term in q for term in ["last job", "previous job", "past job", "former job"]):
        past_jobs = [exp for exp in RESUME_DATA["professional_experience"] if exp["status"] == "Past"]
        if past_jobs:
            # The jobs are in reverse-chronological order in resume_data.py
            last_job = past_jobs[0]
            return f"Frank's most recent previous job was as a {last_job['role']} at {last_job['company']}.", 1.0
        else:
            return "I couldn't find information about Frank's past jobs, but I can tell you about his current one.", 0.6

    # Certifications
    if any(term in q for term in ["certification", "certified", "cert"]):
        certs = [f"• {cert['name']} ({cert['issuer']})" for cert in RESUME_DATA["certifications"]]
        return "Frank holds the following certifications:\n" + "\n".join(certs), 1.0
    
    # Current role
    if any(term in q for term in ["current role", "current position", "current job", "job", "role", "work", "do for work", "do for a living"]):
        current_job = next((exp for exp in RESUME_DATA["professional_experience"] if exp["status"] == "Current"), None)
        if current_job:
            return f"Frank's current role is {current_job['role']} at {current_job['company']}.", 1.0
        return "I couldn't find Frank's current role.", 0.5

    # Location
    if any(term in q for term in ["where", "location", "based", "live", "located", "from"]):
        return f"Frank is located in {RESUME_DATA['contact_information']['location']}.", 1.0
    
    # Contact
    if any(term in q for term in ["contact", "email", "reach", "get in touch"]):
        contact = RESUME_DATA["contact_information"]
        return f"You can contact Frank via email at {contact['email']}. You can also find him on LinkedIn: {contact['linkedin']}", 1.0
    
    # Skills
    if any(term in q for term in ["skill", "technology", "tool", "tech", "know", "can do", "expertise", "proficiency"]):
        skills_data = RESUME_DATA["skills_and_technologies"]
        if "cloud" in q or "azure" in q:
            skills = skills_data["cloud_and_net"]
            return f"Frank's cloud and .NET skills include:\n" + "\n".join(f"• {skill}" for skill in skills), 1.0
        elif "programming" in q or "language" in q or "code" in q:
            skills = skills_data["programming_languages"]
            return f"Frank's programming languages include:\n" + "\n".join(f"• {skill}" for skill in skills), 1.0
        elif "tool" in q:
            skills = skills_data["tools"]
            return f"Frank's technical tools expertise includes:\n" + "\n".join(f"• {skill}" for skill in skills), 1.0
        elif "business" in q:
            skills = skills_data["business_analysis"] + skills_data["agile_and_scrum"]
            return f"Frank's business and process skills include:\n" + "\n".join(f"• {skill}" for skill in skills), 1.0
        else:
            # All skills
            all_skills = {
                "Cloud & .NET": skills_data["cloud_and_net"],
                "Programming Languages": skills_data["programming_languages"],
                "Tools": skills_data["tools"],
                "Business & Agile": skills_data["business_analysis"] + skills_data["agile_and_scrum"],
                "Soft Skills": skills_data["soft_skills"]
            }
            response = "Frank's skills by category:\n\n"
            for category, skills in all_skills.items():
                response += f"{category}:\n" + "\n".join(f"• {skill}" for skill in skills) + "\n\n"
            return response.strip(), 1.0
    
    # Experience
    if any(term in q for term in ["experience", "how long", "years", "time"]):
        exp = RESUME_DATA["experience_highlights"]
        if "business" in q or "ba" in q:
            return f"Frank has {exp['total_ba_experience']} of Business Analysis experience.", 1.0
        elif "azure" in q:
            return f"Frank has {exp['azure_experience']} of Azure experience.", 1.0
        elif "sql" in q:
            return f"Frank has {exp['sql_experience']} of SQL experience.", 1.0
        elif "scrum" in q:
            return f"Frank has {exp['scrum_master_experience']} of Scrum experience.", 1.0
        else:
            return f"Frank's experience includes:\n• Business Analysis: {exp['total_ba_experience']}\n• Scrum Master: {exp['scrum_master_experience']}\n• Azure: {exp['azure_experience']}\n• SQL: {exp['sql_experience']}", 1.0
    
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