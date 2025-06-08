import streamlit as st
import requests
import json
import time
import os
import logging
from pathlib import Path
from datetime import datetime

# Debug Configuration - Secure toggle for debug UI
# Set DEBUG_MODE = False for production, True for development
DEBUG_MODE = os.getenv("STREAMLIT_DEBUG", "false").lower() == "true"

# Feedback Configuration - Toggle for feedback system  
# Set ENABLE_FEEDBACK = False for Streamlit-only deployment, True when backend is available
ENABLE_FEEDBACK = os.getenv("STREAMLIT_ENABLE_FEEDBACK", "false").lower() == "true"

def debug_print(message, message_type="info"):
    """Conditionally display debug messages based on DEBUG_MODE"""
    if DEBUG_MODE:
        if message_type == "error":
            st.error(f"🐛 DEBUG: {message}")
        elif message_type == "warning":
            st.warning(f"🐛 DEBUG: {message}")
        else:
            st.write(f"🐛 DEBUG: {message}")

# Set up logging for Streamlit
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/streamlit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configure the page
st.set_page_config(
    page_title="Frank's Candidate Concierge",
    page_icon="app/static/images/concierge_icon.png",
    layout="wide"
)

logger.info("Streamlit app started")

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

# Initialize session state for answer tracking
if 'current_answer_id' not in st.session_state:
    st.session_state.current_answer_id = None

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

# Function to check if API is ready (only when feedback is enabled)
def is_api_ready():
    if not ENABLE_FEEDBACK:
        return True  # Skip API check when feedback is disabled
    try:
        response = requests.get("http://localhost:8000")
        return response.status_code == 200
    except:
        return False

# Conditional backend initialization
if ENABLE_FEEDBACK and not is_api_ready():
    st.warning("Please wait while the system is being initialized...")
    
    # Create placeholders for loading elements
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    with progress_placeholder.container():
        progress_bar = st.progress(0)
    
    # Show progress simulation
    api_ready = False
    for i in range(100):
        # Simulate progress steps
        if i < 25:
            status_placeholder.text("Loading model...")
        elif i < 50:
            status_placeholder.text("Loading tokenizer...")
        elif i < 75:
            status_placeholder.text("Setting up QA pipeline...")
        else:
            status_placeholder.text("Loading resume data...")
        progress_bar.progress(i + 1)
        time.sleep(0.1)
        
        # Check if API is ready
        if is_api_ready():
            api_ready = True
            break
    
    # Clear loading elements
    progress_placeholder.empty()
    status_placeholder.empty()
            
    if api_ready or is_api_ready():
        st.success("✅ System initialized successfully! Ready to answer your questions.")
    else:
        st.error("❌ Failed to initialize the backend. Please refresh the page to try again.")
elif ENABLE_FEEDBACK:
    st.success("✅ Ready to answer questions!")
else:
    st.success("✅ Ready to answer questions!")

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

def submit_feedback(answer_id: int, score: int, was_helpful: bool, comment: str = None):
    """Submit feedback to the API with detailed logging."""
    try:
        logger.info(f"Starting feedback submission - answer_id={answer_id}, score={score}, helpful={was_helpful}")
        debug_print(f"Submitting feedback for answer_id={answer_id}, score={score}, helpful={was_helpful}")
        
        payload = {
            "answer_id": answer_id,
            "score": score,
            "was_helpful": was_helpful,
            "comment": comment
        }
        
        logger.info(f"Feedback payload: {payload}")
        debug_print(f"Payload = {payload}")
        
        response = requests.post(
            "http://localhost:8000/feedback",
            json=payload,
            timeout=30
        )
        
        logger.info(f"API response - status: {response.status_code}, text: {response.text}")
        debug_print(f"Response status = {response.status_code}")
        debug_print(f"Response text = {response.text}")
        
        if response.status_code == 200:
            logger.info("Feedback submitted successfully")
            debug_print("Feedback submitted successfully!")
            return True
        else:
            logger.error(f"Feedback failed with status {response.status_code}: {response.text}")
            debug_print(f"Feedback failed with status {response.status_code}", "error")
            return False
            
    except Exception as e:
        logger.error(f"Exception in submit_feedback: {str(e)}")
        debug_print(f"Exception in submit_feedback: {str(e)}", "error")
        return False

# Main interaction area
question = st.text_input("Ask a question about Frank's qualifications:", 
                        value=st.session_state.get("question", ""),
                        key="current_question")

if question:
    try:
        with st.spinner("🤔 Analyzing resume and generating response..."):
            response = requests.post(
                "http://localhost:8000/ask",
                json={"text": question},
                timeout=30
            )
            
            if response.status_code == 200:
                answer_data = response.json()
                if answer_data["answer"]:
                    # Check confidence threshold - only show answers for high confidence
                    confidence = answer_data["confidence"]
                    
                    if confidence >= 0.8:
                        # High confidence - show the answer
                        st.success(f"Answer: {answer_data['answer']}")
                        
                        # Store the answer ID in session state
                        st.session_state.current_answer_id = answer_data["id"]
                        debug_print(f"Stored answer_id = {st.session_state.current_answer_id}")
                        
                        # Add feedback section
                        st.write("### Was this answer helpful?")
                        
                        debug_print(f"Current session answer_id = {st.session_state.current_answer_id}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("👍 Yes"):
                                debug_print("Yes button clicked!")
                                if st.session_state.current_answer_id:
                                    result = submit_feedback(
                                        answer_id=st.session_state.current_answer_id,
                                        score=5,
                                        was_helpful=True
                                    )
                                    if result:
                                        st.success("Thank you for your positive feedback!")
                                    else:
                                        st.error("Failed to submit feedback - check debug info above")
                                else:
                                    debug_print("No answer_id in session state!", "error")
                                    
                        with col2:
                            if st.button("👎 No"):
                                debug_print("No button clicked!")
                                if st.session_state.current_answer_id:
                                    result = submit_feedback(
                                        answer_id=st.session_state.current_answer_id,
                                        score=1,
                                        was_helpful=False
                                    )
                                    if result:
                                        st.success("Thank you for your feedback!")
                                    else:
                                        st.error("Failed to submit feedback - check debug info above")
                                else:
                                    debug_print("No answer_id in session state!", "error")
                        
                        # Optional detailed feedback
                        feedback_text = st.text_area("Additional feedback (optional)")
                        if feedback_text and st.button("Submit detailed feedback"):
                            if st.session_state.current_answer_id:
                                result = submit_feedback(
                                    answer_id=st.session_state.current_answer_id,
                                    score=3,  # Neutral score for detailed feedback
                                    was_helpful=True,  # Assume positive if they're giving detailed feedback
                                    comment=feedback_text
                                )
                                if result:
                                    st.success("Thank you for your detailed feedback!")
                                else:
                                    st.error("Failed to submit detailed feedback")
                            else:
                                debug_print("No answer_id for detailed feedback!", "error")
                    else:
                        # Low confidence - can't provide reliable answer
                        st.warning("I'm not confident enough to provide a reliable answer to that question. Please try rephrasing your question or use one of the example questions in the sidebar.")
                else:
                    st.warning("I couldn't find a specific answer to that question. Try rephrasing or check the example questions.")
            else:
                st.error(f"Error: Received status code {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        st.warning("⏳ The AI model is still initializing. Please wait a moment and try again...")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

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
        st.write(f"Current answer_id in session: {st.session_state.current_answer_id}")
        st.write(f"Session state keys: {list(st.session_state.keys())}")
        if st.button("Clear session state"):
            st.session_state.clear()
            st.rerun() 