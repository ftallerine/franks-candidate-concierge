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
            
            # Initialize predefined Q&A for common questions
            self.predefined_qa = [
                {
                    "question": "What certifications does Frank have?",
                    "answer": "- Certified Scrum Master (CSM), Scrum Alliance, 2019\n- Microsoft Certified: Azure Administrator Associate, 2021\n- Microsoft Certified: Azure Fundamentals, 2020\n- Status: All active",
                    "keywords": ["certifications", "certification", "certified"]
                },
                {
                    "question": "What are Frank's technical skills?",
                    "answer": "- Cloud & DevOps: Azure (3+ years), Azure DevOps (3+ years), PowerShell\n- Data & Analytics: SQL (3+ years), Power BI, Microsoft Access\n- Development: Python, Git, Visual Studio, Mermaid.js\n- Productivity: Office 365 (5+ years)",
                    "keywords": ["technical skills", "technologies"]
                },
                {
                    "question": "What programming languages does Frank know?",
                    "answer": "- Languages: Python, JavaScript, HTML, CSS, PowerShell\n- Applications: Web development, data processing, automation",
                    "keywords": ["programming languages", "coding languages"]
                },
                {
                    "question": "What is Frank's current role?",
                    "answer": "- Role: Technical Business Analyst, The Marker Group\n- Since: September 2018\n- Focus: Agile optimization, stakeholder analysis, Azure DevOps releases",
                    "keywords": ["current role", "current position", "current job"]
                },
                {
                    "question": "What is Frank's experience with Azure?",
                    "answer": "Duration: 3+ years (since 2021)\nAchievements:\n- Azure DevOps releases: Reduced errors by 40%, increased frequency to 3-5/week\n- Managed compute, networking, security resources\n- Built Azure-integrated Power BI dashboards\nCertifications: Azure Administrator Associate (2021), Azure Fundamentals (2020)",
                    "keywords": ["azure experience", "experience with azure"]
                },
                {
                    "question": "How many years of business analysis experience does Frank have?",
                    "answer": "- Total: 6+ years\n- Breakdown:\n  - Technical Business Analyst, The Marker Group (since 2018)\n  - Lead Project Coordinator, John Moore Services (2017-2018)",
                    "keywords": ["business analysis experience", "years of experience as business analyst"]
                },
                {
                    "question": "What tools does Frank use for data visualization?",
                    "answer": "- Tools:\n  - Power BI: 15+ interactive dashboards built\n  - Microsoft Access: Financial reporting from complex datasets\n  - Azure DevOps Dashboards: Project metrics visualization",
                    "keywords": ["data visualization tools", "visualization tools"]
                }
            ]
            
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
            self.structured_data = RESUME_DATA
            self.resume_content = self._create_resume_text()
            
            print("\n=== Model Initialization Complete! ===")
            print("Ready to answer questions about Frank's qualifications!")
            print("Using device:", "CPU" if self.qa_pipeline.device.type == "cpu" else "GPU")
            
        except Exception as e:
            print("\n=== ERROR DURING INITIALIZATION ===")
            print(f"Error initializing model: {str(e)}")
            raise

    def _create_resume_text(self) -> str:
        """Create resume text from structured data for QA pipeline fallback."""
        data = self.structured_data
        
        # Build comprehensive resume text from structured data
        resume_parts = []
        
        # Contact info
        contact = data["contact_information"]
        resume_parts.append(f"Name: {contact['name']}")
        resume_parts.append(f"Location: {contact['location']}")
        resume_parts.append(f"Email: {contact['email']}")
        resume_parts.append(f"LinkedIn: {contact['linkedin']}")
        
        # Summary
        resume_parts.append("\nProfessional Summary:")
        resume_parts.extend(data["professional_summary"])
        
        # Experience
        resume_parts.append("\nProfessional Experience:")
        for job in data["professional_experience"]:
            resume_parts.append(f"\n{job['title']} at {job['company']} ({job['dates']})")
            resume_parts.extend(job["responsibilities"])
            if "achievements" in job:
                resume_parts.extend(job["achievements"])
        
        # Skills
        resume_parts.append("\nSkills and Technologies:")
        for category, skills in data["skills_and_technologies"].items():
            if isinstance(skills, list):
                resume_parts.append(f"{category}: {', '.join(skills)}")
        
        # Education
        edu = data["education"]
        resume_parts.append(f"\nEducation: {', '.join(edu['degrees'])} from {edu['university']}, graduated {edu['honors']} in {edu['graduation_year']}")
        
        # Certifications
        resume_parts.append("\nCertifications:")
        for cert in data["certifications"]:
            resume_parts.append(f"{cert['name']} ({cert['issuer']}, {cert['year_obtained']})")
        
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
        
        # Fall back to existing structured data matching
        q = question.lower()
        
        # Contact information
        if any(term in q for term in ["contact", "email", "linkedin", "reach"]):
            contact = self.structured_data["contact_information"]
            if "email" in q:
                return contact["email"], 1.0
            elif "linkedin" in q:
                return contact["linkedin"], 1.0
            else:
                return f"Email: {contact['email']}, LinkedIn: {contact['linkedin']}", 1.0
        
        # Location/where questions
        if any(term in q for term in ["where", "location", "based", "live"]):
            if "work" in q:
                return "Frank works at The Marker Group in the Houston metropolitan area", 1.0
            else:
                return self.structured_data["contact_information"]["location"], 1.0
        
        # Current role and job search
        if "current role" in q or "current position" in q or "current job" in q:
            current_job = self.structured_data["professional_experience"][0]
            return f"{current_job['title']} at {current_job['company']} ({current_job['dates']})", 1.0
        
        if any(term in q for term in ["looking for", "seeking", "job search", "desired role", "target role"]):
            criteria = self.structured_data["job_search_criteria"]
            return f"Seeking {criteria['desired_role']} in {criteria['preferred_location']}. {criteria['other_criteria']}", 1.0
            
        # Certifications
        if "certification" in q or "certified" in q:
            certs = []
            for cert in self.structured_data["certifications"]:
                if "when" in q or "year" in q:
                    certs.append(f"{cert['name']} ({cert['issuer']}, {cert['year_obtained']})")
                else:
                    certs.append(f"{cert['name']} ({cert['issuer']})")
            return ", ".join(certs), 1.0
            
        # Experience questions with specific years
        if any(term in q for term in ["experience", "years"]):
            highlights = self.structured_data["experience_highlights"]
            if "business analyst" in q or "ba" in q:
                return highlights["total_ba_experience"], 1.0
            elif "scrum" in q:
                return highlights["scrum_master_experience"], 1.0
            elif "azure" in q:
                return highlights["azure_experience"], 1.0
            elif "sql" in q:
                return highlights["sql_experience"], 1.0
            else:
                return f"Total Business Analysis experience: {highlights['total_ba_experience']}, Scrum Master: {highlights['scrum_master_experience']}, Azure: {highlights['azure_experience']}, SQL: {highlights['sql_experience']}", 1.0
        
        # Programming languages (specific check first)
        if ("programming language" in q or "programming" in q) and ("language" in q or "code" in q or "coding" in q):
            return ", ".join(self.structured_data["skills_and_technologies"]["programming_languages"]), 1.0
        
        # Technical skills (broader category)
        if "technical skill" in q or "technology" in q or "tools" in q:
            skills = []
            skills.extend(self.structured_data["skills_and_technologies"]["cloud_and_net"])
            skills.extend(self.structured_data["skills_and_technologies"]["tools"])
            return ", ".join(skills), 1.0
            
        # Business skills
        if "business skill" in q or "business analysis" in q or "ba skill" in q:
            ba_skills = self.structured_data["skills_and_technologies"]["business_analysis"]
            return ", ".join(ba_skills), 1.0
        
        # Agile and Scrum skills
        if "agile" in q or "scrum" in q:
            agile_skills = self.structured_data["skills_and_technologies"]["agile_and_scrum"]
            return ", ".join(agile_skills), 1.0
        
        # Soft skills
        if "soft skill" in q or "communication" in q or "leadership" in q:
            return ", ".join(self.structured_data["skills_and_technologies"]["soft_skills"]), 1.0
        
        # Achievements and metrics
        if any(term in q for term in ["achievement", "accomplish", "metrics", "results", "impact"]):
            achievements = []
            for item in self.structured_data["key_achievements_summary"]:
                achievements.append(item["achievement"])
            return ". ".join(achievements), 1.0
        
        # Experience with specific technology (enhanced)
        tech_mapping = {
            "azure": ("azure_experience", "3+ years of Azure experience including Azure DevOps, Azure Portal, and Azure administration"),
            "sql": ("sql_experience", "3+ years of SQL experience for database design, reporting, and data analysis"),
            "python": ("programming", "Proficient in Python for data processing, ML pipelines, and automation scripts"),
            "power bi": ("visualization", "Built 15+ Power BI dashboards for real-time insights and decision-making"),
            "git": ("version_control", "Experienced with Git version control and collaborative development"),
            ".net": ("framework", "Experienced in .NET environments and framework development")
        }
        
        for tech, (category, description) in tech_mapping.items():
            if tech in q:
                # Also check for specific experiences in job history
                experiences = [description]
                for job in self.structured_data["professional_experience"]:
                    for resp in job["responsibilities"]:
                        if tech.lower() in resp.lower():
                            experiences.append(f"At {job['company']}: {resp}")
                return " ".join(experiences), 1.0
                    
        # Languages (human languages only, since programming languages handled above)
        if "language" in q and not ("programming" in q or "coding" in q or "technical" in q):
            if "speak" in q or "human" in q or "foreign" in q:
                return ", ".join(self.structured_data["languages"]), 1.0
            else:
                return ", ".join(self.structured_data["languages"]), 1.0
                
        # Education
        if "education" in q or "degree" in q or "university" in q or "college" in q:
            edu = self.structured_data["education"]
            if "when" in q or "year" in q or "graduate" in q:
                return f"Frank graduated in {edu['graduation_year']} with {edu['degrees'][0]} and {edu['degrees'][1]} from {edu['university']}, {edu['honors']}", 1.0
            else:
                return f"{edu['degrees'][0]} and {edu['degrees'][1]} from {edu['university']}, graduated {edu['honors']} in {edu['graduation_year']}", 1.0
            
        # Projects
        if "project" in q or "medical record" in q or "ner" in q or "ai" in q:
            project = self.structured_data["projects"][0]
            description = " ".join(project["description"])
            achievements = " ".join(project["achievements"])
            return f"{project['name']}: {description} {achievements}", 1.0
            
        # Salary expectations
        if "salary" in q or "compensation" in q or "pay" in q or "money" in q:
            salary = self.structured_data["salary_expectations"]
            return f"Target salary: {salary['target']}, {salary['negotiable']}. {salary['additional_notes']}", 1.0
            
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