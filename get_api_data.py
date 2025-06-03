"""Script to get data from the API and display it nicely."""
import requests
import json
from datetime import datetime

def get_data():
    try:
        print("🗄️  Frank's Candidate Concierge - API Data")
        print("=" * 60)
        
        # Get the history from the API
        response = requests.get("http://localhost:8000/history?limit=20")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📊 Found {len(data)} Q&A interactions:")
            print()
            
            for i, item in enumerate(data, 1):
                print(f"#{i} - Question ID: {item['question_id']}")
                print(f"   Time: {item['question_timestamp']}")
                print(f"   Question: {item['question_text']}")
                
                if item['answer_id']:
                    print(f"   Answer ID: {item['answer_id']}")
                    print(f"   Answer: {item['answer_text']}")
                    print(f"   Confidence: {item['confidence']}")
                    print(f"   Source: {item['source']}")
                    print(f"   Answer Time: {item['answer_timestamp']}")
                else:
                    print("   ❌ No answer found")
                print("-" * 40)
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def get_health():
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is healthy!")
            return True
        else:
            print("❌ API health check failed")
            return False
    except:
        print("❌ Cannot connect to API")
        return False

if __name__ == "__main__":
    if get_health():
        get_data()
    else:
        print("Make sure the FastAPI server is running on http://localhost:8000") 