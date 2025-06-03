"""Script to display data from the PostgreSQL database."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "concierge_db")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

try:
    import psycopg2
    
    print("🗄️  Frank's Candidate Concierge - Database Contents")
    print("=" * 60)
    
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Show table counts
    cursor.execute("SELECT COUNT(*) FROM questions")
    questions_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM answers") 
    answers_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM feedback")
    feedback_count = cursor.fetchone()[0]
    
    print(f"📊 Record Counts:")
    print(f"   Questions: {questions_count}")
    print(f"   Answers: {answers_count}")
    print(f"   Feedback: {feedback_count}")
    print()
    
    # Show all questions and answers
    if questions_count > 0:
        print("📝 All Question & Answer Pairs:")
        print("-" * 60)
        
        cursor.execute("""
            SELECT 
                q.id as question_id,
                q.text as question,
                q.timestamp as question_time,
                a.id as answer_id,
                a.text as answer,
                a.confidence,
                a.source,
                a.timestamp as answer_time
            FROM questions q 
            LEFT JOIN answers a ON q.id = a.question_id 
            ORDER BY q.timestamp DESC
        """)
        
        results = cursor.fetchall()
        
        for i, row in enumerate(results, 1):
            q_id, question, q_time, a_id, answer, confidence, source, a_time = row
            
            print(f"\n#{i} - Question ID: {q_id}")
            print(f"   Time: {q_time}")
            print(f"   Question: {question}")
            
            if a_id:
                print(f"   Answer ID: {a_id}")
                print(f"   Answer: {answer}")
                print(f"   Confidence: {confidence:.2%}" if confidence else f"   Confidence: {confidence}")
                print(f"   Source: {source}")
                print(f"   Answer Time: {a_time}")
            else:
                print("   ❌ No answer found")
                
    else:
        print("📭 No questions found in database")
    
    # Show feedback if any
    if feedback_count > 0:
        print(f"\n💭 Feedback Records:")
        print("-" * 60)
        
        cursor.execute("""
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
        """)
        
        feedback_results = cursor.fetchall()
        
        for feedback in feedback_results:
            f_id, answer_id, score, helpful, comment, f_time, answer_text = feedback
            print(f"\nFeedback ID: {f_id}")
            print(f"  Answer ID: {answer_id}")
            print(f"  Score: {score}/5")
            print(f"  Helpful: {'Yes' if helpful else 'No'}")
            print(f"  Comment: {comment or 'None'}")
            print(f"  Time: {f_time}")
            print(f"  For Answer: {answer_text[:100]}...")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Database query completed successfully!")
    
except Exception as e:
    print(f"❌ Error connecting to database: {str(e)}")
    print("Make sure PostgreSQL is running and credentials are correct.") 