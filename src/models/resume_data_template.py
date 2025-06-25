"""
Template for structured resume data.
This file uses environment variable placeholders (e.g., "ENV::VARIABLE_NAME") for sensitive data only.
Non-sensitive professional information is included directly.
"""

RESUME_DATA_TEMPLATE = {
    "keywords": [
        "Business Analyst", "Scrum Master", "Azure", "Python", "SQL", "Power BI"
    ],
    
    "contact_information": {
        "name": "ENV::CONTACT_NAME",
        "location": "ENV::CONTACT_LOCATION", 
        "email": "ENV::CONTACT_EMAIL",
        "linkedin": "ENV::CONTACT_LINKEDIN"
    },
    
    "professional_summary": [
        "Experienced Business Analyst and Scrum Master with expertise in Azure cloud solutions and data analytics",
        "Proven track record in stakeholder management, requirements gathering, and agile project delivery"
    ],
    
    "certifications": [
        {
            "name": "Microsoft Azure Fundamentals",
            "issuer": "Microsoft",
            "year_obtained": "2023",
            "status": "Active"
        },
        {
            "name": "Certified Scrum Master",
            "issuer": "Scrum Alliance", 
            "year_obtained": "2022",
            "status": "Active"
        }
    ],
    
    "professional_experience": [
        {
            "company": "ENV::EXP_1_COMPANY",
            "role": "Senior Business Analyst / Scrum Master",
            "title": "ENV::EXP_1_TITLE",
            "dates": "2020 - Present",
            "duration": "4+ years",
            "status": "Current",
            "responsibilities": [
                "Lead cross-functional teams in agile software development projects using Scrum methodology",
                "Gather and analyze business requirements, creating detailed documentation and user stories",
                "Facilitate sprint planning, daily standups, retrospectives, and stakeholder meetings"
            ],
            "achievements": [
                "Successfully delivered 15+ projects on time and within budget",
                "Improved team velocity by 30% through process optimization and stakeholder alignment"
            ]
        }
    ],
    
    "skills_and_technologies": {
        "cloud_and_net": ["Azure", ".NET"],
        "tools": ["SQL", "Power BI", "Git", "Python"],
        "agile_and_scrum": ["Agile", "Scrum", "Sprint planning"],
        "business_analysis": ["Requirements gathering", "Stakeholder management"],
        "soft_skills": ["Communication", "Problem solving"],
        "programming_languages": ["Python", "JavaScript", "HTML", "CSS"]
    },
    
    "projects": [
        {
            "name": "Healthcare AI Analytics Platform",
            "status": "Completed",
            "completion_date": "2024",
            "description": [
                "Led development of AI-powered analytics platform for healthcare data processing",
                "Implemented natural language processing for medical record analysis"
            ],
            "achievements": [
                "Reduced data processing time by 60% and improved accuracy of medical insights"
            ],
            "technologies_used": ["Python", "spaCy", "Machine Learning"],
            "tags": ["AI", "Healthcare", "NLP"]
        }
    ],
    
    "education": {
        "university": "University of Technology",
        "degrees": ["Bachelor of Science in Information Systems", "Master of Business Administration"],
        "honors": "Magna Cum Laude",
        "graduation_year": "2018",
        "additional_info": ["Specialized in Business Analytics and Information Systems"],
        "graduation_status": "Completed"
    },
    
    "languages": ["English (Native)", "Spanish (Conversational)"],
    
    "salary_expectations": {
        "target": "ENV::SALARY_TARGET",
        "negotiable": "ENV::SALARY_NEGOTIABLE", 
        "additional_notes": "ENV::SALARY_NOTES"
    },
    
    "job_search_criteria": {
        "desired_role": "Senior Business Analyst / Scrum Master",
        "preferred_location": "ENV::JOB_LOCATION",
        "salary_range": "ENV::JOB_SALARY_RANGE",
        "other_criteria": "Remote-friendly positions with growth opportunities"
    },
    
    "experience_highlights": {
        "total_ba_experience": "6+ years in Business Analysis",
        "scrum_master_experience": "4+ years as Certified Scrum Master",
        "azure_experience": "3+ years with Azure cloud solutions"
    },
    
    "industry_expertise": [
        "Healthcare Technology",
        "Financial Services"
    ],
    
    "key_achievements_summary": [
        {
            "achievement": "Led digital transformation initiatives resulting in 40% efficiency improvement"
        },
        {
            "achievement": "Managed stakeholder relationships across 10+ departments and external vendors"
        },
        {
            "achievement": "Developed and implemented data governance frameworks for enterprise-level projects"
        }
    ]
} 