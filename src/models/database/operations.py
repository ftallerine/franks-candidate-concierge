"""Database operations for the Candidate Concierge."""
from sqlalchemy.orm import Session
from .models import Question, Answer, Feedback
from datetime import datetime

class DatabaseOperations:
    def __init__(self, db: Session):
        self.db = db

    def store_qa_interaction(self, question_text: str, answer_text: str, 
                           confidence: float, source: str) -> tuple[Question, Answer]:
        """Store a question-answer interaction in the database."""
        question = Question(text=question_text)
        self.db.add(question)
        self.db.flush()  # Get the question ID
        
        answer = Answer(
            question_id=question.id,
            text=answer_text,
            confidence=confidence,
            source=source
        )
        self.db.add(answer)
        self.db.commit()
        return question, answer

    def store_feedback(self, answer_id: int, score: int, 
                      was_helpful: bool, comment: str = None) -> Feedback:
        """Store user feedback for an answer."""
        feedback = Feedback(
            answer_id=answer_id,
            score=score,
            was_helpful=was_helpful,
            comment=comment
        )
        self.db.add(feedback)
        self.db.commit()
        return feedback

    def get_training_data(self, min_feedback_score: int = 4, 
                         min_confidence: float = 0.7):
        """Get high-quality QA pairs for model training."""
        return self.db.query(Question, Answer, Feedback)\
            .join(Answer)\
            .join(Feedback)\
            .filter(Feedback.score >= min_feedback_score)\
            .filter(Answer.confidence >= min_confidence)\
            .all()

    def get_feedback_stats(self):
        """Get statistics about feedback scores."""
        return self.db.query(
            Feedback.score,
            func.count(Feedback.id).label('count')
        ).group_by(Feedback.score).all() 