#!/usr/bin/env python3
"""
Manual script to trigger model training.
Run this to test the training system with current feedback data.
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

def check_training_status():
    """Check current training status."""
    try:
        response = requests.get(f"{API_BASE}/training/status")
        if response.status_code == 200:
            status = response.json()
            print("🔍 Current Training Status:")
            print(f"   Status: {status['status']}")
            print(f"   Last Training: {status['last_training_date'] or 'Never'}")
            print(f"   Training Samples: {status['training_samples']}")
            print(f"   Satisfaction Rate: {status['satisfaction_rate']:.2%}")
            print(f"   Currently Training: {status['is_training']}")
            return status
        else:
            print(f"❌ Error getting status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def check_feedback_data():
    """Check available feedback data."""
    try:
        response = requests.get(f"{API_BASE}/feedback")
        if response.status_code == 200:
            feedback = response.json()
            print(f"\n📊 Available Feedback Data:")
            print(f"   Total Feedback Records: {len(feedback)}")
            
            if feedback:
                scores = [f['score'] for f in feedback]
                avg_score = sum(scores) / len(scores)
                positive = len([s for s in scores if s >= 4])
                negative = len([s for s in scores if s <= 2])
                
                print(f"   Average Score: {avg_score:.1f}/5")
                print(f"   Positive Feedback: {positive}")
                print(f"   Negative Feedback: {negative}")
                
                print("\n   Recent Feedback:")
                for i, f in enumerate(feedback[:3]):
                    print(f"      #{i+1}: Score {f['score']}/5, Helpful: {f['was_helpful']}")
                    if f['comment']:
                        print(f"          Comment: {f['comment']}")
            
            return len(feedback)
        else:
            print(f"❌ Error getting feedback: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 0

def start_training(force_retrain=False):
    """Start model training."""
    try:
        payload = {
            "force_retrain": force_retrain,
            "min_feedback_score": 4,
            "min_confidence": 0.7
        }
        
        print(f"\n🚀 Starting Training (force_retrain={force_retrain})...")
        response = requests.post(f"{API_BASE}/training/start", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['status']}: {result['message']}")
            if 'training_samples' in result:
                print(f"   Training Samples: {result['training_samples']}")
            return True
        else:
            print(f"❌ Training failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("🤖 Frank's Candidate Concierge - Training Manager")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code != 200:
            print("❌ API is not running. Please start the FastAPI server first.")
            return
    except:
        print("❌ Cannot connect to API. Please start the FastAPI server first.")
        return
    
    print("✅ API is running")
    
    # Check current status
    status = check_training_status()
    if not status:
        return
    
    # Check feedback data
    feedback_count = check_feedback_data()
    
    # Training options
    print(f"\n🎯 Training Options:")
    print(f"   1. Automatic Training (requires 3+ high-quality feedback samples)")
    print(f"   2. Force Training (uses synthetic data if insufficient feedback)")
    print(f"   3. Check Status Only")
    print(f"   4. Exit")
    
    choice = input(f"\nSelect option (1-4): ").strip()
    
    if choice == "1":
        if feedback_count >= 3:
            start_training(force_retrain=False)
        else:
            print(f"❌ Insufficient feedback data ({feedback_count}/3). Use option 2 for force training.")
    elif choice == "2":
        start_training(force_retrain=True)
    elif choice == "3":
        print("✅ Status check completed")
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 