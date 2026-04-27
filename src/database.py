"""Database module for CareerAssistant Pro."""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "career.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH))

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            salary_range TEXT,
            job_url TEXT,
            description TEXT,
            status TEXT DEFAULT 'Applied',
            source TEXT,
            applied_date TEXT,
            last_updated TEXT,
            follow_up_date TEXT,
            notes TEXT,
            resume_path TEXT,
            cover_letter_path TEXT
        );

        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            round INTEGER DEFAULT 1,
            interview_type TEXT,
            scheduled_date TEXT,
            duration_minutes INTEGER,
            interviewer_name TEXT,
            interviewer_title TEXT,
            location TEXT,
            video_link TEXT,
            status TEXT DEFAULT 'Scheduled',
            questions TEXT,
            notes TEXT,
            rating INTEGER,
            feedback TEXT,
            FOREIGN KEY (application_id) REFERENCES applications(id)
        );

        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            title TEXT,
            email TEXT,
            linkedin TEXT,
            relationship TEXT,
            last_contact_date TEXT,
            notes TEXT,
            tags TEXT
        );

        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            entity_type TEXT,
            entity_id INTEGER,
            description TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start TEXT,
            target_applications INTEGER,
            target_networking INTEGER,
            actual_applications INTEGER DEFAULT 0,
            actual_networking INTEGER DEFAULT 0,
            notes TEXT
        );
    ''')

    conn.commit()
    conn.close()

def insert_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already populated
    cursor.execute("SELECT COUNT(*) FROM applications")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    today = datetime.now()
    sample_apps = [
        ("Google", "Software Engineer III", "Mountain View, CA", "$150k-$200k",
         "https://careers.google.com/jobs/123", "Design and develop large-scale distributed systems...",
         "Phone Screen", "LinkedIn", (today - timedelta(days=14)).isoformat(),
         (today - timedelta(days=2)).isoformat(), "Recruiter seemed very positive. Need to prep system design."),
        ("Stripe", "Backend Engineer", "Remote", "$140k-$190k",
         "https://stripe.com/jobs/456", "Build payment infrastructure APIs used by millions of businesses...",
         "Applied", "Company Website", (today - timedelta(days=7)).isoformat(),
         None, "Dream company. Strong referral from former colleague."),
        ("Airbnb", "Full Stack Developer", "San Francisco, CA", "$130k-$175k",
         "https://airbnb.com/careers/789", "Create delightful experiences for hosts and guests...",
         "Interview Round 2", "Referral", (today - timedelta(days=21)).isoformat(),
         (today + timedelta(days=3)).isoformat(), "Cultural fit interview coming up. Review core values."),
        ("Netflix", "Senior Software Engineer", "Los Gatos, CA", "$200k-$300k",
         "https://jobs.netflix.com/321", "Design high-throughput streaming services...",
         "Rejected", "Recruiter Outreach", (today - timedelta(days=30)).isoformat(),
         None, "Position filled internally. Recruiter said to keep in touch for future roles."),
        ("OpenAI", "Machine Learning Engineer", "San Francisco, CA", "$180k-$250k",
         "https://openai.com/careers/654", "Build and scale training infrastructure for large language models...",
         "Applied", "AngelList", (today - timedelta(days=3)).isoformat(),
         None, "Extremely competitive. Need to follow up in one week if no response."),
        ("Figma", "Product Engineer", "Remote / SF", "$140k-$185k",
         "https://figma.com/careers/987", "Build features that empower designers and developers to collaborate...",
         "Technical Screen", "LinkedIn", (today - timedelta(days=10)).isoformat(),
         (today + timedelta(days=1)).isoformat(), "Focus on React performance and real-time collaboration systems."),
    ]

    for app in sample_apps:
        cursor.execute('''
            INSERT INTO applications (company, role, location, salary_range, job_url, description, status, source, applied_date, follow_up_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', app)
        app_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO activities (activity_type, entity_type, entity_id, description, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ("Application Created", "application", app_id, f"Applied to {app[0]} for {app[1]}", app[8]))

    # Sample interviews
    sample_interviews = [
        (1, 1, "Phone Screen", (today - timedelta(days=2)).isoformat(), 45, "Sarah Chen", "Senior Engineering Manager", "Google Meet", "Completed", "Tell me about yourself, Why Google, System design basics", "Went well. Sarah was friendly and transparent about team culture.", 4, None),
        (3, 1, "Behavioral", (today - timedelta(days=7)).isoformat(), 60, "Michael Ross", "Engineering Lead", "Zoom", "Completed", "Tell me about a conflict, Project you're proud of, Diversity and inclusion", "Strong rapport. They emphasized ownership and autonomy.", 5, None),
        (3, 2, "Cultural Fit", (today + timedelta(days=3)).isoformat(), 45, "Lisa Wang", "VP of Engineering", "Onsite", "Scheduled", None, "Prepare questions about Airbnb's approach to platform stability.", None, None),
        (6, 1, "Technical Screen", (today + timedelta(days=1)).isoformat(), 60, "David Kim", "Staff Engineer", "Zoom", "Scheduled", None, "Review Figma's multiplayer architecture blog posts.", None, None),
    ]

    for iv in sample_interviews:
        cursor.execute('''
            INSERT INTO interviews (application_id, round, interview_type, scheduled_date, duration_minutes, interviewer_name, interviewer_title, location, status, questions, notes, rating, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', iv)

    # Sample contacts
    sample_contacts = [
        ("Sarah Chen", "Google", "Senior Engineering Manager", "sarah.chen@google.com", "linkedin.com/in/sarahchen", "Recruiter/Interviewer", today.isoformat(), "Very helpful, shared team culture insights.", "referral,tech"),
        ("James Miller", "Stripe", "Staff Engineer", "james@stripe.com", "linkedin.com/in/jamesmiller", "Former Colleague", (today - timedelta(days=10)).isoformat(), "Provided strong referral. Recommended focusing on API design experience.", "referral,former-colleague"),
        ("Priya Patel", "Airbnb", "Product Manager", "priya@airbnb.com", "linkedin.com/in/priyapatel", "Network Contact", (today - timedelta(days=5)).isoformat(), "Connected at a meetup. Offered to introduce to hiring manager.", "networking,meetup"),
    ]

    for contact in sample_contacts:
        cursor.execute('''
            INSERT INTO contacts (name, company, title, email, linkedin, relationship, last_contact_date, notes, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', contact)

    # Sample goals
    cursor.execute('''
        INSERT INTO goals (week_start, target_applications, target_networking, actual_applications, actual_networking, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ((today - timedelta(days=today.weekday())).isoformat(), 5, 2, 4, 1, "Good week. Strong referrals at Stripe and Airbnb."))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    insert_sample_data()
    print("Database initialized and populated with sample data.")
