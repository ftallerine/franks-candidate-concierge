"""Simple script to query database using existing setup."""
import os
from sqlalchemy import create_engine, text

# Database configuration (hardcoded for simplicity)
DATABASE_URL = "postgresql://postgres:REMOVED_DATABASE_PASSWORD@localhost:5432/concierge_db"

try:
    print("🗄️  Frank's Candidate Concierge - Database Contents")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Count records
        questions_count = conn.execute(text("SELECT COUNT(*) FROM questions")).scalar()
        answers_count = conn.execute(text("SELECT COUNT(*) FROM answers")).scalar()
        feedback_count = conn.execute(text("SELECT COUNT(*) FROM feedback")).scalar()
        
        print(f"📊 Record Counts:")
        print(f"   Questions: {questions_count}")
        print(f"   Answers: {answers_count}")
        print(f"   Feedback: {feedback_count}")
        print()
        
        # Show recent Q&A pairs
        if questions_count > 0:
            print("📝 Recent Question & Answer Pairs:")
            print("-" * 60)
            
            result = conn.execute(text("""
                SELECT 
                    q.id, 
                    q.text as question,
                    q.timestamp,
                    a.id as answer_id,
                    a.text as answer,
                    a.confidence,
                    a.source
                FROM questions q 
                LEFT JOIN answers a ON q.id = a.question_id 
                ORDER BY q.timestamp DESC 
                LIMIT 10
            """))
            
            rows = result.fetchall()
            
            for i, row in enumerate(rows, 1):
                print(f"\n#{i} - Question ID: {row[0]}")
                print(f"   Time: {row[2]}")
                print(f"   Question: {row[1]}")
                
                if row[3]:  # answer_id exists
                    print(f"   Answer ID: {row[3]}")
                    print(f"   Answer: {row[4]}")
                    print(f"   Confidence: {row[5]}")
                    print(f"   Source: {row[6]}")
                else:
                    print("   ❌ No answer found")
        else:
            print("📭 No questions found in database")
        
        # Show any feedback
        if feedback_count > 0:
            print(f"\n💭 Recent Feedback:")
            print("-" * 60)
            
            feedback_result = conn.execute(text("""
                SELECT 
                    f.id,
                    f.answer_id,
                    f.score,
                    f.was_helpful,
                    f.comment,
                    f.timestamp
                FROM feedback f
                ORDER BY f.timestamp DESC
                LIMIT 5
            """))
            
            feedback_rows = feedback_result.fetchall()
            
            for feedback in feedback_rows:
                print(f"\nFeedback ID: {feedback[0]}")
                print(f"  Answer ID: {feedback[1]}")
                print(f"  Score: {feedback[2]}/5")
                print(f"  Helpful: {'Yes' if feedback[3] else 'No'}")
                print(f"  Comment: {feedback[4] or 'None'}")
                print(f"  Time: {feedback[5]}")
    
    print("\n" + "=" * 60)
    print("✅ Database query completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("Make sure PostgreSQL is running and the API is working.") 