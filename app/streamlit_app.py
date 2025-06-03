import streamlit as st
import requests
import json
import time
import os
import logging
from pathlib import Path
from datetime import datetime

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
    page_icon="🤵",
    layout="wide"
)

logger.info("Streamlit app started")

# Custom CSS for the circular image
st.markdown("""
<style>
div.stImage > img {
    width: 200px;
    height: 200px;
    border-radius: 50% !important;
    object-fit: cover;
    border: 3px solid #2e6da4;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin: 20px auto;
    display: block;
}
.profile-section {
    text-align: center;
    padding: 20px;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for answer tracking
if 'current_answer_id' not in st.session_state:
    st.session_state.current_answer_id = None

# Title and profile section
st.title("Frank's Candidate Concierge 🤵")

# Profile section with image
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Get the absolute path to the image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "static", "images", "frank_headshot.jpg")
    
    try:
        if os.path.exists(image_path):
            st.image(image_path, width=200)
        else:
            st.info("👔 Professional headshot will be displayed here")
    except Exception as e:
        st.info("👔 Professional headshot will be displayed here")

st.markdown("""
Welcome to Frank's Candidate Concierge! I'm your AI assistant, ready to answer questions about Frank's professional experience, 
skills, certifications, and more. Feel free to ask me anything about Frank's qualifications!
""")

# Function to check if API is ready
def is_api_ready():
    try:
        response = requests.get("http://localhost:8000")
        return response.status_code == 200
    except:
        return False

# Add a loading message while the model is initializing
if not is_api_ready():
    with st.spinner("⚙️ Initializing AI Model..."):
        st.warning("Please wait while the AI model is being initialized... This may take a few minutes on first startup.")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Show progress simulation
        for i in range(100):
            # Simulate progress steps
            if i < 25:
                status_text.text("Loading model...")
            elif i < 50:
                status_text.text("Loading tokenizer...")
            elif i < 75:
                status_text.text("Setting up QA pipeline...")
            else:
                status_text.text("Loading resume data...")
            progress_bar.progress(i + 1)
            time.sleep(0.1)
            
            # Check if API is ready
            if is_api_ready():
                break
                
        if is_api_ready():
            st.success("✅ AI Model initialized successfully! Ready to answer your questions.")
        else:
            st.error("❌ Failed to initialize the model. Please refresh the page to try again.")
else:
    st.success("✅ AI Model is ready!")

# Sidebar with example questions
with st.sidebar:
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
        st.write(f"🐛 DEBUG: Submitting feedback for answer_id={answer_id}, score={score}, helpful={was_helpful}")
        
        payload = {
            "answer_id": answer_id,
            "score": score,
            "was_helpful": was_helpful,
            "comment": comment
        }
        
        logger.info(f"Feedback payload: {payload}")
        st.write(f"🐛 DEBUG: Payload = {payload}")
        
        response = requests.post(
            "http://localhost:8000/feedback",
            json=payload,
            timeout=30
        )
        
        logger.info(f"API response - status: {response.status_code}, text: {response.text}")
        st.write(f"🐛 DEBUG: Response status = {response.status_code}")
        st.write(f"🐛 DEBUG: Response text = {response.text}")
        
        if response.status_code == 200:
            logger.info("Feedback submitted successfully")
            st.write("🐛 DEBUG: Feedback submitted successfully!")
            return True
        else:
            logger.error(f"Feedback failed with status {response.status_code}: {response.text}")
            st.error(f"🐛 DEBUG: Feedback failed with status {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Exception in submit_feedback: {str(e)}")
        st.error(f"🐛 DEBUG: Exception in submit_feedback: {str(e)}")
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
                    st.success(f"Answer: {answer_data['answer']}")
                    
                    # Store the answer ID in session state
                    st.session_state.current_answer_id = answer_data["id"]
                    st.write(f"🐛 DEBUG: Stored answer_id = {st.session_state.current_answer_id}")
                    
                    # Show confidence with color coding
                    confidence = answer_data["confidence"]
                    if confidence >= 0.8:
                        st.info(f"🎯 Confidence: {confidence:.2%}")
                    elif confidence >= 0.5:
                        st.warning(f"⚠️ Confidence: {confidence:.2%}")
                    else:
                        st.error(f"❗ Low Confidence: {confidence:.2%}")
                    
                    # Add feedback section
                    st.write("### Was this answer helpful?")
                    
                    st.write(f"🐛 DEBUG: Current session answer_id = {st.session_state.current_answer_id}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👍 Yes"):
                            st.write("🐛 DEBUG: Yes button clicked!")
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
                                st.error("🐛 DEBUG: No answer_id in session state!")
                                
                    with col2:
                        if st.button("👎 No"):
                            st.write("🐛 DEBUG: No button clicked!")
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
                                st.error("🐛 DEBUG: No answer_id in session state!")
                    
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
                            st.error("🐛 DEBUG: No answer_id for detailed feedback!")
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
- Ask specific questions about Frank's experience, skills, or qualifications
- Try clicking the example questions in the sidebar
- The AI will answer based on Frank's resume data
- Higher confidence scores (>80%) indicate more reliable answers
- Your feedback helps improve the system's accuracy
""")

# Debug info section
with st.expander("🐛 Debug Info"):
    st.write(f"Current answer_id in session: {st.session_state.current_answer_id}")
    st.write(f"Session state keys: {list(st.session_state.keys())}")
    if st.button("Clear session state"):
        st.session_state.clear()
        st.rerun() 