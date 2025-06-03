"""Script to check feedback table specifically."""
import requests

def check_feedback_data():
    print("📊 Checking Feedback Table Data")
    print("=" * 50)
    
    # Get recent data to see feedback
    try:
        response = requests.get("http://localhost:8000/history?limit=50")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} total Q&A interactions")
            
            # Check for any feedback-related data (we'll need to create a new endpoint for this)
            print("\nNote: The current /history endpoint doesn't show feedback data.")
            print("Let me create a direct database query...")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def query_feedback_directly():
    """Direct database query for feedback."""
    try:
        # Using the simple database connection approach
        from sqlalchemy import create_engine, text
        
        DATABASE_URL = "postgresql://postgres:REMOVED_DATABASE_PASSWORD@localhost:5432/concierge_db"
        
        print("\n🔍 Direct Database Query - Feedback Table")
        print("-" * 50)
        
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Count feedback records
            feedback_count = conn.execute(text("SELECT COUNT(*) FROM feedback")).scalar()
            print(f"Total feedback records: {feedback_count}")
            
            if feedback_count > 0:
                # Get all feedback records
                result = conn.execute(text("""
                    SELECT 
                        f.id,
                        f.answer_id,
                        f.score,
                        f.was_helpful,
                        f.comment,
                        f.timestamp,
                        a.text as answer_text
                    FROM feedback f
                    LEFT JOIN answers a ON f.answer_id = a.id
                    ORDER BY f.timestamp DESC
                """))
                
                rows = result.fetchall()
                
                print(f"\n📝 All Feedback Records:")
                for i, row in enumerate(rows, 1):
                    print(f"\n#{i} - Feedback ID: {row[0]}")
                    print(f"   Answer ID: {row[1]}")
                    print(f"   Score: {row[2]}/5")
                    print(f"   Helpful: {'Yes' if row[3] else 'No'}")
                    print(f"   Comment: {row[4] or 'None'}")
                    print(f"   Time: {row[5]}")
                    print(f"   For Answer: {row[6][:100]}...")
                    
            else:
                print("❌ No feedback records found in database")
                
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")

if __name__ == "__main__":
    check_feedback_data()
    query_feedback_directly() 