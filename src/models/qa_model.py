from pathlib import Path
import torch
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
from .resume_data import RESUME_DATA
from .response_templates import ResponseFormatter
from .gpt_service import GPTService

class QAModel:
    def __init__(self):
        try:
            print("\n=== Starting Model Initialization ===")
            
            # Initialize response formatter
            self.formatter = ResponseFormatter()
            
            # Initialize predefined Q&A for common questions
            self.predefined_qa = [
                {
                    "question": "What certifications does Frank have?",
                    "answer": self.formatter.format_certifications(RESUME_DATA["certifications"]),
                    "keywords": ["certifications", "certification", "certified"]
                },
                {
                    "question": "What are Frank's technical skills?",
                    "answer": self.formatter.format_skills(RESUME_DATA["skills_and_technologies"]),
                    "keywords": ["technical skills", "technologies"]
                },
                {
                    "question": "What programming languages does Frank know?",
                    "answer": self.formatter.format_skills({
                        "Programming Languages": RESUME_DATA["skills_and_technologies"]["programming_languages"]
                    }),
                    "keywords": ["programming languages", "coding languages"]
                },
                {
                    "question": "What is Frank's current role?",
                    "answer": self.formatter.format_experience([RESUME_DATA["professional_experience"][0]]),
                    "keywords": ["current role", "current position", "current job"]
                },
                {
                    "question": "What is Frank's experience with Azure?",
                    "answer": self.formatter.format_achievements(
                        RESUME_DATA["key_achievements_summary"],
                        filter_tags=["Azure", "Azure DevOps"]
                    ),
                    "keywords": ["azure experience", "experience with azure"]
                },
                {
                    "question": "How many years of business analysis experience does Frank have?",
                    "answer": f"Frank has {RESUME_DATA['experience_highlights']['total_ba_experience']} of business analysis experience.",
                    "keywords": ["business analysis experience", "years of experience as business analyst"]
                },
                {
                    "question": "What tools does Frank use for data visualization?",
                    "answer": self.formatter.format_skills({
                        "Data Visualization Tools": [
                            skill for skill in RESUME_DATA["skills_and_technologies"]["tools"]
                            if any(tool in skill.lower() for tool in ["power bi", "visualization", "dashboard"])
                        ]
                    }),
                    "keywords": ["data visualization tools", "visualization tools"]
                }
            ]
            
            # Load structured data immediately (fast)
            print("Loading resume data...")
            self.structured_data = RESUME_DATA
            self.resume_content = self._create_resume_text()
            
            # Initialize GPT service
            self.gpt_service = GPTService()
            
            # Lazy loading for ML model (will be loaded on first use)
            self.model = None
            self.tokenizer = None
            self.qa_pipeline = None
            self.model_name = "deepset/minilm-uncased-squad2"
            self._model_loaded = False
            
            print("\n=== Model Initialization Complete! ===")
            print("Ready to answer questions about Frank's qualifications!")
            print("ML model will be loaded on first use for better startup performance.")
            
        except Exception as e:
            print("\n=== ERROR DURING INITIALIZATION ===")
            print(f"Error initializing model: {str(e)}")
            raise

    def _load_ml_model(self):
        """Lazy load the ML model only when needed."""
        if not self._model_loaded:
            try:
                print(f"\n=== Loading ML Model ({self.model_name}) ===")
                print("This may take 30-60 seconds on first use...")
                
                self.model = AutoModelForQuestionAnswering.from_pretrained(
                    self.model_name, 
                    force_download=False,  # Changed to False for faster loading
                    local_files_only=True  # Use cached version if available
                )
                
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name, 
                    force_download=False,
                    local_files_only=True
                )
                
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=-1,  # Force CPU
                    handle_impossible_answer=True,
                    max_answer_len=150,
                    max_seq_len=512,
                    doc_stride=128
                )
                
                self._model_loaded = True
                print("=== ML Model Loaded Successfully! ===")
                
            except Exception as e:
                print(f"Error loading ML model: {str(e)}")
                # Fallback to structured data only
                self._model_loaded = False

    def _create_resume_text(self) -> str:
        """Create resume text from structured data for QA pipeline fallback."""
        data = self.structured_data
        
        # Build comprehensive resume text from structured data
        resume_parts = []
        
        # Contact info
        resume_parts.append(self.formatter.format_contact(data["contact_information"]))
        
        # Summary
        resume_parts.append("\nProfessional Summary:")
        resume_parts.extend(data["professional_summary"])
        
        # Experience
        resume_parts.append(self.formatter.format_experience(data["professional_experience"]))
        
        # Skills
        resume_parts.append(self.formatter.format_skills(data["skills_and_technologies"]))
        
        # Education
        resume_parts.append(self.formatter.format_education(data["education"]))
        
        # Certifications
        resume_parts.append(self.formatter.format_certifications(data["certifications"]))
        
        # Projects
        resume_parts.append(self.formatter.format_projects(data["projects"]))
        
        # Languages
        resume_parts.append(self.formatter.format_languages(data["languages"]))
        
        return "\n".join(resume_parts)
    
    def _get_structured_answer(self, question: str) -> tuple[str, float]:
        """Get answer from structured data based on question type."""
        q_lower = question.lower()
        
        # First, check predefined Q&A for keyword matches
        for qa in self.predefined_qa:
            for keyword in qa["keywords"]:
                keyword_words = keyword.lower().split()
                if all(word in q_lower for word in keyword_words):
                    return qa["answer"], 1.0
        
        q = question.lower()
        
        # Education (moved up, and includes "school")
        if any(term in q for term in ["education", "degree", "university", "college", "school"]):
            return self.formatter.format_education(self.structured_data["education"]), 1.0
        
        # Work location
        if any(term in q for term in ["where", "location", "based", "live"]):
            if "work" in q or "job" in q or "company" in q or "office" in q:
                return "Frank works at The Marker Group in the Houston metropolitan area", 1.0
            elif "school" in q or "university" in q or "college" in q or "education" in q:
                # Already handled above, but just in case
                return self.formatter.format_education(self.structured_data["education"]), 1.0
            else:
                return f"Frank is located in {self.structured_data['contact_information']['location']}", 1.0
        
        # Contact information
        if any(term in q for term in ["contact", "email", "linkedin", "reach"]):
            return self.formatter.format_contact(self.structured_data["contact_information"]), 1.0
        
        # Current role and job search
        if "current role" in q or "current position" in q or "current job" in q:
            return self.formatter.format_experience([self.structured_data["professional_experience"][0]]), 1.0
        
        if any(term in q for term in ["looking for", "seeking", "job search", "desired role", "target role"]):
            criteria = self.structured_data["job_search_criteria"]
            return f"Seeking {criteria['desired_role']} in {criteria['preferred_location']}. {criteria['other_criteria']}", 1.0
            
        # Certifications
        if "certification" in q or "certified" in q:
            return self.formatter.format_certifications(self.structured_data["certifications"]), 1.0
            
        # Experience questions with specific years
        if any(term in q for term in ["experience", "years"]):
            highlights = self.structured_data["experience_highlights"]
            if "business analyst" in q or "ba" in q:
                return f"Frank has {highlights['total_ba_experience']} of business analysis experience.", 1.0
            elif "scrum" in q:
                return f"Frank has {highlights['scrum_master_experience']} of Scrum Master experience.", 1.0
            elif "azure" in q:
                return f"Frank has {highlights['azure_experience']} of Azure experience.", 1.0
            elif "sql" in q:
                return f"Frank has {highlights['sql_experience']} of SQL experience.", 1.0
            else:
                return f"Frank's experience:\n• Business Analysis: {highlights['total_ba_experience']}\n• Scrum Master: {highlights['scrum_master_experience']}\n• Azure: {highlights['azure_experience']}\n• SQL: {highlights['sql_experience']}", 1.0
        
        # Programming languages (specific check first)
        if ("programming language" in q or "programming" in q) and ("language" in q or "code" in q or "coding" in q):
            return self.formatter.format_skills({
                "Programming Languages": self.structured_data["skills_and_technologies"]["programming_languages"]
            }), 1.0
        
        # Technical skills (broader category)
        if "technical skill" in q or "technology" in q or "tools" in q:
            return self.formatter.format_skills({
                "Cloud & Networking": self.structured_data["skills_and_technologies"]["cloud_and_net"],
                "Tools & Technologies": self.structured_data["skills_and_technologies"]["tools"]
            }), 1.0
            
        # Business skills
        if "business skill" in q or "business analysis" in q or "ba skill" in q:
            return self.formatter.format_skills({
                "Business Analysis": self.structured_data["skills_and_technologies"]["business_analysis"]
            }), 1.0
        
        # Agile and Scrum skills
        if "agile" in q or "scrum" in q:
            return self.formatter.format_skills({
                "Agile & Scrum": self.structured_data["skills_and_technologies"]["agile_and_scrum"]
            }), 1.0
        
        # Soft skills
        if "soft skill" in q or "communication" in q or "leadership" in q:
            return self.formatter.format_skills({
                "Soft Skills": self.structured_data["skills_and_technologies"]["soft_skills"]
            }), 1.0
        
        # Achievements and metrics
        if any(term in q for term in ["achievement", "accomplish", "metrics", "results", "impact"]):
            return self.formatter.format_achievements(self.structured_data["key_achievements_summary"]), 1.0
        
        # Experience with specific technology (enhanced)
        tech_mapping = {
            "azure": ("Azure", "Azure DevOps"),
            "sql": ("SQL", "Database"),
            "python": ("Python", "Programming"),
            "power bi": ("Power BI", "Data Visualization"),
            "git": ("Git", "Version Control"),
            ".net": (".NET", "Framework")
        }
        
        for tech, (primary_tag, secondary_tag) in tech_mapping.items():
            if tech in q:
                return self.formatter.format_achievements(
                    self.structured_data["key_achievements_summary"],
                    filter_tags=[primary_tag, secondary_tag]
                ), 1.0
                    
        # Languages (human languages only, since programming languages handled above)
        if "language" in q and not ("programming" in q or "coding" in q or "technical" in q):
            return self.formatter.format_languages(self.structured_data["languages"]), 1.0
                
        # Projects
        if "project" in q or "medical record" in q or "ner" in q or "ai" in q:
            return self.formatter.format_projects(self.structured_data["projects"]), 1.0
            
        # Salary expectations
        if "salary" in q or "compensation" in q or "pay" in q or "money" in q:
            return self.formatter.format_salary_expectations(self.structured_data["salary_expectations"]), 1.0
            
        return "", 0.0
    
    def _get_relevant_context(self, question: str) -> str:
        """Return only the relevant sections of the resume as context based on the question."""
        q = question.lower()
        context_parts = []

        # Education-related
        if any(term in q for term in ["school", "university", "college", "education", "degree", "graduate"]):
            context_parts.append(self.formatter.format_education(self.structured_data["education"]))

        # Certification-related
        if any(term in q for term in ["certification", "certified", "certificate", "scrum", "azure certified"]):
            context_parts.append(self.formatter.format_certifications(self.structured_data["certifications"]))

        # Experience-related
        if any(term in q for term in ["experience", "work history", "job", "role", "position", "responsibility"]):
            context_parts.append(self.formatter.format_experience(self.structured_data["professional_experience"]))

        # Skills/technologies
        if any(term in q for term in ["skill", "technology", "tools", "programming", "language", "framework"]):
            context_parts.append(self.formatter.format_skills(self.structured_data["skills_and_technologies"]))

        # Achievements
        if "achievement" in q or "accomplishment" in q or "result" in q:
            context_parts.append(self.formatter.format_achievements(self.structured_data["key_achievements_summary"]))

        # Projects
        if "project" in q:
            context_parts.append(self.formatter.format_projects(self.structured_data["projects"]))

        # Contact/location
        if any(term in q for term in ["contact", "email", "linkedin", "location", "based", "live"]):
            context_parts.append(self.formatter.format_contact(self.structured_data["contact_information"]))

        # If no keywords matched, fall back to summary
        if not context_parts:
            context_parts.append("\n".join(self.structured_data.get("professional_summary", [])))

        return "\n".join(context_parts)

    def answer_question(self, question: str) -> tuple[str, float, str]:
        """Answer a question about the resume using structured data, ML, then GPT fallback."""
        try:
            # Try to get answer from structured data first
            answer, confidence = self._get_structured_answer(question)
            if answer and confidence > 0.7:
                return self.formatter.add_confidence_note(answer, confidence), confidence, "structured"

            # Load ML model if not already loaded
            if not self._model_loaded:
                self._load_ml_model()

            # Fall back to QA model with context filtering (only if model loaded successfully)
            if self._model_loaded and self.qa_pipeline:
                try:
                    context = self._get_relevant_context(question)
                    result = self.qa_pipeline(
                        question=question,
                        context=context,
                        max_answer_len=150,
                        handle_impossible_answer=True
                    )

                    answer = result["answer"].strip()
                    confidence = result["score"]

                    if answer and confidence > 0.7:
                        return self.formatter.add_confidence_note(answer, confidence, "AI model"), confidence, "qa_model"
                except Exception as ml_error:
                    print(f"ML model error: {str(ml_error)}")
                    # Continue to GPT fallback

            # Final fallback: GPT
            try:
                gpt_answer = self.gpt_service.get_completion(question)
                return self.formatter.add_confidence_note(gpt_answer, 0.6, "GPT fallback"), 0.6, "gpt"
            except Exception as gpt_error:
                print(f"GPT error: {str(gpt_error)}")
                # Ultimate fallback - use structured data with lower confidence
                answer, _ = self._get_structured_answer(question)
                if answer:
                    return self.formatter.add_confidence_note(answer, 0.5, "structured fallback"), 0.5, "structured_fallback"
                return "I'm having trouble processing your question right now. Please try asking about Frank's certifications, experience, or skills.", 0.0, "fallback"

        except Exception as e:
            print(f"Error processing question: {str(e)}")
            return "I encountered an error while processing your question. Please try again.", 0.0, "error"