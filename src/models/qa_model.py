from pathlib import Path
import torch
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
from .resume_data import RESUME_DATA

class QAModel:
    def __init__(self):
        try:
            # Use a smaller model for faster loading
            model_name = "deepset/minilm-uncased-squad2"
            
            print("\n=== Starting Model Initialization ===")
            print(f"Loading {model_name}...")
            
            # Initialize progress indicators
            steps = ["Loading model", "Loading tokenizer", "Setting up pipeline", "Loading resume data"]
            total_steps = len(steps)
            
            print(f"\n[1/{total_steps}] Loading model...")
            self.model = AutoModelForQuestionAnswering.from_pretrained(model_name, force_download=True)
            
            print(f"[2/{total_steps}] Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, force_download=True)
            
            print(f"[3/{total_steps}] Setting up QA pipeline...")
            self.qa_pipeline = pipeline(
                "question-answering",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1,  # Force CPU
                handle_impossible_answer=True,
                max_answer_len=150,  # Allow longer answers for better context
                max_seq_len=512,  # Maximum sequence length
                doc_stride=128  # Overlap between chunks when splitting long documents
            )
            
            print(f"[4/{total_steps}] Loading resume data...")
            self.resume_content = self._load_resume()
            self.structured_data = RESUME_DATA
            
            print("\n=== Model Initialization Complete! ===")
            print("Ready to answer questions about Frank's qualifications!")
            print("Using device:", "CPU" if self.qa_pipeline.device.type == "cpu" else "GPU")
            
        except Exception as e:
            print("\n=== ERROR DURING INITIALIZATION ===")
            print(f"Error initializing model: {str(e)}")
            raise

    def _load_resume(self) -> str:
        """Load the resume content from the data directory."""
        resume_path = Path("data/resume.txt")
        if not resume_path.exists():
            raise FileNotFoundError("Resume file not found in data directory")
        
        with open(resume_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def _get_structured_answer(self, question: str) -> tuple[str, float]:
        """Get answer from structured data based on question type."""
        q = question.lower()
        
        # Current role
        if "current role" in q or "current position" in q:
            return self.structured_data["current_role"], 1.0
            
        # Certifications
        if "certification" in q:
            return ", ".join(self.structured_data["certifications"]), 1.0
            
        # Technical skills
        if "technical skill" in q or "programming" in q or "technology" in q:
            skills = []
            skills.extend(self.structured_data["skills_and_technologies"]["cloud_and_net"])
            skills.extend(self.structured_data["skills_and_technologies"]["tools"])
            return ", ".join(skills), 1.0
            
        # Experience with specific technology
        for tech in ["azure", "python", "sql", "git", ".net"]:
            if tech in q:
                # Find relevant experiences
                experiences = []
                if tech.lower() in [t.lower() for t in self.structured_data["skills_and_technologies"]["cloud_and_net"]]:
                    experiences.append(f"Skilled in {tech}")
                if tech.lower() in [t.lower() for t in self.structured_data["skills_and_technologies"]["tools"]]:
                    experiences.append(f"Proficient with {tech}")
                for job in self.structured_data["professional_experience"]:
                    for resp in job["responsibilities"]:
                        if tech.lower() in resp.lower():
                            experiences.append(resp)
                if experiences:
                    return " ".join(experiences), 1.0
                    
        # Languages
        if "language" in q or "programming language" in q:
            tech_langs = ["Python", "C++", "JavaScript", "HTML", "CSS"]
            human_langs = self.structured_data["languages"]
            if "programming" in q or "coding" in q:
                return ", ".join(tech_langs), 1.0
            elif "speak" in q or "human" in q:
                return ", ".join(human_langs), 1.0
            else:
                return f"Programming Languages: {', '.join(tech_langs)}. Human Languages: {', '.join(human_langs)}", 1.0
                
        # Education
        if "education" in q or "degree" in q or "university" in q:
            edu = self.structured_data["education"]
            return f"{edu['degrees'][0]} and {edu['degrees'][1]} from {edu['university']}, {edu['honors']}", 1.0
            
        # Salary expectations
        if "salary" in q or "compensation" in q or "pay" in q:
            salary = self.structured_data["salary_expectations"]
            return f"{salary['target']}, {salary['negotiable']}. {salary['additional_notes']}", 1.0
            
        return "", 0.0
    
    def answer_question(self, question: str) -> tuple[str, float]:
        """Answer a question about the resume using structured data first, falling back to QA model."""
        try:
            # Try to get answer from structured data first
            answer, confidence = self._get_structured_answer(question)
            if answer and confidence > 0.7:
                return answer, confidence
            
            # Fall back to QA model
            result = self.qa_pipeline(
                question=question,
                context=self.resume_content,
                max_answer_len=150,
                handle_impossible_answer=True
            )
            
            answer = result["answer"].strip()
            confidence = result["score"]
            
            # If answer is empty but confidence is high, something went wrong
            if not answer and confidence > 0.5:
                return "I apologize, but I couldn't extract a clear answer from the resume. Please try rephrasing your question.", 0.5
                
            return answer, confidence
            
        except Exception as e:
            print(f"Error processing question: {str(e)}")
            return "I encountered an error while processing your question. Please try again.", 0.0