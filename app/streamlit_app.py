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
st.set_page_config(
    page_title="Frank's Candidate Concierge",
    page_icon="📋",
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
    .linkedin-button-text {
        display: none;
    }
    .linkedin-button {
        padding: 6px;
    }
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

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0

# Display previous messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input Handling ---
def handle_user_input(prompt=None):
    """Process user input, call API, and update chat."""
    user_question = prompt if prompt else st.session_state.get("chat_input", "")
    
    if user_question:
        st.session_state.question_count += 1
        
        # Add user question to chat history
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
            
        # Get answer from API and display it
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, confidence = get_api_answer(user_question)
                
                # Add a small delay for a more natural feel
                time.sleep(0.5)
                
                response_text = answer
                if DEBUG_MODE:
                    response_text += f"\n\n*(Confidence: {confidence:.2f})*"
                
                st.markdown(response_text)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # Clear the input box after submission if using the text_input
        if not prompt and "chat_input" in st.session_state:
             st.session_state.chat_input = ""

# User input form at the bottom
st.chat_input("Ask a question about Frank's qualifications:", key="chat_input", on_submit=handle_user_input)

# --- Example Questions and Tips ---
st.markdown("---")
st.markdown("#### Example Questions")

# Use a responsive grid for example questions
cols = st.columns([1, 1, 1])
example_questions = [
    "What is Frank's current role?",
    "What certifications does Frank have?",
    "What are Frank's technical skills?"
]

for i, col in enumerate(cols):
    if col.button(example_questions[i], use_container_width=True):
        handle_user_input(prompt=example_questions[i])

st.markdown("""
<div class="tips-container">
    <h4>💡 Tips:</h4>
    <ul>
        <li><b>Be specific:</b> Ask about particular roles, skills, or experiences (e.g., "What Azure certifications does Frank have?")</li>
        <li><b>Use the examples:</b> Click the sample questions above</li>
        <li><b>Try different phrasings:</b> If you don't get the answer you need, rephrase your question</li>
    </ul>
</div>
""", unsafe_allow_html=True)

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

# Mobile-friendly sample questions (shown only on mobile)
st.markdown("""
<style>
.mobile-questions {
    display: none;
}

.mobile-questions-container {
    display: none;
}

@media (max-width: 768px) {
    .mobile-questions {
        display: block;
        margin: 20px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
        border-left: 4px solid #FFD700;
    }
    
    .mobile-questions-container {
        display: block;
    }
    
    .mobile-questions h4 {
        margin-top: 0;
        color: #333;
        font-size: 16px;
    }
    
    /* Hide sidebar on mobile */
    .css-1d391kg {
        display: none !important;
    }
    
    /* Hide sidebar toggle button on mobile */
    .css-1y4p8pa {
        display: none !important;
    }
    
    /* Adjust main content on mobile when sidebar is hidden */
    .css-18e3th9 {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: 0 !important;
    }
    
    /* Ensure full width usage on mobile */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
}

/* Desktop: hide mobile questions completely */
@media (min-width: 769px) {
    .mobile-questions-container {
        display: none !important;
    }
    
    /* Also hide by targeting the specific container div */
    div[data-testid="column"] .mobile-questions-container {
        display: none !important;
    }
    
    /* Target the buttons more specifically */
    .mobile-questions-container .stButton {
        display: none !important;
    }
    
    /* Ensure the entire section is hidden */
    .element-container:has(.mobile-questions-container) {
        display: none !important;
    }
}

/* Remove any unwanted lines/borders */
.element-container:has(.mobile-questions-container) + .element-container hr {
    display: none !important;
}

/* Remove any horizontal rules that might appear */
hr {
    display: none !important;
}

/* Ensure no borders appear after main content */
.main .block-container::after {
    border: none !important;
}

/* Remove bottom borders from sections */
.element-container {
    border-bottom: none !important;
}

/* Make Ask button consistent golden color on all devices */
.stButton button[kind="primary"] {
    background-color: #FFD700 !important;
    color: #333 !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3) !important;
    transition: all 0.2s ease !important;
}

.stButton button[kind="primary"]:hover {
    background-color: #FFA500 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4) !important;
}

.stButton button[kind="primary"]:active {
    background-color: #FF8C00 !important;
    transform: translateY(0) !important;
}
</style>

""", unsafe_allow_html=True)

# Add mobile quick questions with a more reliable approach
st.markdown("""
<style>
/* Mobile quick questions - only show on mobile */
@media (max-width: 768px) {
    .mobile-questions-section {
        display: block !important;
        margin: 20px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
        border-left: 4px solid #FFD700;
    }
    
    .mobile-questions-section h4 {
        margin-top: 0;
        margin-bottom: 10px;
        color: #333;
        font-size: 16px;
    }
    
    .mobile-questions-section p {
        margin: 5px 0 15px 0;
        font-size: 13px;
        color: #666;
    }
}

/* Hide on desktop */
@media (min-width: 769px) {
    .mobile-questions-section {
        display: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Create mobile questions container
st.markdown("""
<div class="mobile-questions-section">
    <h4>💡 Quick Questions</h4>
    <p>Tap a question to get started:</p>
</div>
""", unsafe_allow_html=True)

# Add the actual mobile question buttons
mobile_questions = [
    "What is Frank's current role?",
    "What certifications does Frank have?", 
    "What are Frank's technical skills?"
]

# Create columns for mobile layout
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button(mobile_questions[0], key="mob_q1", help="Click to ask this question", use_container_width=True):
        st.session_state.question = mobile_questions[0]
        st.rerun()

with col2:  
    if st.button(mobile_questions[1], key="mob_q2", help="Click to ask this question", use_container_width=True):
        st.session_state.question = mobile_questions[1]
        st.rerun()

with col3:
    if st.button(mobile_questions[2], key="mob_q3", help="Click to ask this question", use_container_width=True):
        st.session_state.question = mobile_questions[2]
        st.rerun()

# Hide the buttons on desktop using CSS
st.markdown("""
<style>
@media (min-width: 769px) {
    /* Hide the button columns on desktop */
    div[data-testid="column"]:has(button[title*="What is Frank's current role"]),
    div[data-testid="column"]:has(button[title*="What certifications does Frank have"]),
    div[data-testid="column"]:has(button[title*="What are Frank's technical skills"]) {
        display: none !important;
    }
}

/* Make mobile buttons look better */
@media (max-width: 768px) {
    .mobile-questions-section + div[data-testid="column"] button {
        font-size: 12px !important;
        padding: 8px 4px !important;
        height: auto !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Add a footer with instructions (removed the line)
st.markdown("""
💡 **Tips:**
- **Be specific**: Ask about particular roles, skills, or experiences (e.g., "What Azure certifications does Frank have?")
- **Use the examples**: Click the sample questions above (mobile) or in the sidebar (desktop)
- **Try different phrasings**: If you don't get the answer you need, rephrase your question
- **Ask about anything**: Technical skills, work history, certifications, education, and projects
""")

# Debug info section - only show if debug mode is enabled
if DEBUG_MODE:
    with st.expander("🐛 Debug Info"):
        st.write(f"Debug Mode: {DEBUG_MODE}")
        st.write(f"Model Available: {MODEL_AVAILABLE}")
        st.write(f"Session state keys: {list(st.session_state.keys())}")
        if st.button("Clear session state"):
            st.session_state.clear()
            st.rerun() 