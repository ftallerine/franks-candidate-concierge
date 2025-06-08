@echo off
echo Starting Frank's Candidate Concierge...
echo.

echo Starting FastAPI Backend Server...
start "FastAPI Backend" cmd /k "uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak > nul

echo Starting Streamlit Frontend...
start "Streamlit Frontend" cmd /k "streamlit run app/streamlit_app.py"

echo.
echo Services are starting up!
echo - FastAPI Backend: http://localhost:8000
echo - Streamlit Frontend: http://localhost:8501
echo.
echo Both services will open in separate windows.
pause 