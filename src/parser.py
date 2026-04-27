"""Job description parser to extract keywords, skills, and requirements."""
import re
from collections import Counter

COMMON_SKILLS = {
    "python", "javascript", "typescript", "java", "go", "golang", "rust", "c++", "c#",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "bash", "powershell",
    "react", "angular", "vue", "svelte", "next.js", "nuxt", "django", "flask", "fastapi",
    "spring", "express", "nestjs", "rails", "laravel", "nodejs", "node.js",
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "jenkins", "github actions", "gitlab ci", "circleci", "travisci",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb",
    "cassandra", "sqlite", "firebase", "snowflake", "bigquery",
    "graphql", "rest", "grpc", "websocket", "kafka", "rabbitmq", "sqs",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "spark", "hadoop", "airflow", "dbt", "tableau", "powerbi",
    "git", "jira", "confluence", "figma", "sketch", "notion",
    "microservices", "serverless", "ci/cd", "devops", "sre", "mlops",
    "agile", "scrum", "kanban", "tdd", "bdd", "oauth", "jwt", "sso"
}

def parse_job_description(text):
    text_lower = text.lower()
    found_skills = set()
    for skill in COMMON_SKILLS:
        if skill in text_lower:
            found_skills.add(skill)

    # Extract years of experience
    exp_patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience.*?([0-9]+)\+?\s*years',
        r'([0-9]+)\+?\s*yrs?\s+exp',
    ]
    years_exp = set()
    for pattern in exp_patterns:
        for match in re.finditer(pattern, text_lower):
            years_exp.add(int(match.group(1)))

    # Extract education requirements
    edu_keywords = []
    edu_terms = ["bachelor", "master", "phd", "doctorate", "bs", "ms", "mba", "degree"]
    for term in edu_terms:
        if term in text_lower:
            edu_keywords.append(term)

    # Extract responsibilities / what you'll do
    resp_section = extract_section(text, ["what you'll do", "responsibilities", "role overview", "job description", "about the role"])

    # Extract requirements / qualifications
    req_section = extract_section(text, ["requirements", "qualifications", "what you need", "minimum qualifications", "basic qualifications"])

    # Soft skills
    soft_skills = []
    soft_terms = ["communication", "leadership", "teamwork", "collaboration", "problem.solving", "critical thinking", "time management", "adaptability", "creativity"]
    for term in soft_terms:
        if term.replace(".", " ") in text_lower or term in text_lower:
            soft_skills.append(term.replace(".", " "))

    return {
        "skills": sorted(found_skills),
        "years_experience": sorted(years_exp),
        "education": edu_keywords,
        "soft_skills": soft_skills,
        "responsibilities_preview": resp_section[:500] if resp_section else "",
        "requirements_preview": req_section[:500] if req_section else "",
    }

def extract_section(text, headers):
    lines = text.splitlines()
    capture = False
    captured = []
    for line in lines:
        stripped = line.strip().lower()
        if any(header in stripped for header in headers):
            capture = True
            continue
        if capture:
            if stripped == "" or (len(stripped) < 40 and any(h in stripped for h in ["requirements", "qualifications", "benefits", "perks", "about us", "we offer"])):
                break
            captured.append(line)
    return "\n".join(captured).strip()

def generate_tailoring_suggestions(job_text, user_skills=None):
    parsed = parse_job_description(job_text)
    suggestions = []

    if parsed["skills"]:
        suggestions.append(f"Key technical skills mentioned: {', '.join(parsed['skills'][:10])}")

    if parsed["years_experience"]:
        suggestions.append(f"Experience level requested: {min(parsed['years_experience'])}+ years")

    if parsed["soft_skills"]:
        suggestions.append(f"Emphasize these soft skills: {', '.join(parsed['soft_skills'][:5])}")

    if user_skills:
        missing = set(parsed["skills"]) - set(user_skills)
        if missing:
            suggestions.append(f"Skills to highlight or learn: {', '.join(list(missing)[:5])}")
        matched = set(parsed["skills"]) & set(user_skills)
        if matched:
            suggestions.append(f"Your matched strengths: {', '.join(list(matched)[:8])}")

    return suggestions

if __name__ == "__main__":
    sample = """We are looking for a Senior Software Engineer with 5+ years of experience in Python, React, and AWS.
    You will design scalable systems and collaborate with cross-functional teams.
    Requirements: Bachelor's degree, strong communication skills, experience with microservices and Kubernetes."""
    result = parse_job_description(sample)
    print(result)
