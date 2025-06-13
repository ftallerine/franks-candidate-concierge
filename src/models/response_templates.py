"""Response templates for formatting answers in a natural, professional way."""

from typing import List, Dict, Any, Optional
from datetime import datetime

class ResponseFormatter:
    """Formats structured data into natural, professional responses."""
    
    @staticmethod
    def format_certifications(certs: List[Dict[str, str]]) -> str:
        """Format certifications into a professional bullet list."""
        if not certs:
            return "No certifications found."
            
        formatted = "Frank holds the following certifications:\n"
        for cert in certs:
            status = f" — Status: {cert['status']}" if 'status' in cert else ""
            formatted += f"• {cert['name']} ({cert['issuer']}, {cert['year_obtained']}){status}\n"
        return formatted.strip()
    
    @staticmethod
    def format_skills(skills: Dict[str, List[str]]) -> str:
        """Format skills into categorized sections with descriptions."""
        if not skills:
            return "No skills found."
            
        formatted = ""
        for category, skill_list in skills.items():
            if not skill_list:
                continue
                
            # Format category name for display
            category_name = category.replace('_', ' ').title()
            formatted += f"\n{category_name}:\n"
            
            for skill in skill_list:
                # Handle skills with descriptions (after dash)
                if " - " in skill:
                    skill_name, description = skill.split(" - ", 1)
                    formatted += f"• {skill_name}: {description}\n"
                else:
                    formatted += f"• {skill}\n"
                    
        return formatted.strip()
    
    @staticmethod
    def format_experience(experience: List[Dict[str, Any]]) -> str:
        """Format professional experience with achievements."""
        if not experience:
            return "No professional experience found."
            
        formatted = "Professional Experience:\n"
        for job in experience:
            formatted += f"\n{job['title']} at {job['company']} ({job['dates']})\n"
            
            if job.get('responsibilities'):
                formatted += "\nKey Responsibilities:\n"
                for resp in job['responsibilities']:
                    formatted += f"• {resp}\n"
                    
            if job.get('achievements'):
                formatted += "\nNotable Achievements:\n"
                for achievement in job['achievements']:
                    formatted += f"• {achievement}\n"
                    
        return formatted.strip()
    
    @staticmethod
    def format_achievements(achievements: List[Dict[str, Any]], filter_tags: Optional[List[str]] = None) -> str:
        """Format achievements with optional tag filtering."""
        if not achievements:
            return "No achievements found."
            
        # Filter achievements by tags if provided
        if filter_tags:
            filtered = [
                a for a in achievements 
                if any(tag.lower() in [t.lower() for t in a.get('tags', [])] 
                      for tag in filter_tags)
            ]
            if not filtered:
                return f"No achievements found matching tags: {', '.join(filter_tags)}"
            achievements = filtered
            
        formatted = "Key Achievements:\n"
        for achievement in achievements:
            formatted += f"• {achievement['achievement']}\n"
            
        return formatted.strip()
    
    @staticmethod
    def format_education(education: Dict[str, Any]) -> str:
        """Format education information."""
        if not education:
            return "No education information found."
            
        degrees = " and ".join(education['degrees'])
        formatted = f"Education: {degrees}\n"
        formatted += f"University: {education['university']}\n"
        formatted += f"Graduation: {education['graduation_year']} ({education['honors']})\n"
        
        if education.get('additional_info'):
            formatted += "\nAdditional Information:\n"
            for info in education['additional_info']:
                formatted += f"• {info}\n"
                
        return formatted.strip()
    
    @staticmethod
    def format_contact(contact: Dict[str, str]) -> str:
        """Format contact information."""
        if not contact:
            return "No contact information found."
            
        formatted = "Contact Information:\n"
        formatted += f"• Email: {contact['email']}\n"
        formatted += f"• LinkedIn: {contact['linkedin']}\n"
        formatted += f"• Location: {contact['location']}\n"
        
        return formatted.strip()
    
    @staticmethod
    def format_projects(projects: List[Dict[str, Any]]) -> str:
        """Format project information with achievements."""
        if not projects:
            return "No projects found."
            
        formatted = "Projects:\n"
        for project in projects:
            formatted += f"\n{project['name']} ({project['status']}, {project['completion_date']})\n"
            
            if project.get('description'):
                formatted += "\nDescription:\n"
                for desc in project['description']:
                    formatted += f"• {desc}\n"
                    
            if project.get('achievements'):
                formatted += "\nAchievements:\n"
                for achievement in project['achievements']:
                    formatted += f"• {achievement}\n"
                    
            if project.get('technologies_used'):
                formatted += "\nTechnologies Used:\n"
                formatted += f"• {', '.join(project['technologies_used'])}\n"
                
        return formatted.strip()
    
    @staticmethod
    def add_confidence_note(answer: str, confidence: float, source: str = "structured data") -> str:
        """Add a confidence note to the answer."""
        if confidence >= 0.95:
            return f"{answer}\n\n(This answer is based on structured data.)"
        elif confidence >= 0.7:
            return f"{answer}\n\n(This answer is generated by AI and is likely accurate.)"
        else:
            return f"{answer}\n\n(This response has low confidence. Please verify details.)"
    
    @staticmethod
    def format_salary_expectations(salary: Dict[str, str]) -> str:
        """Format salary expectations."""
        if not salary:
            return "No salary information available."
            
        formatted = "Salary Expectations:\n"
        formatted += f"• Target: {salary['target']}\n"
        formatted += f"• Negotiable: {salary['negotiable']}\n"
        
        if salary.get('additional_notes'):
            formatted += f"\nAdditional Notes:\n• {salary['additional_notes']}\n"
            
        return formatted.strip()
    
    @staticmethod
    def format_languages(languages: List[str]) -> str:
        """Format language proficiencies."""
        if not languages:
            return "No language information available."
            
        formatted = "Languages:\n"
        for lang in languages:
            formatted += f"• {lang}\n"
            
        return formatted.strip() 