"""Model training and fine-tuning using collected feedback data."""
import torch
from transformers import (
    AutoModelForQuestionAnswering, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer,
    default_data_collator
)
from torch.utils.data import Dataset
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from src.models.database.session import get_db
from src.models.database.operations import DatabaseOperations
from src.models.resume_data import RESUME_DATA

logger = logging.getLogger(__name__)

class ResumeQADataset(Dataset):
    """Dataset for fine-tuning on resume-specific Q&A pairs."""
    
    def __init__(self, qa_pairs: List[Dict], tokenizer, resume_context: str, max_length: int = 384):
        self.qa_pairs = qa_pairs
        self.tokenizer = tokenizer
        self.resume_context = resume_context
        self.max_length = max_length
        
    def __len__(self):
        return len(self.qa_pairs)
    
    def __getitem__(self, idx):
        qa_pair = self.qa_pairs[idx]
        question = qa_pair['question']
        answer = qa_pair['answer']
        
        # Tokenize question and context
        encoding = self.tokenizer(
            question,
            self.resume_context,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # Find answer start and end positions in the tokenized context
        answer_start, answer_end = self._find_answer_positions(
            encoding, answer, question
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'start_positions': torch.tensor(answer_start, dtype=torch.long),
            'end_positions': torch.tensor(answer_end, dtype=torch.long)
        }
    
    def _find_answer_positions(self, encoding, answer: str, question: str) -> Tuple[int, int]:
        """Find the start and end token positions of the answer in the context."""
        # Convert tokens back to text to find answer position
        tokens = self.tokenizer.convert_ids_to_tokens(encoding['input_ids'].flatten())
        
        # Find separator between question and context
        sep_indices = [i for i, token in enumerate(tokens) if token == '[SEP]']
        if len(sep_indices) < 2:
            return 0, 0  # Fallback if structure is unexpected
            
        context_start = sep_indices[0] + 1
        context_end = sep_indices[1]
        
        # Reconstruct context from tokens
        context_tokens = tokens[context_start:context_end]
        context_text = self.tokenizer.convert_tokens_to_string(context_tokens)
        
        # Find answer in context
        answer_start_char = context_text.lower().find(answer.lower())
        if answer_start_char == -1:
            return 0, 0  # Answer not found in context
            
        answer_end_char = answer_start_char + len(answer)
        
        # Convert character positions to token positions
        answer_start_token = context_start
        answer_end_token = context_start
        
        # This is a simplified approach - in practice, you'd want more sophisticated alignment
        for i, token in enumerate(context_tokens):
            if answer_start_char <= i * 4 <= answer_end_char:  # Rough estimation
                if answer_start_token == context_start:
                    answer_start_token = context_start + i
                answer_end_token = context_start + i + 1
                
        return answer_start_token, min(answer_end_token, len(tokens) - 1)

class ModelTrainer:
    """Handles model training and fine-tuning based on feedback data."""
    
    def __init__(self, model_name: str = "deepset/minilm-uncased-squad2"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.resume_context = self._load_resume_context()
        
    def _load_resume_context(self) -> str:
        """Load resume content for training context."""
        resume_path = Path("data/resume.txt")
        if resume_path.exists():
            with open(resume_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    def prepare_training_data(self, db: Session) -> List[Dict]:
        """Collect high-quality Q&A pairs from database for training."""
        db_ops = DatabaseOperations(db)
        
        # Get high-quality interactions (score >= 4, confidence >= 0.7)
        training_pairs = db_ops.get_training_data(min_feedback_score=4, min_confidence=0.7)
        
        formatted_pairs = []
        for question, answer, feedback in training_pairs:
            formatted_pairs.append({
                'question': question.text,
                'answer': answer.text,
                'feedback_score': feedback.score,
                'confidence': answer.confidence
            })
            
        logger.info(f"Prepared {len(formatted_pairs)} high-quality training pairs")
        return formatted_pairs
    
    def add_synthetic_training_data(self) -> List[Dict]:
        """Create synthetic training data from structured resume data."""
        synthetic_pairs = []
        
        # Contact Information Q&A
        contact_qa = [
            ("What is Frank's email address?", RESUME_DATA["contact_information"]["email"]),
            ("How can I contact Frank?", f"Email: {RESUME_DATA['contact_information']['email']}, LinkedIn: {RESUME_DATA['contact_information']['linkedin']}"),
            ("What is Frank's LinkedIn profile?", RESUME_DATA["contact_information"]["linkedin"]),
            ("Where is Frank located?", RESUME_DATA["contact_information"]["location"]),
            ("Where does Frank live?", RESUME_DATA["contact_information"]["location"]),
        ]
        
        # Current Role & Job Search Q&A
        current_job = RESUME_DATA["professional_experience"][0]
        current_role_text = f"{current_job['title']} at {current_job['company']} ({current_job['dates']})"
        role_qa = [
            ("What is Frank's current role?", current_role_text),
            ("What is Frank's current position?", current_role_text),
            ("Where does Frank work now?", "Frank works at The Marker Group in Montgomery, TX (Houston metropolitan area)"),
            ("What kind of job is Frank looking for?", RESUME_DATA["job_search_criteria"]["desired_role"]),
            ("What roles is Frank seeking?", RESUME_DATA["job_search_criteria"]["desired_role"]),
            ("What is Frank's target role?", RESUME_DATA["job_search_criteria"]["desired_role"]),
        ]
        
        # Experience & Years Q&A
        experience_qa = [
            ("How many years of business analysis experience does Frank have?", RESUME_DATA["experience_highlights"]["total_ba_experience"]),
            ("How long has Frank been a Business Analyst?", RESUME_DATA["experience_highlights"]["total_ba_experience"]),
            ("How much Scrum Master experience does Frank have?", RESUME_DATA["experience_highlights"]["scrum_master_experience"]),
            ("How many years of Azure experience does Frank have?", RESUME_DATA["experience_highlights"]["azure_experience"]),
            ("How long has Frank been working with SQL?", RESUME_DATA["experience_highlights"]["sql_experience"]),
            ("What is Frank's experience level?", f"Total Business Analysis experience: {RESUME_DATA['experience_highlights']['total_ba_experience']}, Scrum Master: {RESUME_DATA['experience_highlights']['scrum_master_experience']}, Azure: {RESUME_DATA['experience_highlights']['azure_experience']}, SQL: {RESUME_DATA['experience_highlights']['sql_experience']}"),
        ]
        
        # Certifications Q&A
        cert_list = [f"{cert['name']} ({cert['issuer']})" for cert in RESUME_DATA["certifications"]]
        cert_with_years = [f"{cert['name']} ({cert['issuer']}, {cert['year_obtained']})" for cert in RESUME_DATA["certifications"]]
        cert_qa = [
            ("What certifications does Frank have?", ", ".join(cert_list)),
            ("Is Frank certified?", ", ".join(cert_list)),
            ("What are Frank's professional certifications?", ", ".join(cert_list)),
            ("When did Frank get his certifications?", ", ".join(cert_with_years)),
            ("Does Frank have any Azure certifications?", "Microsoft Certified: Azure Administrator Associate (Microsoft, 2021), Microsoft Certified: Azure Fundamentals (Microsoft, 2020)"),
            ("Is Frank a Certified Scrum Master?", "Yes, Certified Scrum Master (CSM) from Scrum Alliance, obtained in 2019"),
        ]
        
        # Skills Q&A
        skills_qa = [
            ("What are Frank's technical skills?", ", ".join(RESUME_DATA["skills_and_technologies"]["cloud_and_net"] + RESUME_DATA["skills_and_technologies"]["tools"])),
            ("What tools does Frank use?", ", ".join(RESUME_DATA["skills_and_technologies"]["tools"])),
            ("What cloud technologies does Frank know?", ", ".join(RESUME_DATA["skills_and_technologies"]["cloud_and_net"])),
            ("What are Frank's business analysis skills?", ", ".join(RESUME_DATA["skills_and_technologies"]["business_analysis"])),
            ("What are Frank's Agile and Scrum skills?", ", ".join(RESUME_DATA["skills_and_technologies"]["agile_and_scrum"])),
            ("What soft skills does Frank have?", ", ".join(RESUME_DATA["skills_and_technologies"]["soft_skills"])),
            ("What programming languages does Frank know?", ", ".join(RESUME_DATA["skills_and_technologies"]["programming_languages"])),
            ("Does Frank know Python?", "Yes, Frank is proficient in Python for data processing, ML pipelines, and automation scripts"),
            ("What is Frank's experience with Azure?", "3+ years of Azure experience including Azure DevOps, Azure Portal, and Azure administration"),
            ("Does Frank know SQL?", "Yes, Frank has 3+ years of SQL experience for database design, reporting, and data analysis"),
            ("How long has Frank been using Office 365?", "Frank has 5+ years of experience with Office 365"),
            ("Does Frank know Mermaid.js?", "Yes, Frank is proficient with Mermaid.js for creating diagrams and visualizations"),
        ]
        
        # Education Q&A
        education_qa = [
            ("What is Frank's educational background?", f"{RESUME_DATA['education']['degrees'][0]} and {RESUME_DATA['education']['degrees'][1]} from {RESUME_DATA['education']['university']}, graduated {RESUME_DATA['education']['honors']} in {RESUME_DATA['education']['graduation_year']}"),
            ("Where did Frank go to university?", RESUME_DATA["education"]["university"]),
            ("What degrees does Frank have?", f"{RESUME_DATA['education']['degrees'][0]} and {RESUME_DATA['education']['degrees'][1]}"),
            ("Did Frank graduate with honors?", f"Yes, Frank graduated {RESUME_DATA['education']['honors']}"),
            ("When did Frank graduate?", f"Frank graduated in {RESUME_DATA['education']['graduation_year']}"),
            ("What year did Frank graduate from college?", RESUME_DATA["education"]["graduation_year"]),
        ]
        
        # Achievements Q&A
        achievements_list = [item["achievement"] for item in RESUME_DATA["key_achievements_summary"]]
        achievements_qa = [
            ("What are Frank's key achievements?", ". ".join(achievements_list)),
            ("What results has Frank delivered?", ". ".join(achievements_list)),
            ("What impact has Frank made?", ". ".join(achievements_list)),
            ("What metrics can Frank share?", ". ".join(achievements_list)),
        ]
        
        # Company-specific Q&A
        for job in RESUME_DATA["professional_experience"]:
            company_qa = [
                (f"What was Frank's role at {job['company']}?", job["title"]),
                (f"When did Frank work at {job['company']}?", job["duration"]),
                (f"What did Frank do at {job['company']}?", ". ".join(job["responsibilities"])),
                (f"What were Frank's achievements at {job['company']}?", ". ".join(job["achievements"])),
            ]
            synthetic_pairs.extend([{
                'question': q,
                'answer': a,
                'feedback_score': 5,
                'confidence': 1.0
            } for q, a in company_qa])
        
        # Projects Q&A
        project_qa = [
            ("What projects has Frank worked on?", f"{RESUME_DATA['projects'][0]['name']}: {' '.join(RESUME_DATA['projects'][0]['description'])}"),
            ("Tell me about Frank's AI project", f"{RESUME_DATA['projects'][0]['name']}: {' '.join(RESUME_DATA['projects'][0]['description'])} {' '.join(RESUME_DATA['projects'][0]['achievements'])}"),
            ("Has Frank worked with machine learning?", f"Yes, Frank built the {RESUME_DATA['projects'][0]['name']}: {' '.join(RESUME_DATA['projects'][0]['description'])}"),
        ]
        
        # Salary Q&A
        salary_qa = [
            ("What are Frank's salary expectations?", f"Target salary: {RESUME_DATA['salary_expectations']['target']}, {RESUME_DATA['salary_expectations']['negotiable']}. {RESUME_DATA['salary_expectations']['additional_notes']}"),
            ("What is Frank's target salary?", RESUME_DATA["salary_expectations"]["target"]),
            ("Is Frank's salary negotiable?", f"Yes, {RESUME_DATA['salary_expectations']['negotiable']}. {RESUME_DATA['salary_expectations']['additional_notes']}"),
        ]
        
        # Language Q&A
        language_qa = [
            ("What languages does Frank speak?", ", ".join(RESUME_DATA["languages"])),
            ("Is Frank bilingual?", f"Yes, Frank speaks {', '.join(RESUME_DATA['languages'])}"),
            ("What programming languages does Frank know?", ", ".join(RESUME_DATA["skills_and_technologies"]["programming_languages"])),
        ]
        
        # Combine all Q&A pairs
        all_qa_sets = [
            contact_qa, role_qa, experience_qa, cert_qa, skills_qa,
            education_qa, achievements_qa, project_qa, salary_qa, language_qa
        ]
        
        for qa_set in all_qa_sets:
            synthetic_pairs.extend([{
                'question': q,
                'answer': a,
                'feedback_score': 5,  # Synthetic data gets highest score
                'confidence': 1.0
            } for q, a in qa_set])
        
        logger.info(f"Generated {len(synthetic_pairs)} synthetic training pairs")
        return synthetic_pairs
    
    def train_model(self, training_data: List[Dict], output_dir: str = "models/fine_tuned"):
        """Fine-tune the model on collected training data."""
        logger.info("Starting model fine-tuning...")
        
        # Load model and tokenizer
        self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Create dataset
        dataset = ResumeQADataset(
            qa_pairs=training_data,
            tokenizer=self.tokenizer,
            resume_context=self.resume_context
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            save_strategy="epoch",
            evaluation_strategy="no",  # We don't have eval data for this simple case
            load_best_model_at_end=False,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=default_data_collator,
        )
        
        # Train the model
        logger.info("Training started...")
        trainer.train()
        
        # Save the fine-tuned model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Model fine-tuning completed. Saved to {output_dir}")
        
        # Save training metadata
        metadata = {
            "training_date": datetime.now().isoformat(),
            "base_model": self.model_name,
            "training_samples": len(training_data),
            "epochs": training_args.num_train_epochs,
            "batch_size": training_args.per_device_train_batch_size
        }
        
        with open(f"{output_dir}/training_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
    
    def evaluate_improvements(self, db: Session) -> Dict:
        """Evaluate how the model has improved based on recent feedback."""
        db_ops = DatabaseOperations(db)
        
        # Get feedback statistics
        feedback_stats = db_ops.get_feedback_stats()
        
        stats = {
            "total_feedback": sum(count for _, count in feedback_stats),
            "positive_feedback": sum(count for score, count in feedback_stats if score >= 4),
            "negative_feedback": sum(count for score, count in feedback_stats if score <= 2),
            "feedback_breakdown": dict(feedback_stats)
        }
        
        if stats["total_feedback"] > 0:
            stats["satisfaction_rate"] = stats["positive_feedback"] / stats["total_feedback"]
        else:
            stats["satisfaction_rate"] = 0.0
            
        logger.info(f"Model evaluation: {stats['satisfaction_rate']:.2%} satisfaction rate")
        return stats

def run_training_pipeline():
    """Main training pipeline that can be called periodically."""
    logger.info("Starting training pipeline...")
    
    try:
        # Get database session
        db = next(get_db())
        
        # Initialize trainer
        trainer = ModelTrainer()
        
        # Prepare training data
        feedback_data = trainer.prepare_training_data(db)
        synthetic_data = trainer.add_synthetic_training_data()
        
        # Combine real and synthetic data
        all_training_data = feedback_data + synthetic_data
        
        if len(all_training_data) < 5:
            logger.warning("Insufficient training data. Need at least 5 examples to train.")
            return False
        
        # Train the model
        output_dir = f"models/fine_tuned_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trainer.train_model(all_training_data, output_dir)
        
        # Evaluate improvements
        stats = trainer.evaluate_improvements(db)
        
        logger.info("Training pipeline completed successfully!")
        logger.info(f"Training stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"Training pipeline failed: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the training pipeline
    success = run_training_pipeline()
    print(f"Training pipeline {'succeeded' if success else 'failed'}") 