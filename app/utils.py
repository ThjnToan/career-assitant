"""Utility functions for parsing, generating, and reporting."""
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

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
    found_skills = {s for s in COMMON_SKILLS if s in text_lower}
    
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
    
    edu_terms = ["bachelor", "master", "phd", "doctorate", "bs", "ms", "mba", "degree"]
    edu_keywords = [t for t in edu_terms if t in text_lower]
    
    soft_terms = ["communication", "leadership", "teamwork", "collaboration", "problem solving", "critical thinking", "time management", "adaptability", "creativity"]
    soft_skills = [t for t in soft_terms if t in text_lower]
    
    return {
        "skills": sorted(found_skills),
        "years_experience": sorted(years_exp),
        "education": edu_keywords,
        "soft_skills": soft_skills,
    }

def generate_tailoring_suggestions(job_text, user_skills=None):
    parsed = parse_job_description(job_text)
    suggestions = []
    if parsed["skills"]:
        suggestions.append(f"Key technical skills: {', '.join(parsed['skills'][:10])}")
    if parsed["years_experience"]:
        suggestions.append(f"Experience level: {min(parsed['years_experience'])}+ years")
    if parsed["soft_skills"]:
        suggestions.append(f"Emphasize: {', '.join(parsed['soft_skills'][:5])}")
    if user_skills:
        missing = set(parsed["skills"]) - set(user_skills)
        if missing:
            suggestions.append(f"Skills to highlight/learn: {', '.join(list(missing)[:5])}")
        matched = set(parsed["skills"]) & set(user_skills)
        if matched:
            suggestions.append(f"Your matched strengths: {', '.join(list(matched)[:8])}")
    return suggestions

def generate_weekly_report(user):
    from app.models import Application, Interview
    
    now = datetime.utcnow()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59)
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(seconds=1)
    
    apps_this_week = Application.query.filter(
        Application.user_id == user.id,
        Application.applied_date >= week_start
    ).count()
    
    apps_last_week = Application.query.filter(
        Application.user_id == user.id,
        Application.applied_date >= last_week_start,
        Application.applied_date <= last_week_end
    ).count()
    
    responses_this_week = Application.query.filter(
        Application.user_id == user.id,
        Application.last_updated >= week_start,
        Application.status != 'Applied'
    ).count()
    
    interviews_this_week = Interview.query.join(Application).filter(
        Application.user_id == user.id,
        Interview.scheduled_date >= week_start
    ).count()
    
    pipeline_counts = {}
    for app in Application.query.filter_by(user_id=user.id).all():
        pipeline_counts[app.status] = pipeline_counts.get(app.status, 0) + 1
    
    total = sum(pipeline_counts.values())
    active = total - pipeline_counts.get("Rejected", 0) - pipeline_counts.get("Accepted", 0) - pipeline_counts.get("Withdrawn", 0) - pipeline_counts.get("Ghosted", 0)
    
    sources = {}
    for app in Application.query.filter_by(user_id=user.id).all():
        src = app.source or 'Unknown'
        sources[src] = sources.get(src, 0) + 1
    
    phone_screens = pipeline_counts.get("Phone Screen", 0) + pipeline_counts.get("Technical Screen", 0)
    interviews_count = sum(v for k, v in pipeline_counts.items() if "Interview" in k or k in ["Phone Screen", "Technical Screen", "Final Round"])
    offers = pipeline_counts.get("Offer", 0) + pipeline_counts.get("Negotiating", 0) + pipeline_counts.get("Accepted", 0)
    
    return {
        "week_of": week_start.strftime("%Y-%m-%d"),
        "applications": {"this_week": apps_this_week, "last_week": apps_last_week, "change": apps_this_week - apps_last_week},
        "responses_this_week": responses_this_week,
        "interviews_this_week": interviews_this_week,
        "pipeline": pipeline_counts,
        "active_applications": active,
        "total_applications": total,
        "sources": sources,
        "conversion_rates": {
            "applied_to_screen": round(phone_screens / total * 100, 1) if total else 0,
            "screen_to_interview": round(interviews_count / max(phone_screens, 1) * 100, 1),
            "interview_to_offer": round(offers / max(interviews_count, 1) * 100, 1)
        }
    }

def get_status_color(status):
    colors = {
        "Applied": "#3b82f6", "Phone Screen": "#06b6d4", "Technical Screen": "#06b6d4",
        "Interview Round 1": "#f59e0b", "Interview Round 2": "#f59e0b", "Interview Round 3": "#f59e0b",
        "Final Round": "#8b5cf6", "Offer": "#10b981", "Negotiating": "#10b981", "Accepted": "#059669",
        "Rejected": "#ef4444", "Withdrawn": "#9ca3af", "Ghosted": "#9ca3af"
    }
    return colors.get(status, "#6b7280")

VALID_STATUSES = [
    "Applied", "Phone Screen", "Technical Screen", "Interview Round 1",
    "Interview Round 2", "Interview Round 3", "Final Round", "Offer",
    "Negotiating", "Accepted", "Rejected", "Withdrawn", "Ghosted"
]
