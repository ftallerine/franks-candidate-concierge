"""
Template for structured resume data.
This file uses environment variable placeholders (e.g., "ENV::VARIABLE_NAME").
The application will dynamically load these values from your .env file or hosting environment.
This template is safe to commit to version control.
"""

RESUME_DATA_TEMPLATE = {
    "keywords": [
        "ENV::KEYWORD_1", "ENV::KEYWORD_2", "ENV::KEYWORD_3",
        "ENV::KEYWORD_4", "ENV::KEYWORD_5", "ENV::KEYWORD_6"
    ],
    
    "contact_information": {
        "name": "ENV::CONTACT_NAME",
        "location": "ENV::CONTACT_LOCATION",
        "email": "ENV::CONTACT_EMAIL",
        "linkedin": "ENV::CONTACT_LINKEDIN"
    },
    
    "professional_summary": [
        "ENV::PROFESSIONAL_SUMMARY_1",
        "ENV::PROFESSIONAL_SUMMARY_2"
    ],
    
    "certifications": [
        {
            "name": "ENV::CERT_1_NAME",
            "issuer": "ENV::CERT_1_ISSUER",
            "year_obtained": "ENV::CERT_1_YEAR",
            "status": "Active"
        },
        {
            "name": "ENV::CERT_2_NAME",
            "issuer": "ENV::CERT_2_ISSUER",
            "year_obtained": "ENV::CERT_2_YEAR",
            "status": "Active"
        }
    ],
    
    "professional_experience": [
        {
            "company": "ENV::EXP_1_COMPANY",
            "role": "ENV::EXP_1_ROLE",
            "title": "ENV::EXP_1_TITLE",
            "dates": "ENV::EXP_1_DATES",
            "duration": "ENV::EXP_1_DURATION", 
            "status": "Current",
            "responsibilities": [
                "ENV::EXP_1_RESP_1",
                "ENV::EXP_1_RESP_2",
                "ENV::EXP_1_RESP_3"
            ],
            "achievements": [
                "ENV::EXP_1_ACHIEVE_1",
                "ENV::EXP_1_ACHIEVE_2"
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
            "name": "ENV::PROJ_1_NAME",
            "status": "Completed",
            "completion_date": "ENV::PROJ_1_DATE",
            "description": [
                "ENV::PROJ_1_DESC_1",
                "ENV::PROJ_1_DESC_2"
            ],
            "achievements": [
                "ENV::PROJ_1_ACHIEVE_1"
            ],
            "technologies_used": ["Python", "spaCy", "Machine Learning"],
            "tags": ["AI", "Healthcare", "NLP"]
        }
    ],
    
    "education": {
        "university": "ENV::EDU_UNIVERSITY",
        "degrees": ["ENV::EDU_DEGREE_1", "ENV::EDU_DEGREE_2"],
        "honors": "ENV::EDU_HONORS",
        "graduation_year": "ENV::EDU_YEAR",
        "additional_info": ["ENV::EDU_INFO_1"],
        "graduation_status": "Completed"
    },
    
    "languages": ["ENV::LANGUAGE_1"],
    
    "salary_expectations": {
        "target": "ENV::SALARY_TARGET",
        "negotiable": "ENV::SALARY_NEGOTIABLE",
        "additional_notes": "ENV::SALARY_NOTES"
    },
    
    "job_search_criteria": {
        "desired_role": "ENV::JOB_DESIRED_ROLE",
        "preferred_location": "ENV::JOB_LOCATION",
        "salary_range": "ENV::JOB_SALARY_RANGE",
        "other_criteria": "ENV::JOB_CRITERIA"
    },
    
    "experience_highlights": {
        "total_ba_experience": "ENV::HIGHLIGHT_BA_EXP",
        "scrum_master_experience": "ENV::HIGHLIGHT_SCRUM_EXP",
        "azure_experience": "ENV::HIGHLIGHT_AZURE_EXP"
    },
    
    "industry_expertise": [
        "ENV::INDUSTRY_1",
        "ENV::INDUSTRY_2"
    ],
    
    "key_achievements_summary": [
        {
            "achievement": "ENV::KEY_ACHIEVEMENT_1"
        },
        {
            "achievement": "ENV::KEY_ACHIEVEMENT_2"
        },
        {
            "achievement": "ENV::KEY_ACHIEVEMENT_3"
        }
    ]
} 