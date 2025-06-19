"""
Test script for Frank's Candidate Concierge API
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "https://franks-candidate-concierge.onrender.com"

def test_root():
    response = requests.get(f"{API_BASE_URL}/")
    print("\nTesting root endpoint:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_health():
    response = requests.get(f"{API_BASE_URL}/health")
    print("\nTesting health endpoint:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_ask_question(question):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "text": question
    }
    
    response = requests.post(
        f"{API_BASE_URL}/ask",
        headers=headers,
        json=data
    )
    
    print(f"\nTesting ask endpoint with question: '{question}'")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    # Test all endpoints
    test_root()
    test_health()
    
    # Test some sample questions
    test_questions = [
        "What certifications do you have?",
        "What is your current role?",
        "What are your cloud skills?",
        "How much experience do you have?"
    ]
    
    for question in test_questions:
        test_ask_question(question)

    print("\n🧪 Testing Frank's Candidate Concierge API")
    print("=" * 50)
    test_api()
    print("\n" + "=" * 50) 