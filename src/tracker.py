"""Tracker module for managing job applications."""
import sqlite3
from datetime import datetime, timedelta
from src.database import get_connection

VALID_STATUSES = [
    "Applied", "Phone Screen", "Technical Screen", "Interview Round 1",
    "Interview Round 2", "Interview Round 3", "Final Round", "Offer",
    "Negotiating", "Accepted", "Rejected", "Withdrawn", "Ghosted"
]

def add_application(company, role, location="", salary_range="", job_url="",
                    description="", source="", notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    follow_up = (datetime.now() + timedelta(days=7)).isoformat()

    cursor.execute('''
        INSERT INTO applications (company, role, location, salary_range, job_url, description, status, source, applied_date, last_updated, follow_up_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (company, role, location, salary_range, job_url, description, "Applied", source, now, now, follow_up, notes))

    app_id = cursor.lastrowid
    cursor.execute('''
        INSERT INTO activities (activity_type, entity_type, entity_id, description, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', ("Application Created", "application", app_id, f"Applied to {company} for {role}", now))

    conn.commit()
    conn.close()
    return app_id

def update_status(app_id, new_status, notes=None):
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status. Choose from: {', '.join(VALID_STATUSES)}")

    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    cursor.execute("SELECT company, role, status FROM applications WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Application {app_id} not found.")

    old_status = row[2]
    cursor.execute('''
        UPDATE applications SET status = ?, last_updated = ? WHERE id = ?
    ''', (new_status, now, app_id))

    if notes:
        cursor.execute("UPDATE applications SET notes = COALESCE(notes, '') || '\n[' || ? || '] ' || ? WHERE id = ?",
                       (now[:10], notes, app_id))

    cursor.execute('''
        INSERT INTO activities (activity_type, entity_type, entity_id, description, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', ("Status Updated", "application", app_id, f"{row[0]} ({row[1]}): {old_status} -> {new_status}", now))

    conn.commit()
    conn.close()

def get_application(app_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def list_applications(status=None, limit=50):
    conn = get_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute("SELECT * FROM applications WHERE status = ? ORDER BY last_updated DESC LIMIT ?", (status, limit))
    else:
        cursor.execute("SELECT * FROM applications ORDER BY last_updated DESC LIMIT ?", (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def search_applications(query):
    conn = get_connection()
    cursor = conn.cursor()
    like = f"%{query}%"
    cursor.execute('''
        SELECT * FROM applications
        WHERE company LIKE ? OR role LIKE ? OR notes LIKE ? OR description LIKE ?
        ORDER BY last_updated DESC
    ''', (like, like, like, like))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_application(app_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    cursor.execute("DELETE FROM interviews WHERE application_id = ?", (app_id,))
    conn.commit()
    conn.close()

def get_pipeline_counts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    rows = cursor.fetchall()
    conn.close()
    return dict(rows)

def get_overdue_followups():
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        SELECT * FROM applications
        WHERE follow_up_date < ? AND status IN ('Applied', 'Phone Screen', 'Technical Screen', 'Interview Round 1', 'Interview Round 2', 'Interview Round 3', 'Final Round')
        ORDER BY follow_up_date ASC
    ''', (now,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_interview(application_id, interview_type, scheduled_date, duration=60,
                  interviewer_name="", interviewer_title="", location="",
                  video_link="", notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT company, role FROM applications WHERE id = ?", (application_id,))
    app = cursor.fetchone()
    if not app:
        conn.close()
        raise ValueError(f"Application {application_id} not found.")

    cursor.execute("SELECT MAX(round) FROM interviews WHERE application_id = ?", (application_id,))
    row = cursor.fetchone()
    round_num = (row[0] or 0) + 1

    cursor.execute('''
        INSERT INTO interviews (application_id, round, interview_type, scheduled_date, duration_minutes, interviewer_name, interviewer_title, location, video_link, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (application_id, round_num, interview_type, scheduled_date, duration, interviewer_name, interviewer_title, location, video_link, notes))

    iv_id = cursor.lastrowid
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO activities (activity_type, entity_type, entity_id, description, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', ("Interview Scheduled", "interview", iv_id, f"{interview_type} for {app[0]} ({app[1]}) on {scheduled_date}", now))

    conn.commit()
    conn.close()
    return iv_id

def get_interviews_for_app(app_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interviews WHERE application_id = ? ORDER BY round", (app_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_upcoming_interviews(hours=48):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    future = (datetime.now() + timedelta(hours=hours)).isoformat()
    cursor.execute('''
        SELECT i.*, a.company, a.role FROM interviews i
        JOIN applications a ON i.application_id = a.id
        WHERE i.scheduled_date BETWEEN ? AND ? AND i.status = 'Scheduled'
        ORDER BY i.scheduled_date ASC
    ''', (now, future))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_interview(iv_id, **kwargs):
    allowed = {"status", "questions", "notes", "rating", "feedback"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return

    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [iv_id]
    cursor.execute(f"UPDATE interviews SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
