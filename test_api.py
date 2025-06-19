"""
Test script for Frank's Candidate Concierge API
"""

import requests
import json
from datetime import datetime

def test_api():
    """Test the deployed API endpoints"""
    base_url = "https://franks-candidate-concierge.onrender.com"
    
    # Test simple questions that should work with structured data
    test_questions = [
        "What certifications does Frank have?",
        "What is Frank's current role?",
        "What are Frank's technical skills?",
        "Where is Frank located?",
        "What is Frank's experience with Azure?"
    ]
    
    print("Testing API endpoints...\n")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Check Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error checking health: {str(e)}\n")
    
    # Test questions
    print("Testing questions:")
    for question in test_questions:
        try:
            print(f"\nQuestion: {question}")
            response = requests.post(
                f"{base_url}/ask",
                json={"text": question},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Status: ✅ Success")
                print(f"Answer: {result.get('answer', 'No answer')}")
                print(f"Confidence: {result.get('confidence', 'Unknown')}")
            else:
                print(f"Status: ❌ Failed ({response.status_code})")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 80)

if __name__ == "__main__":
    print("\n🧪 Testing Frank's Candidate Concierge API")
    print("=" * 50)
    test_api()
    print("\n" + "=" * 50) 