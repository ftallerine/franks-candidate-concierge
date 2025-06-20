# Streamlit app for Frank's Candidate Concierge
# Professional resume Q&A assistant - Updated for mobile compatibility

import streamlit as st
import sys
import os
from pathlib import Path
import time
import logging
from datetime import datetime
import requests  # Import the requests library to make API calls

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
concierge_icon_path = os.path.join(current_dir, "static", "images", "concierge_icon.png")
st.set_page_config(
    page_title="Frank's Candidate Concierge",
    page_icon=concierge_icon_path if os.path.exists(concierge_icon_path) else "📋",
    layout="wide"
)

logger.info("Streamlit app started")

# --- New Function to Call the Backend API ---
API_URL = "https://franks-candidate-concierge.onrender.com/ask"

@st.cache_data(ttl=300)  # Cache responses for 5 minutes
def get_api_answer(question: str) -> tuple[str, float]:
    """
    Calls the backend API to get an answer to a question.
    Returns the answer and confidence score.
    """
    if not question:
        return "", 0.0

    try:
        logger.info(f"Calling API with question: '{question}'")
        payload = {"text": question}
        response = requests.post(API_URL, json=payload, timeout=30)
        
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()
        answer = data.get("answer", "I could not find an answer.")
        confidence = data.get("confidence", 0.0)
        
        logger.info(f"API returned answer with confidence {confidence}")
        return answer, confidence

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return "Sorry, I'm having trouble connecting to my knowledge base. Please try again in a moment.", 0.0
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return "An unexpected error occurred while fetching the answer.", 0.0

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
            width: 160px !important;
            height: 160px !important;
            border-radius: 50% !important;
            object-fit: cover !important;
            border: 4px solid #ffffff !important;
            margin: 15px auto !important;
            display: block !important;
        }
        .stImage {
            text-align: center !important;
            display: flex !important;
            justify-content: center !important;
        }
        .linkedin-button-text {
            display: none; /* Hide text by default */
        }
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .header-container {
                flex-direction: column;
                align-items: center;
                height: auto;
                gap: 15px;
            }
            .header-title {
                font-size: 2rem;
                text-align: center;
            }
            .linkedin-button {
                padding: 6px;
            }
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

# Responsive header layout
st.markdown("""
<style>
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 80px;
    margin-bottom: 1rem;
}

.header-title {
    margin: 0;
    font-size: 3rem;
    line-height: 1;
}

.linkedin-button {
    background: linear-gradient(135deg, #FFD700, #FFA500, #FF8C00);
    border-radius: 6px;
    padding: 8px;
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    align-items: center;
    cursor: pointer;
    text-decoration: none;
}

.linkedin-button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
}

.linkedin-button-text {
    color: white;
    font-weight: 600;
    font-size: 14px;
    margin-left: 8px;
}
</style>

<div class="header-container">
    <h1 class="header-title">Frank's Candidate Concierge</h1>
    <div>
        <a href="https://www.linkedin.com/in/frank-tallerine/" target="_blank" class="linkedin-button">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
            <span class="linkedin-button-text">Connect on LinkedIn</span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Welcome to Frank's Candidate Concierge! I'm your AI assistant, ready to answer questions about Frank's professional experience, 
skills, certifications, and more. Feel free to ask me anything about Frank's qualifications!
""")

# Predefined answers for common questions
PREDEFINED_ANSWERS = {
    "What is Frank's current role?": "Frank's current role is a Technical Business Analyst at The Marker Group.",
    "What certifications does Frank have?": """Frank has the following certifications:

1. Certified Scrum Master (CSM) obtained in 2019 from Scrum Alliance (Active)
2. Microsoft Certified: Azure Administrator Associate obtained in 2021 from Microsoft (Active)  
3. Microsoft Certified: Azure Fundamentals obtained in 2020 from Microsoft (Active)""",
    "What are Frank's technical skills?": """Frank's technical skills include:

**Programming & Development:**
- C#, .NET Framework, .NET Core
- Python, R, SQL
- JavaScript, HTML, CSS
- PowerShell scripting

**Cloud & Azure:**
- Azure Administration
- Azure DevOps
- Cloud architecture and migration

**Data & Analytics:**
- SQL Server, MySQL, PostgreSQL
- Power BI, Tableau
- Data analysis and visualization
- Machine Learning basics

**Agile & Project Management:**
- Scrum methodology
- Jira, Azure DevOps
- Requirements gathering
- Stakeholder management""",
    "Tell me about Frank's experience with Agile/Scrum methodologies": """Frank has extensive Agile/Scrum experience:

**Scrum Master Certification:**
- Certified Scrum Master (CSM) since 2019 - 5+ years active
- Led Agile process optimization at The Marker Group

**Practical Implementation:**
- Implemented daily standups and sprint planning
- Increased team velocity by 75% (from ~12 to 20-25 stories per 2-week sprint)
- Managed cross-functional teams of 5-10 members
- Conducted sprint retrospectives and backlog refinement

**Agile Tools & Processes:**
- Azure DevOps for sprint management
- User story creation and estimation
- Release planning and deployment coordination
- Continuous improvement through retrospectives""",
    "What is Frank's experience with stakeholder management?": """Frank excels in stakeholder management with proven results:

**Track Record:**
- Achieved 85% stakeholder approval rate (improved by 55%)
- Conducted requirement analysis with diverse stakeholder groups
- Bridged technical and business teams through precise communication

**Key Skills:**
- Requirements gathering and documentation
- Translating complex technical concepts for non-technical stakeholders
- Conflict resolution and negotiation
- Cross-functional collaboration across departments

**Communication Excellence:**
- Delivered precise, high-level communication to align teams
- Presented complex AI methodologies to stakeholders with clarity
- Built consensus through effective facilitation and active listening""",
    "Can you describe Frank's most significant project achievements?": """Frank's most significant achievements include:

**Process Optimization at The Marker Group:**
- Increased team velocity by 75% through Agile implementation
- Reduced deployment errors by 40% via Azure DevOps optimization
- Enabled 3-5 weekly deployments (up from 1-2 monthly)

**Data-Driven Decision Making:**
- Built 15+ Power BI dashboards for real-time business insights
- Enhanced decision-making accuracy through data visualization
- Improved financial reporting through database design

**AI/ML Innovation:**
- Developed Medical Record Annotation NER Model using spaCy
- Cut data processing time by 25% through pipeline optimization
- Created scalable backend with webhook and API integration

**Business Impact:**
- Achieved 85% stakeholder approval rate (55% improvement)
- Reduced post-release defects through quality assurance leadership
- Boosted on-time job completion by 20% through scheduling optimization"""
}

