"""
Test script for Frank's Candidate Concierge API
"""

import requests
import json
import time

# Wait for the server to start
print("Waiting for server to start...")
time.sleep(5)

# Test the /ask endpoint
print("Testing /ask endpoint...")
try:
    response = requests.post(
        "http://localhost:8000/ask",
        json={"text": "What certifications do you have?"},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response:")
        print(f"  Answer: {data['answer']}")
        print(f"  Confidence: {data['confidence']}")
        print(f"  Answer ID: {data.get('answer_id', 'None')}")
        
        # Test feedback if we got an answer_id
        if data.get('answer_id'):
            print("\nTesting /feedback endpoint...")
            feedback_response = requests.post(
                "http://localhost:8000/feedback",
                json={
                    "answer_id": data['answer_id'],
                    "score": 5,
                    "was_helpful": True,
                    "comment": "Very helpful test response!"
                }
            )
            
            if feedback_response.status_code == 200:
                feedback_data = feedback_response.json()
                print("✅ Feedback Response:")
                print(f"  Status: {feedback_data['status']}")
                print(f"  Message: {feedback_data['message']}")
                print(f"  Feedback ID: {feedback_data['feedback_id']}")
            else:
                print(f"❌ Feedback failed: {feedback_response.status_code}")
                print(feedback_response.text)
    else:
        print(f"❌ API failed: {response.status_code}")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"❌ Connection error: {e}")
    print("Make sure the API server is running on http://localhost:8000") 