"""Notifier module for reminders and daily digest."""
import sqlite3
from datetime import datetime, timedelta
from src.database import get_connection

def get_daily_digest():
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
    tomorrow = (now + timedelta(days=1)).replace(hour=23, minute=59).isoformat()

    # Today's interviews
    cursor.execute('''
        SELECT i.*, a.company, a.role FROM interviews i
        JOIN applications a ON i.application_id = a.id
        WHERE i.scheduled_date BETWEEN ? AND ? AND i.status = 'Scheduled'
        ORDER BY i.scheduled_date ASC
    ''', (today_start, today_end))
    today_interviews = cursor.fetchall()

    # Tomorrow's interviews
    cursor.execute('''
        SELECT i.*, a.company, a.role FROM interviews i
        JOIN applications a ON i.application_id = a.id
        WHERE i.scheduled_date BETWEEN ? AND ? AND i.status = 'Scheduled'
        ORDER BY i.scheduled_date ASC
    ''', (today_end, tomorrow))
    tomorrow_interviews = cursor.fetchall()

    # Overdue follow-ups
    cursor.execute('''
        SELECT * FROM applications
        WHERE follow_up_date < ? AND status IN ('Applied', 'Phone Screen', 'Technical Screen', 'Interview Round 1', 'Interview Round 2', 'Interview Round 3', 'Final Round')
        ORDER BY follow_up_date ASC
    ''', (now.isoformat(),))
    overdue = cursor.fetchall()

    # Applications this week
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0).isoformat()
    cursor.execute("SELECT COUNT(*) FROM applications WHERE applied_date >= ?", (week_start,))
    apps_this_week = cursor.fetchone()[0]

    # Pipeline summary
    cursor.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    pipeline = dict(cursor.fetchall())

    conn.close()

    return {
        "today_interviews": today_interviews,
        "tomorrow_interviews": tomorrow_interviews,
        "overdue_followups": overdue,
        "applications_this_week": apps_this_week,
        "pipeline": pipeline,
        "generated_at": now.isoformat()
    }

def format_digest(digest):
    lines = []
    lines.append("=" * 60)
    lines.append("CAREER ASSISTANT - DAILY DIGEST")
    lines.append(f"Generated: {digest['generated_at'][:16].replace('T', ' ')}")
    lines.append("=" * 60)

    if digest["today_interviews"]:
        lines.append("\n[bold red]TODAY'S INTERVIEWS[/bold red]")
        for iv in digest["today_interviews"]:
            time = iv[4][:16].replace("T", " ") if iv[4] else "TBD"
            lines.append(f"  {time} - {iv[15]} ({iv[16]})")
            lines.append(f"    Type: {iv[3]} | Round: {iv[2]} | With: {iv[6]} ({iv[7]})")
            if iv[9]:
                lines.append(f"    Link: {iv[9]}")
    else:
        lines.append("\nNo interviews scheduled for today.")

    if digest["tomorrow_interviews"]:
        lines.append("\n[bold yellow]TOMORROW'S INTERVIEWS[/bold yellow]")
        for iv in digest["tomorrow_interviews"]:
            time = iv[4][:16].replace("T", " ") if iv[4] else "TBD"
            lines.append(f"  {time} - {iv[15]} ({iv[16]})")

    if digest["overdue_followups"]:
        lines.append("\n[bold magenta]OVERDUE FOLLOW-UPS[/bold magenta]")
        for app in digest["overdue_followups"]:
            lines.append(f"  {app[1]} ({app[2]}) - Applied: {app[9][:10] if app[9] else 'N/A'}")
    else:
        lines.append("\nNo overdue follow-ups. Great job!")

    lines.append(f"\n[bold green]APPLICATIONS THIS WEEK:[/bold green] {digest['applications_this_week']}")
    lines.append("\n[bold blue]PIPELINE SUMMARY[/bold blue]")
    for status, count in digest["pipeline"].items():
        lines.append(f"  {status}: {count}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)

def send_desktop_notification(title, message):
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )
    except Exception as e:
        print(f"[Notification] {title}: {message}")

def check_and_notify():
    digest = get_daily_digest()
    if digest["today_interviews"]:
        iv = digest["today_interviews"][0]
        title = f"Interview Today: {iv[15]}"
        msg = f"{iv[3]} at {iv[4][:16].replace('T', ' ')} with {iv[6]}"
        send_desktop_notification(title, msg)

    if digest["overdue_followups"]:
        title = f"Follow-ups Needed"
        msg = f"You have {len(digest['overdue_followups'])} overdue follow-ups."
        send_desktop_notification(title, msg)

if __name__ == "__main__":
    d = get_daily_digest()
    print(format_digest(d))