# Initialize session state for the Q&A section
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'current_answer' not in st.session_state:
    st.session_state.current_answer = ""
if 'input_text' not in st.session_state:
    # Set a default question for the first view
    st.session_state.input_text = "What is Frank's current role?"
    st.session_state.current_question = st.session_state.input_text
    st.session_state.current_answer = PREDEFINED_ANSWERS[st.session_state.input_text]

# --- Main Q&A Interaction Area ---

# Function to handle question submission
def handle_submission():
    """Process the question from the text input."""
    question = st.session_state.get("text_input_area", "")
    if question:
        st.session_state.input_text = question
        st.session_state.current_question = question
        # Check for predefined answers first
        if question in PREDEFINED_ANSWERS:
            st.session_state.current_answer = PREDEFINED_ANSWERS[question]
            debug_print(f"Used predefined answer for: {question}")
        else:
            # Call API for other questions
            with st.spinner("Thinking..."):
                answer, confidence = get_api_answer(question)
                st.session_state.current_answer = answer
                if DEBUG_MODE:
                    st.session_state.current_answer += f"\\n\\n*(Confidence: {confidence:.2f})*"

# Function to handle button clicks for predefined questions
def handle_button_click(question):
    """Update state when a predefined question button is clicked."""
    st.session_state.input_text = question
    st.session_state.current_question = question
    st.session_state.current_answer = PREDEFINED_ANSWERS[question]
    debug_print(f"Used predefined answer for: {question}")

# --- UI Layout ---

# Input bar at the top
st.text_input(
    "Ask a question about Frank's qualifications:",
    key="text_input_area",
    value=st.session_state.input_text,
    on_change=handle_submission,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True) # Add some space

# The single, updating Q&A display section
if st.session_state.current_question:
    with st.container():
        st.chat_message("user").markdown(st.session_state.current_question)
        st.chat_message("assistant").markdown(st.session_state.current_answer)

# --- Example Questions ---
st.markdown("---")
st.markdown("#### Or, click an example question to get started:")

# All 6 example questions in a responsive 2x3 grid
example_questions = [
    "What is Frank's current role?",
    "What certifications does Frank have?",
    "What are Frank's technical skills?",
    "Tell me about Frank's experience with Agile/Scrum methodologies",
    "What is Frank's experience with stakeholder management?",
    "Can you describe Frank's most significant project achievements?"
]

# Create a 2x3 grid for the buttons
for i in range(0, len(example_questions), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(example_questions):
            question = example_questions[i+j]
            cols[j].button(
                question, 
                use_container_width=True, 
                key=f"q_{i+j}",
                on_click=handle_button_click,
                args=(question,)
            )

st.markdown("---")

# Sidebar content with headshot and professional summary
with st.sidebar:
    # --- Headshot Image ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "static", "images", "headshot.png")
    if os.path.exists(image_path):
        st.image(image_path, width=160, use_column_width=False)
        logger.info(f"Successfully loaded headshot in sidebar: {image_path}")
    else:
        logger.warning(f"Headshot image not found at {image_path}")

    # --- Professional Summary ---
    st.markdown("### Professional Summary")
    st.markdown("""
    Certified Scrum Master with over 6 years of experience as a Technical Business Analyst, excelling in Agile frameworks and AI-driven insights within .NET environments. Adept at delivering precise, high-level communication and devising creative solutions.
    """)

    st.markdown("---")
    
    # --- Contact Information ---
    st.markdown("### Contact")
    st.markdown("""
    - **Email:** REDACTED_EMAIL@example.com 
    - **Location:** Montgomery, TX
    """)

# Debug section (only shown if DEBUG_MODE is enabled)
if DEBUG_MODE:
    st.markdown("---")
    st.markdown("#### Debug Information")
    with st.expander("Debug Details"):
        st.write(f"Debug Mode: {DEBUG_MODE}")
        st.write(f"Session state keys: {list(st.session_state.keys())}")
        if st.button("Clear session state"):
            st.session_state.clear()
            st.experimental_rerun() 