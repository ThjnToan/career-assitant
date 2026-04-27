"""Generator module for tailored resumes and cover letters."""
import re
import json
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "config.json"
MASTER_RESUME = Path(__file__).resolve().parent.parent / "resumes" / "master_resume.md"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def load_master_resume():
    with open(MASTER_RESUME, "r", encoding="utf-8") as f:
        return f.read()

def generate_tailored_resume(job_description, role, company, output_name=None):
    config = load_config()
    master = load_master_resume()
    user = config["user"]

    if not output_name:
        safe_company = re.sub(r"[^a-zA-Z0-9]", "_", company)[:30]
        safe_role = re.sub(r"[^a-zA-Z0-9]", "_", role)[:30]
        output_name = f"{safe_company}_{safe_role}_{datetime.now().strftime('%Y%m%d')}.md"

    output_path = Path(config["resume"]["output_dir"]) / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Simple keyword injection - in production, this would be more sophisticated
    from src.parser import parse_job_description
    parsed = parse_job_description(job_description)

    tailored = master.replace("Software Engineer | Full Stack Developer", f"{role} | {user['name']}")

    # Add a customization header
    customization = f"""
<!-- TAILORED FOR: {company} | {role} | Generated: {datetime.now().strftime('%Y-%m-%d')} -->
<!-- TARGET SKILLS: {', '.join(parsed.get('skills', [])[:12])} -->

"""

    final_content = customization + tailored

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    return str(output_path)

def generate_cover_letter(role, company, job_description="", highlights=None, output_name=None):
    config = load_config()
    user = config["user"]
    template_dir = Path(config["cover_letter"]["template_dir"])
    output_dir = Path(config["cover_letter"]["output_dir"])

    template_file = template_dir / "default_template.md"
    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_file}")

    with open(template_file, "r", encoding="utf-8") as f:
        template = f.read()

    if not output_name:
        safe_company = re.sub(r"[^a-zA-Z0-9]", "_", company)[:30]
        safe_role = re.sub(r"[^a-zA-Z0-9]", "_", role)[:30]
        output_name = f"CL_{safe_company}_{safe_role}_{datetime.now().strftime('%Y%m%d')}.md"

    output_path = output_dir / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Basic replacements
    content = template.replace("{{ROLE}}", role)
    content = content.replace("{{COMPANY}}", company)
    content = content.replace("{{YEARS}}", "5+")
    content = content.replace("{{CURRENT_COMPANY}}", "TechCorp Inc.")

    # Job-specific replacements
    from src.parser import parse_job_description
    parsed = parse_job_description(job_description)

    skills = parsed.get("skills", ["Python", "React", "AWS"])
    content = content.replace("{{RELEVANT SKILL 1}}", skills[0] if len(skills) > 0 else "software development")
    content = content.replace("{{RELEVANT SKILL 2}}", skills[1] if len(skills) > 1 else "system design")
    content = content.replace("{{RELEVANT DOMAIN}}", skills[0] if skills else "software engineering")

    # Achievements
    if highlights:
        for i, hl in enumerate(highlights[:3], 1):
            content = content.replace(f"{{{{ACHIEVEMENT {i}}}}}", hl)
    else:
        content = content.replace("{{ACHIEVEMENT 1}}", "Architected microservices handling 10M+ daily events, reducing latency by 60%")
        content = content.replace("{{ACHIEVEMENT 2}}", "Led migration to AWS EKS, increasing deployment frequency by 5x")
        content = content.replace("{{ACHIEVEMENT 3}}", "Mentored 4 junior engineers and established code review best practices")

    # Company-specific placeholders
    content = content.replace("{{MISSION/VALUE}}", "innovation and technical excellence")
    content = content.replace("{{PRODUCT/INITIATIVE}}", "industry-leading products")
    content = content.replace("{{SPECIFIC DETAIL}}", "your commitment to engineering quality")
    content = content.replace("{{KEY SKILL AREA}}", "distributed systems and cloud infrastructure")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(output_path)

if __name__ == "__main__":
    print(generate_tailored_resume("Python, AWS, Kubernetes", "Backend Engineer", "Stripe"))
    print(generate_cover_letter("Backend Engineer", "Stripe", "Python, AWS, Kubernetes"))
