"""
Prompt optimization and Q&A analytics for Frank's Candidate Concierge.
Uses stored feedback to improve prompts and system performance.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from sqlalchemy.orm import Session

from src.models.database.session import get_db
from src.models.database.operations import DatabaseOperations
from src.models.database.models import Question, Answer, Feedback
from src.config.data_loader import RESUME_DATA
from src.services.logging_config import logger


class PromptOptimizer:
    """Analyzes Q&A data to improve prompts and system performance."""
    
    def __init__(self, db: Session):
        self.db = db
        self.db_ops = DatabaseOperations(db)
    
    def analyze_feedback_patterns(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze feedback patterns to identify improvement areas."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get feedback data
        feedback_data = self.db.query(Question, Answer, Feedback)\
            .join(Answer, Question.id == Answer.question_id)\
            .join(Feedback, Answer.id == Feedback.answer_id)\
            .filter(Question.created_at >= cutoff_date)\
            .all()
        
        if not feedback_data:
            return {"message": "No feedback data found", "recommendations": []}
        
        # Analyze patterns
        low_rated = [row for row in feedback_data if row.Feedback.score <= 2]
        high_rated = [row for row in feedback_data if row.Feedback.score >= 4]
        
        # Common themes in low-rated responses
        low_rated_questions = [row.Question.text.lower() for row in low_rated]
        high_rated_questions = [row.Question.text.lower() for row in high_rated]
        
        analysis = {
            "total_feedback": len(feedback_data),
            "low_rated_count": len(low_rated),
            "high_rated_count": len(high_rated),
            "average_score": sum(row.Feedback.score for row in feedback_data) / len(feedback_data),
            "common_low_rated_themes": self._extract_themes(low_rated_questions),
            "common_high_rated_themes": self._extract_themes(high_rated_questions),
            "recommendations": self._generate_recommendations(low_rated, high_rated)
        }
        
        return analysis
    
    def _extract_themes(self, questions: List[str]) -> List[str]:
        """Extract common themes from questions."""
        # Simple keyword extraction
        keywords = []
        for question in questions:
            words = question.split()
            keywords.extend([word for word in words if len(word) > 3])
        
        # Return most common keywords
        common = Counter(keywords).most_common(5)
        return [word for word, count in common if count > 1]
    
    def _generate_recommendations(self, low_rated: List, high_rated: List) -> List[str]:
        """Generate recommendations based on feedback analysis."""
        recommendations = []
        
        if len(low_rated) > len(high_rated) * 0.3:  # >30% low ratings
            recommendations.append("Consider refining the prompt to be more specific about Frank's experience")
        
        if low_rated:
            low_themes = [row.Question.text.lower() for row in low_rated]
            if any("salary" in q for q in low_themes):
                recommendations.append("Add more detailed salary expectation information to resume data")
            if any("experience" in q for q in low_themes):
                recommendations.append("Enhance experience descriptions with more specific details")
            if any("skill" in q for q in low_themes):
                recommendations.append("Expand technical skills section with proficiency levels")
        
        return recommendations
    
    def suggest_prompt_improvements(self) -> Dict[str, str]:
        """Suggest improvements to the GPT prompt based on feedback."""
        analysis = self.analyze_feedback_patterns()
        
        base_prompt = """You are Frank's professional assistant. Answer this question about Frank's qualifications, experience, and skills based on his resume.

Question: {question}

Resume Context: {resume_data}

Provide a professional, concise answer. If you cannot find specific information, say so politely."""
        
        # Enhanced prompt based on common issues
        enhanced_prompt = """You are Frank's professional assistant and career advocate. Answer this question about Frank's qualifications, experience, and skills based on his detailed resume.

Question: {question}

Resume Context: {resume_data}

Instructions:
- Provide specific, detailed answers with examples when possible
- If asked about experience, mention duration and key achievements
- For technical questions, reference specific tools and technologies Frank has used
- If information isn't available, suggest related experience or skills Frank has
- Keep responses professional but personable
- Always end with a brief summary of why Frank would be a good fit

