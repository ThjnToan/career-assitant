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

# ========== EMAIL NOTIFICATIONS ==========

def send_email(smtp_server, smtp_port, smtp_username, smtp_password, to_email, subject, html_body):
    """Send an HTML email using SMTP."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = to_email
        
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

def generate_email_digest(user):
    """Generate a daily digest email subject and HTML body."""
    from app.models import Application, Interview
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0)
    today_end = now.replace(hour=23, minute=59, second=59)
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0)
    
    # Today's interviews
    today_ivs = Interview.query.join(Application).filter(
        Application.user_id == user.id,
        Interview.scheduled_date.between(today_start, today_end),
        Interview.status == 'Scheduled'
    ).all()
    
    # Overdue follow-ups
    overdue = Application.query.filter(
        Application.user_id == user.id,
        Application.follow_up_date < now,
        Application.status.in_(['Applied', 'Phone Screen', 'Technical Screen', 'Interview Round 1', 'Interview Round 2', 'Interview Round 3', 'Final Round'])
    ).all()
    
    # This week's applications
    week_apps = Application.query.filter(
        Application.user_id == user.id,
        Application.applied_date >= week_start
    ).count()
    
    # Pipeline
    pipeline = {}
    for app in Application.query.filter_by(user_id=user.id).all():
        pipeline[app.status] = pipeline.get(app.status, 0) + 1
    
    subject = f"CareerAssistant Daily Digest - {now.strftime('%A, %B %d')}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f8fafc; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .header p {{ margin: 8px 0 0; opacity: 0.9; }}
            .content {{ padding: 30px; }}
            .section {{ margin-bottom: 24px; }}
            .section h2 {{ font-size: 16px; color: #1e293b; margin-bottom: 12px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
            .alert {{ padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; }}
            .alert-warning {{ background: #fef3c7; color: #92400e; }}
            .alert-danger {{ background: #fee2e2; color: #991b1b; }}
            .alert-info {{ background: #dbeafe; color: #1e40af; }}
            .stat-grid {{ display: flex; gap: 12px; }}
            .stat {{ flex: 1; background: #f1f5f9; padding: 16px; border-radius: 8px; text-align: center; }}
            .stat-value {{ font-size: 24px; font-weight: 700; color: #2563eb; }}
            .stat-label {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
            .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; background: #f8fafc; }}
            .interview-item {{ padding: 10px; background: #f8fafc; border-radius: 6px; margin-bottom: 6px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Good Morning, {user.name or user.username}!</h1>
                <p>Your daily job search briefing for {now.strftime('%A, %B %d')}</p>
            </div>
            <div class="content">
    """
    
    if today_ivs:
        html += '<div class="section"><h2>&#128227; Interviews Today</h2>'
        for iv in today_ivs:
            time_str = iv.scheduled_date.strftime('%I:%M %p') if iv.scheduled_date else 'TBD'
            html += f'<div class="alert alert-warning">{iv.interview_type} with <strong>{iv.application.company}</strong> at {time_str}'
            if iv.video_link:
                html += f' - <a href="{iv.video_link}">Join Meeting</a>'
            html += '</div>'
        html += '</div>'
    
    if overdue:
        html += '<div class="section"><h2>&#128293; Follow-ups Needed</h2>'
        for app in overdue[:3]:
            html += f'<div class="alert alert-danger"><strong>{app.company}</strong> ({app.role}) - Applied {app.applied_date.strftime("%b %d")}</div>'
        if len(overdue) > 3:
            html += f'<div style="color:#64748b;font-size:13px;">...and {len(overdue) - 3} more</div>'
        html += '</div>'
    
    html += '<div class="section"><h2>&#128200; This Week</h2><div class="stat-grid">'
    html += f'<div class="stat"><div class="stat-value">{week_apps}</div><div class="stat-label">Applications</div></div>'
    html += f'<div class="stat"><div class="stat-value">{pipeline.get("Offer", 0) + pipeline.get("Negotiating", 0) + pipeline.get("Accepted", 0)}</div><div class="stat-label">Offers</div></div>'
    html += f'<div class="stat"><div class="stat-value">{sum(pipeline.values())}</div><div class="stat-label">Total Active</div></div>'
    html += '</div></div>'
    
    html += """
            </div>
            <div class="footer">
                <p>CareerAssistant Pro - Your personal job search companion</p>
                <p><a href="http://localhost:5000">Open Dashboard</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html

# ========== PDF RESUME GENERATOR ==========

def generate_resume_pdf(user, application):
    """Generate a professional PDF resume tailored for a specific application."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    import io
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=18
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=8,
        spaceBefore=16
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    
    story = []
    
    # Name
    story.append(Paragraph(user.name or user.username, name_style))
    story.append(Paragraph(user.title or application.role, title_style))
    
    # Contact info
    contact_parts = []
    if user.email: contact_parts.append(user.email)
    if user.phone: contact_parts.append(user.phone)
    if user.location: contact_parts.append(user.location)
    if user.linkedin: contact_parts.append(user.linkedin)
    if user.portfolio: contact_parts.append(user.portfolio)
    
    if contact_parts:
        story.append(Paragraph(' | '.join(contact_parts), ParagraphStyle(
            'ContactStyle', parent=styles['Normal'], fontSize=9, 
            textColor=colors.HexColor('#64748b'), alignment=TA_CENTER, spaceAfter=24
        )))
    
    # Horizontal line
    story.append(Table([['']], colWidths=[6.5*inch], style=TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 2, colors.HexColor('#e2e8f0')),
    ])))
    
    # Professional Summary
    story.append(Paragraph('PROFESSIONAL SUMMARY', section_style))
    story.append(Paragraph(
        f"Results-driven professional seeking the {application.role} position at {application.company}. "
        f"Committed to delivering high-quality work and contributing to team success.",
        body_style
    ))
    
    story.append(Spacer(1, 12))
    
    # Target Role
    story.append(Paragraph('TARGET POSITION', section_style))
    story.append(Paragraph(
        f'<b>{application.role}</b> at <b>{application.company}</b><br/>'
        f'Location: {application.location or "Not specified"}<br/>'
        f'Salary Range: {application.salary_range or "Not specified"}',
        body_style
    ))
    
    story.append(Spacer(1, 12))
    
    # Key Skills (parsed from job description)
    if application.description:
        parsed = parse_job_description(application.description)
        if parsed['skills']:
            story.append(Paragraph('KEY SKILLS', section_style))
            skills_text = ', '.join(parsed['skills'][:12])
            story.append(Paragraph(skills_text, body_style))
            story.append(Spacer(1, 12))
    
    # Experience
    story.append(Paragraph('PROFESSIONAL EXPERIENCE', section_style))
    story.append(Paragraph(
        '<b>Senior Role</b> | Company Name<br/>'
        'Dates of Employment<br/>'
        '- Led key initiatives and delivered measurable results<br/>'
        '- Collaborated with cross-functional teams to achieve goals<br/>'
        '- Improved processes and optimized performance',
        body_style
    ))
    
    story.append(Spacer(1, 12))
    
    # Education
    story.append(Paragraph('EDUCATION', section_style))
    story.append(Paragraph(
        '<b>Degree Name</b> | University Name<br/>'
        'Graduation Year | Relevant coursework and achievements',
        body_style
    ))
    
    story.append(Spacer(1, 12))
    
    # Why this company
    story.append(Paragraph('WHY THIS ROLE', section_style))
    story.append(Paragraph(
        f"I am particularly excited about the opportunity to contribute to {application.company} "
        f"as a {application.role}. The company's mission aligns with my professional values, "
        f"and I am eager to bring my expertise to the team.",
        body_style
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
