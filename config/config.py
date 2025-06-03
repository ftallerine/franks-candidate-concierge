from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Data directory
DATA_DIR = BASE_DIR / "data"
RESUME_PATH = DATA_DIR / "resume.txt"

# API settings
API_HOST = "localhost"
API_PORT = 8000
API_URL = f"http://{API_HOST}:{API_PORT}"

# Model settings
MODEL_NAME = "distilbert-base-cased-distilled-squad"
MAX_SEQUENCE_LENGTH = 512
DOC_STRIDE = 128

# Streamlit settings
STREAMLIT_PORT = 8501
PAGE_TITLE = "Frank's Candidate Concierge"
PAGE_ICON = "👔" 