"""Structured resume data for more accurate question answering."""

RESUME_DATA = {
    # Keywords for faster search and query optimization
    "keywords": [
        "Technical Business Analyst", "Business Systems Analyst", "Senior Business Analyst",
        "Azure", "Scrum Master", "Agile", "SQL", "Power BI", "Python", "Azure DevOps",
        "Requirements Gathering", "Stakeholder Management", "Process Optimization",
        "Data Analysis", "Machine Learning", "Houston", "Montgomery"
    ],
    # Removed current_role - consolidated into professional_experience[0] to reduce redundancy
    "contact_information": {
        "name": "Frank Tallerine",
        "location": "Montgomery, TX",
        "email": "franktallerine@gmail.com",
        "linkedin": "https://www.linkedin.com/in/frank-tallerine/"
    },
    "professional_summary": [
        "Certified Scrum Master with over 6 years of experience as a Technical Business Analyst, excelling in Agile frameworks and AI-driven insights within .NET environments.",
        "Adept at delivering precise, high-level communication to align cross-functional teams, devising creative solutions to complex challenges, and applying critical thinking to drive strategic outcomes."
    ],
    "certifications": [
        {
            "name": "Certified Scrum Master (CSM)",
            "issuer": "Scrum Alliance",
            "year_obtained": "2019",
            "status": "Active"
        },
        {
            "name": "Microsoft Certified: Azure Administrator Associate",
            "issuer": "Microsoft",
            "year_obtained": "2021",
            "status": "Active"
        },
        {
            "name": "Microsoft Certified: Azure Fundamentals",
            "issuer": "Microsoft",
            "year_obtained": "2020",
            "status": "Active"
        }
    ],
    "professional_experience": [
        {
            "company": "The Marker Group",
            "role": "Technical Business Analyst",
            "title": "Technical Business Analyst",
            "dates": "Sep 2018-Present",
            "duration": "Sep 2018-Present",
            "status": "Current",
            "responsibilities": [
                "Led Agile process optimization, implementing daily standups and sprint planning, increasing team velocity by 75% (20-25 stories per 2-week sprint).",
                "Conducted requirement analysis with stakeholders, achieving an 85% approval rate, improving by 55%.",
                "Implemented Azure DevOps release processes, reducing deployment errors and enabling 3-5 weekly deployments (up from 1-2 monthly).",
                "Directed quality assurance and User Acceptance Testing, reducing post-release defects.",
                "Built 15+ Power BI dashboards for real-time insights, enhancing decision-making accuracy."
            ],
            "achievements": [
                "Orchestrated cross-functional collaboration to resolve intricate deployment bottlenecks, slashing errors by 40% through innovative, creative problem-solving.",
                "Distilled complex technical requirements into concise, actionable strategies, ensuring precise high-level communication that bridged technical and business teams."
            ]
        },
        {
            "company": "John Moore Services",
            "role": "Lead Project Coordinator",
            "title": "Lead Project Coordinator",
            "dates": "Feb 2017-Jul 2018",
            "duration": "Feb 2017-Jul 2018",
            "status": "Past",
            "responsibilities": [
                "Designed a Microsoft Access database for financial reporting, improving decision-making.",
                "Coordinated sales and installation teams, ensuring on-time job completion and high customer satisfaction.",
                "Monitored job schedules, achieving high invoice collection rates."
            ],
            "achievements": [
                "Engineered a novel scheduling framework that boosted on-time job completion by 20%, leveraging high-level critical thinking to analyze and optimize workflows.",
                "Translated intricate financial data into clear, impactful reports for non-technical stakeholders, exemplifying precise high-level communication."
            ]
        },
        {
            "company": "Self-Employed",
            "role": "Web Developer",
            "title": "Web Developer",
            "dates": "Sep 2016-Feb 2017",
            "duration": "Sep 2016-Feb 2017",
            "status": "Past",
            "responsibilities": [
                "Developed custom web applications using HTML, CSS, and JavaScript.",
                "Delivered responsive, cross-browser-compatible solutions based on client requirements."
            ],
            "achievements": [
                "Devised creative solutions to tackle cross-browser compatibility challenges, achieving 100% client satisfaction through adaptive problem-solving.",
                "Articulated technical concepts with precision to clients, accelerating project approvals through high-level communication."
            ]
        }
    ],
    "skills_and_technologies": {
        "cloud_and_net": [
            "Azure (3+ years)", 
            "Azure DevOps (3+ years)", 
            "Azure Portal", 
            "PowerShell", 
            ".NET environments"
        ],
        "tools": [
            "SQL (3+ years) - database design, reporting, and data analysis", 
            "Power BI - dashboard creation and data visualization", 
            "Git - version control and collaborative development", 
            "Visual Studio - .NET development and debugging", 
            "Python - data processing, ML pipelines, and automation", 
            "Office 365 (5+ years) - Excel for data analysis, Teams for collaboration, SharePoint for documentation", 
            "Microsoft Access - database design and financial reporting",
            "Mermaid.js - process diagramming and flowchart creation"
        ],
        "agile_and_scrum": [
            "Agile methodologies", 
            "Scrum framework",
            "Sprint planning",
            "Backlog refinement",
            "Retrospectives",
            "Daily standups",
            "User story creation"
        ],
        "business_analysis": [
            "Requirements gathering", 
            "Stakeholder management", 
            "Data analysis",
            "Process optimization",
            "Business process mapping",
            "User acceptance testing",
            "Documentation"
        ],
        "soft_skills": [
            "Conflict resolution", 
            "Negotiation", 
            "Cross-functional collaboration", 
            "Precise high-level communication", 
            "Creative problem solving", 
            "High-level critical thinking"
        ],
        # Legacy structure for backward compatibility
        "technical_skills": ["Azure", "PowerShell", ".NET", "SQL", "Power BI", "Python", "Git", "Visual Studio"],
        "business_skills": ["Requirements gathering", "Stakeholder management", "Data analysis", "Agile", "Scrum"],
        "programming_languages": ["Python", "C++", "JavaScript", "HTML", "CSS", "PowerShell"]
    },
    "projects": [
        {
            "name": "Medical Record Annotation NER Model",
            "status": "Completed",
            "completion_date": "2024",
            "description": [
                "Built an AI-driven proof-of-concept using spaCy NER to extract medical data.",
                "Created Python pipelines for data processing and model training, integrating Label Studio for annotation.",
                "Developed a scalable backend with webhook and Label Studio API for real-time predictions."
            ],
            "achievements": [
                "Exercised high-level critical thinking to streamline data pipelines, cutting processing time by 25% through rigorous analysis and optimization.",
                "Presented complex AI methodologies to stakeholders with clarity and precision, fostering alignment and buy-in on project objectives."
            ],
            "technologies_used": ["Python", "spaCy", "Label Studio", "NER", "Machine Learning", "API Development"],
            "tags": ["AI", "Machine Learning", "Healthcare", "Data Processing", "API Development"]
        }
    ],
    "education": {
        "university": "Texas State University, San Marcos, TX",
        "degrees": ["Bachelor of Mathematics", "Bachelor of Finance"],
        "honors": "Cum Laude",
        "graduation_year": "2016",
        "additional_info": ["Completed C++ courses", "Participated in Student Managed Investment Fund"],
        "graduation_status": "Completed"
    },
    "languages": ["English (Fluent)", "Spanish (Conversational)"],
    "salary_expectations": {
        "target": "$90,000-$115,000 annually",
        "negotiable": "based on role, benefits, and location",
        "additional_notes": "Open to discussing equity or performance-based bonuses for high-impact roles."
    },
    # Removed business_analysis_experience - consolidated into experience_highlights to reduce redundancy
    "job_search_criteria": {
        "desired_role": "Technical Business Analyst, Senior Business Analyst, or Business Systems Analyst roles",
        "preferred_location": "Montgomery, TX (Houston metropolitan area)",
        "salary_range": "$90,000-$115,000",
        "other_criteria": "Seeking roles that leverage Agile/Scrum methodologies, Azure cloud technologies, and data-driven decision making in collaborative environments"
    },
    "experience_highlights": {
        "total_ba_experience": "6+ years (Sep 2018-Present)",
        "scrum_master_experience": "5+ years (2019-Present)", 
        "azure_experience": "3+ years (2021-Present)",
        "sql_experience": "3+ years (2021-Present)",
        "office365_experience": "5+ years (2019-Present)",
        "team_leadership": "Led cross-functional teams of 5-10 members",
        "process_improvement": "Increased team velocity by 75%, reduced deployment errors by 40%"
    },
    "industry_expertise": [
        "Business Analysis",
        "Agile/Scrum methodologies", 
        "Cloud computing (Azure)",
        "Data analytics and visualization",
        "Process optimization",
        "Stakeholder management"
    ],
    "key_achievements_summary": [
        {
            "achievement": "75% increase in team velocity through Agile optimization",
            "tags": ["Agile", "Process Optimization", "Team Leadership", "Scrum"]
        },
        {
            "achievement": "85% stakeholder approval rate for requirements analysis",
            "tags": ["Requirements Gathering", "Stakeholder Management", "Business Analysis"]
        },
        {
            "achievement": "40% reduction in deployment errors",
            "tags": ["Azure DevOps", "Process Improvement", "Quality Assurance"]
        },
        {
            "achievement": "15+ Power BI dashboards delivered",
            "tags": ["Power BI", "Data Visualization", "Analytics", "Dashboards"]
        },
        {
            "achievement": "3-5 weekly deployments enabled (from 1-2 monthly)",
            "tags": ["Azure DevOps", "Process Optimization", "Deployment"]
        }
    ]
}