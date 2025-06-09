import streamlit as st
import sys
import os
from pathlib import Path
import time
import logging
from datetime import datetime

# Add the project root to Python path so we can import from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Now import the QA model and resume data
try:
    from src.models.qa_model import QAModel
    from src.models.resume_data import RESUME_DATA
    MODEL_AVAILABLE = True
except ImportError as e:
    MODEL_AVAILABLE = False
    print(f"Model import failed: {e}")

# Debug Configuration - Secure toggle for debug UI
# Set DEBUG_MODE = False for production, True for development
DEBUG_MODE = os.getenv("STREAMLIT_DEBUG", "false").lower() == "true"

def debug_print(message, message_type="info"):
    """Conditionally display debug messages based on DEBUG_MODE"""
    if DEBUG_MODE:
        if message_type == "error":
            st.error(f"🐛 DEBUG: {message}")
        elif message_type == "warning":
            st.warning(f"🐛 DEBUG: {message}")
        else:
            st.write(f"🐛 DEBUG: {message}")

# Set up logging for Streamlit (Cloud-compatible)
try:
    # Try to create logs directory and file handler for local development
    os.makedirs('logs', exist_ok=True)
    handlers = [
        logging.FileHandler('logs/streamlit.log'),
        logging.StreamHandler()
    ]
except (OSError, PermissionError):
    # Fallback to console only for Streamlit Cloud deployment
    handlers = [logging.StreamHandler()]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# Configure the page
st.set_page_config(
    page_title="Frank's Candidate Concierge",
    page_icon="📋",
    layout="wide"
)

logger.info("Streamlit app started")

# Use Streamlit caching for model loading
@st.cache_resource(show_spinner=False)
def load_qa_model():
    """Load the QA model with caching to avoid reloading."""
    try:
        logger.info("Loading QA model with caching...")
        model = QAModel()
        logger.info("QA model loaded successfully")
        return model, True
    except Exception as e:
        logger.error(f"Failed to load QA model: {str(e)}")
        return None, False

# Simple Q&A fallback using structured data only
def get_simple_answer(question: str) -> tuple[str, float]:
    """Get answer using only structured data, without ML model."""
    if not MODEL_AVAILABLE:
        return "Model not available. Please check the installation.", 0.0
        
    q_lower = question.lower()
    
    # Simple keyword-based matching for common questions
    predefined_answers = {
        "current role": "Technical Business Analyst at The Marker Group (September 2018-Present)",
        "certifications": "Certified Scrum Master (CSM) - Scrum Alliance, 2019; Microsoft Certified: Azure Administrator Associate - Microsoft, 2021; Microsoft Certified: Azure Fundamentals - Microsoft, 2020",
        "technical skills": "Azure (3+ years), Azure DevOps (3+ years), SQL (3+ years), Power BI, Python, Git, Visual Studio, Office 365 (5+ years), PowerShell",
        "programming languages": "Python, C++, JavaScript, HTML, CSS, PowerShell",
        "azure experience": "3+ years since 2021. Azure DevOps releases, reduced deployment errors by 40%, enabled 3-5 weekly deployments. Azure Administrator Associate certified.",
        "education": "Bachelor of Mathematics and Bachelor of Finance from Texas State University, San Marcos, TX. Graduated Cum Laude in 2016.",
        "experience": "6+ years as Technical Business Analyst. Led Agile process optimization, increased team velocity by 75%, conducted stakeholder analysis.",
        "contact": "Email: REDACTED_EMAIL@example.com , LinkedIn: https://www.linkedin.com/in/frank-tallerine/, Location: Montgomery, TX"
    }
    
    # Find matching answer
    for key, answer in predefined_answers.items():
        if key in q_lower:
            return answer, 1.0
    
    # Try to extract from RESUME_DATA if available
    try:
        # Current role
        if any(term in q_lower for term in ["current", "role", "position", "job"]):
            current_job = RESUME_DATA["professional_experience"][0]
            return f"{current_job['title']} at {current_job['company']} ({current_job['dates']})", 1.0
            
        # Certifications
        if "cert" in q_lower:
            certs = []
            for cert in RESUME_DATA["certifications"]:
                certs.append(f"{cert['name']} ({cert['issuer']}, {cert['year_obtained']})")
            return "; ".join(certs), 1.0
            
        # Skills
        if any(term in q_lower for term in ["skill", "technology", "tech"]):
            skills = []
            skills.extend(RESUME_DATA["skills_and_technologies"]["cloud_and_net"])
            skills.extend(RESUME_DATA["skills_and_technologies"]["tools"][:5])  # First 5 tools
            return ", ".join(skills), 1.0
            
        # Programming languages
        if "programming" in q_lower and "language" in q_lower:
            return ", ".join(RESUME_DATA["skills_and_technologies"]["programming_languages"]), 1.0
            
        # Azure
        if "azure" in q_lower:
            return "3+ years experience with Azure and Azure DevOps. Microsoft Certified: Azure Administrator Associate (2021), Azure Fundamentals (2020). Managed Azure DevOps releases, reducing deployment errors by 40%.", 1.0
            
        # Education
        if any(term in q_lower for term in ["education", "degree", "university", "college"]):
            edu = RESUME_DATA["education"]
            return f"{', '.join(edu['degrees'])} from {edu['university']}, graduated {edu['honors']} in {edu['graduation_year']}", 1.0
            
        # Contact
        if any(term in q_lower for term in ["contact", "email", "linkedin"]):
            contact = RESUME_DATA["contact_information"]
            return f"Email: {contact['email']}, LinkedIn: {contact['linkedin']}, Location: {contact['location']}", 1.0
            
    except Exception as e:
        logger.error(f"Error in simple answer extraction: {str(e)}")
    
    return "", 0.0

