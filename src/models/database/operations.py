"""Database operations for the Candidate Concierge."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Question, Answer, Feedback, PromptVersion
from datetime import datetime

class DatabaseOperations:
    def __init__(self, db: Session):
        self.db = db

    def log_question(self, question_text: str) -> int:
        """Log a question and return its ID."""
        question = Question(text=question_text)
        self.db.add(question)
        self.db.flush()  # Get the question ID without committing
        return question.id

    def log_answer(self, question_id: int, answer_text: str, source: str, confidence: float) -> int:
        """Log an answer and return its ID."""
        answer = Answer(
            question_id=question_id,
            text=answer_text,
            confidence=confidence,
            source=source
        )
        self.db.add(answer)
        self.db.commit()
        return answer.id

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
        # Get Q&A pairs that have feedback with high scores
        return self.db.query(Question, Answer, Feedback)\
            .join(Answer, Question.id == Answer.question_id)\
            .join(Feedback, Answer.id == Feedback.answer_id)\
            .filter(Feedback.score >= min_feedback_score)\
            .filter(Answer.confidence >= min_confidence)\
            .all()

    def get_feedback_stats(self):
        """Get statistics about feedback scores."""
        return self.db.query(
            Feedback.score,
            func.count(Feedback.id).label('count')
        ).group_by(Feedback.score).all()
    
    def get_high_confidence_qa_pairs(self, min_confidence: float = 0.8, limit: int = 50):
        """Get high-confidence Q&A pairs even without feedback for training."""
        return self.db.query(Question, Answer)\
            .join(Answer, Question.id == Answer.question_id)\
            .filter(Answer.confidence >= min_confidence)\
            .limit(limit)\
            .all()
    
    def store_prompt_version(self, name: str, prompt_text: str, version_number: str, 
                           notes: str = None, created_by: str = "system") -> PromptVersion:
        """Store a new prompt version."""
        prompt_version = PromptVersion(
            name=name,
            prompt_text=prompt_text,
            version_number=version_number,
            notes=notes,
            created_by=created_by
        )
        self.db.add(prompt_version)
        self.db.commit()
        return prompt_version
    
    def activate_prompt(self, prompt_id: int) -> bool:
        """Activate a prompt version (deactivates all others)."""
        # Deactivate all prompts
        self.db.query(PromptVersion).update({"is_active": False, "activated_at": None})
        
        # Activate the selected prompt
        prompt = self.db.query(PromptVersion).filter(PromptVersion.id == prompt_id).first()
        if prompt:
            prompt.is_active = True
            prompt.activated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def get_active_prompt(self) -> PromptVersion:
        """Get the currently active prompt."""
        return self.db.query(PromptVersion)\
            .filter(PromptVersion.is_active == True)\
            .first()
    
    def get_prompt_performance(self, prompt_id: int) -> float:
        """Calculate average feedback score for a specific prompt version."""
        # This would require tracking which prompt was used for each answer
        # For now, return None - can be enhanced later
        return None 