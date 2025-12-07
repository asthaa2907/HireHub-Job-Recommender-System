# skill_extractor.py
import re

def extract_skills(text: str):
    """
    Extract common technical and soft skills from resume text.
    Returns a unique, lowercase list of keywords.
    """

    if not text:
        return []

    # List of keywords you can expand later
    skill_keywords = [
        # Programming languages
        "python", "java", "c++", "c", "javascript", "typescript", "r", "sql", "matlab", "scala",
        # Data & Analytics
        "machine learning", "deep learning", "data analysis", "data visualization", "pandas",
        "numpy", "matplotlib", "seaborn", "scikit-learn", "tensorflow", "keras", "pytorch",
        "power bi", "tableau", "excel",
        # Cloud & Tools
        "aws", "azure", "gcp", "docker", "kubernetes", "linux", "git", "github", "jenkins",
        # Web & Backend
        "flask", "django", "react", "node", "api", "html", "css", "bootstrap",
        # Soft skills
        "communication", "leadership", "teamwork", "problem solving", "critical thinking"
    ]

    text = text.lower()
    skills_found = []

    for skill in skill_keywords:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            skills_found.append(skill)

    # Deduplicate
    skills_found = list(sorted(set(skills_found)))

    return skills_found