# Load external CSS file for cleaner code organization
def load_css():
    """Load the external CSS file for styling."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "static", "css", "styles.css")
    
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        logger.info("Successfully loaded external CSS file")
    except Exception as e:
        logger.error(f"Error loading CSS file: {e}")
        # Fallback inline CSS for critical styling
        st.markdown("""
        <style>
        div.stImage > img {
            width: 200px !important;
            height: 200px !important;
            border-radius: 50% !important;
            object-fit: cover !important;
            border: 6px solid #ffffff !important;
            margin: 20px auto !important;
            display: block !important;
        }
        .stImage {
            text-align: center !important;
            display: flex !important;
            justify-content: center !important;
        }
        </style>
        """, unsafe_allow_html=True)

# Apply the professional styling
load_css()

# Professional headshot setup
current_dir = os.path.dirname(os.path.abspath(__file__))
image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
image_path = None

# Check for the new headshot.png first
headshot_png = os.path.join(current_dir, "static", "images", "headshot.png")
if os.path.exists(headshot_png):
    image_path = headshot_png
else:
    # Fallback to original naming pattern
    for ext in image_extensions:
        potential_path = os.path.join(current_dir, "static", "images", f"frank_headshot{ext}")
        if os.path.exists(potential_path):
            image_path = potential_path
            break

# Simplified header layout - title with emoji icon
st.markdown("""
<div style="display: flex; align-items: center; height: 80px; margin-bottom: 1rem;">
    <h1 style="margin: 0; font-size: 3rem; line-height: 1;">Frank's Candidate Concierge</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Welcome to Frank's Candidate Concierge! I'm your AI assistant, ready to answer questions about Frank's professional experience, 
skills, certifications, and more. Feel free to ask me anything about Frank's qualifications!
""")

# Initialize the AI model in the background
if MODEL_AVAILABLE:
    # Try to load the full AI model
    with st.spinner("🔄 Loading AI model... This may take a moment on first run."):
        qa_model, model_loaded = load_qa_model()
    
    if model_loaded:
        st.success("✅ AI model loaded! Ready to answer detailed questions.")
    else:
        st.warning("⚠️ AI model couldn't load, but I can still answer common questions using structured data.")
        qa_model = None
else:
    st.warning("⚠️ AI model unavailable, but I can still answer common questions using structured data.")
    qa_model = None

# Sidebar with profile and example questions
with st.sidebar:
    # Professional headshot at top of sidebar
    try:
        if image_path:
            st.image(image_path, use_container_width=True)
            logger.info(f"Successfully loaded headshot in sidebar: {image_path}")
        else:
            st.info("👔 Professional headshot")
            logger.warning("No headshot image found")
    except Exception as e:
        logger.error(f"Error loading headshot in sidebar: {e}")
        st.info("👔 Professional headshot")
    
    # Add some spacing
    st.write("")
    
    st.header("Example Questions")
    example_questions = [
        "What is Frank's current role?",
        "What certifications does Frank have?",
        "What are Frank's technical skills?",
        "What programming languages does Frank know?",
        "What is Frank's experience with Azure?",
        "What was Frank's role at The Marker Group?"
    ]
    
    for question in example_questions:
        if st.button(question):
            st.session_state.question = question

# Main interaction area
question = st.text_input("Ask a question about Frank's qualifications:", 
                        value=st.session_state.get("question", ""),
                        key="current_question")

if question:
    try:
        with st.spinner("🤔 Analyzing resume and generating response..."):
            answer = ""
            confidence = 0.0
            
            # Try full AI model first if available
            if qa_model:
                try:
                    answer, confidence = qa_model.answer_question(question)
                except Exception as e:
                    logger.error(f"AI model error: {str(e)}")
                    # Fall back to simple answers
                    answer, confidence = get_simple_answer(question)
            else:
                # Use simple structured data answers
                answer, confidence = get_simple_answer(question)
            
            if answer and confidence >= 0.5:
                # Format the answer properly for display
                formatted_answer = answer.replace('\n', '  \n')  # Double space + newline for markdown line breaks
                st.markdown(f"✅ **Answer:**  \n{formatted_answer}")
                
                # Show confidence and source for debugging
                if DEBUG_MODE:
                    source = "AI Model" if qa_model and confidence < 1.0 else "Structured Data"
                    st.write(f"Debug: Confidence = {confidence:.2f}, Source = {source}")
                    
            else:
                st.warning("I couldn't find a specific answer to that question. Please try rephrasing your question or use one of the example questions in the sidebar.")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        logger.error(f"Question processing error: {str(e)}")

# Add a footer with instructions
st.markdown("---")
st.markdown("""
💡 **Tips:**
- **Be specific**: Ask about particular roles, skills, or experiences (e.g., "What Azure certifications does Frank have?")
- **Use the examples**: Click the sample questions in the sidebar to get started quickly
- **Try different phrasings**: If you don't get the answer you need, rephrase your question
- **Ask about anything**: Technical skills, work history, certifications, education, and projects
""")

# Debug info section - only show if debug mode is enabled
if DEBUG_MODE:
    with st.expander("🐛 Debug Info"):
        st.write(f"Debug Mode: {DEBUG_MODE}")
        st.write(f"Model Available: {MODEL_AVAILABLE}")
        st.write(f"AI Model Loaded: {qa_model is not None}")
        st.write(f"Session state keys: {list(st.session_state.keys())}")
        if st.button("Clear session state"):
            st.session_state.clear()
            st.rerun() 