Answer:"""
        
        return {
            "current_prompt": base_prompt,
            "suggested_prompt": enhanced_prompt,
            "reasoning": "Enhanced prompt provides more guidance for detailed, specific responses"
        }
    
    def get_frequently_asked_questions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently asked questions to identify common user interests."""
        # Group similar questions by keywords
        questions = self.db.query(Question).all()
        
        # Simple clustering by common words
        question_groups = {}
        for q in questions:
            key_words = [word.lower() for word in q.text.split() if len(word) > 3]
            if key_words:
                primary_theme = key_words[0]  # Simplified grouping
                if primary_theme not in question_groups:
                    question_groups[primary_theme] = []
                question_groups[primary_theme].append(q)
        
        # Sort by frequency
        frequent_questions = sorted(
            question_groups.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:limit]
        
        return [
            {
                "theme": theme,
                "count": len(questions),
                "example_question": questions[0].text,
                "latest_question": max(questions, key=lambda x: x.created_at).text
            }
            for theme, questions in frequent_questions
        ]
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        return {
            "feedback_analysis": self.analyze_feedback_patterns(),
            "frequently_asked": self.get_frequently_asked_questions(),
            "prompt_suggestions": self.suggest_prompt_improvements(),
            "generated_at": datetime.now().isoformat()
        }


class DataExporter:
    """Export Q&A data for external analysis or backup."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_training_data(self, min_score: int = 4) -> List[Dict[str, Any]]:
        """Export high-quality Q&A pairs for future use."""
        high_quality = self.db.query(Question, Answer, Feedback)\
            .join(Answer, Question.id == Answer.question_id)\
            .join(Feedback, Answer.id == Feedback.answer_id)\
            .filter(Feedback.score >= min_score)\
            .all()
        
        return [
            {
                "question": row.Question.text,
                "answer": row.Answer.text,
                "confidence": row.Answer.confidence,
                "feedback_score": row.Feedback.score,
                "timestamp": row.Question.created_at.isoformat()
            }
            for row in high_quality
        ]
    
    def export_analytics_data(self) -> Dict[str, Any]:
        """Export analytics data for dashboard or reporting."""
        total_questions = self.db.query(Question).count()
        total_answers = self.db.query(Answer).count()
        total_feedback = self.db.query(Feedback).count()
        
        if total_feedback > 0:
            avg_score = self.db.query(Feedback).with_entities(
                self.db.query(Feedback.score).subquery().c.score
            ).scalar()
        else:
            avg_score = 0
        
        return {
            "total_questions": total_questions,
            "total_answers": total_answers,
            "total_feedback": total_feedback,
            "average_feedback_score": avg_score,
            "export_timestamp": datetime.now().isoformat()
        }


def run_optimization_analysis():
    """Main function to run prompt optimization analysis."""
    logger.info("Starting prompt optimization analysis...")
    
    try:
        # Get database session
        db = next(get_db())
        
        # Initialize optimizer
        optimizer = PromptOptimizer(db)
        
        # Generate comprehensive report
        report = optimizer.generate_performance_report()
        
        # Save report
        report_filename = f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"logs/{report_filename}", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Optimization report saved to logs/{report_filename}")
        
        # Print key insights
        feedback_analysis = report["feedback_analysis"]
        print(f"\n📊 PERFORMANCE ANALYSIS")
        print(f"Total feedback received: {feedback_analysis['total_feedback']}")
        print(f"Average rating: {feedback_analysis['average_score']:.2f}/5")
        print(f"Recommendations: {len(feedback_analysis['recommendations'])}")
        
        for rec in feedback_analysis['recommendations']:
            print(f"  • {rec}")
        
        return True
        
    except Exception as e:
        logger.error(f"Optimization analysis failed: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    # Run the optimization analysis
    success = run_optimization_analysis()
    if success:
        print("\n✅ Optimization analysis completed successfully!")
    else:
        print("\n❌ Optimization analysis failed!") 