"""Reporter module for analytics and progress reports."""
import sqlite3
from datetime import datetime, timedelta
from src.database import get_connection

def generate_weekly_report():
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59)
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(seconds=1)

    # This week applications
    cursor.execute("SELECT COUNT(*) FROM applications WHERE applied_date >= ?", (week_start.isoformat(),))
    apps_this_week = cursor.fetchone()[0]

    # Last week applications
    cursor.execute("SELECT COUNT(*) FROM applications WHERE applied_date BETWEEN ? AND ?",
                   (last_week_start.isoformat(), last_week_end.isoformat()))
    apps_last_week = cursor.fetchone()[0]

    # Responses this week (status changes from Applied)
    cursor.execute("""
        SELECT COUNT(*) FROM applications
        WHERE last_updated >= ? AND status != 'Applied'
    """, (week_start.isoformat(),))
    responses_this_week = cursor.fetchone()[0]

    # Pipeline counts
    cursor.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    pipeline = dict(cursor.fetchall())

    total = sum(pipeline.values())
    active = total - pipeline.get("Rejected", 0) - pipeline.get("Accepted", 0) - pipeline.get("Withdrawn", 0) - pipeline.get("Ghosted", 0)

    # Interview stats
    cursor.execute("SELECT COUNT(*) FROM interviews WHERE scheduled_date >= ?", (week_start.isoformat(),))
    interviews_this_week = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(rating) FROM interviews WHERE rating IS NOT NULL")
    avg_rating = cursor.fetchone()[0]

    # Sources effectiveness
    cursor.execute("SELECT source, COUNT(*) FROM applications GROUP BY source")
    sources = dict(cursor.fetchall())

    # Conversion rates
    phone_screens = pipeline.get("Phone Screen", 0) + pipeline.get("Technical Screen", 0)
    interviews = sum(v for k, v in pipeline.items() if "Interview" in k or k in ["Phone Screen", "Technical Screen", "Final Round"])
    offers = pipeline.get("Offer", 0) + pipeline.get("Negotiating", 0) + pipeline.get("Accepted", 0)

    conn.close()

    report = {
        "week_of": week_start.strftime("%Y-%m-%d"),
        "applications": {
            "this_week": apps_this_week,
            "last_week": apps_last_week,
            "change": apps_this_week - apps_last_week
        },
        "responses_this_week": responses_this_week,
        "interviews_this_week": interviews_this_week,
        "pipeline": pipeline,
        "active_applications": active,
        "total_applications": total,
        "average_interview_rating": round(avg_rating, 2) if avg_rating else None,
        "sources": sources,
        "conversion_rates": {
            "applied_to_screen": round(phone_screens / total * 100, 1) if total else 0,
            "screen_to_interview": round(interviews / max(phone_screens, 1) * 100, 1),
            "interview_to_offer": round(offers / max(interviews, 1) * 100, 1)
        }
    }
    return report

def format_weekly_report(report):
    lines = []
    lines.append("=" * 60)
    lines.append(f"WEEKLY REPORT - Week of {report['week_of']}")
    lines.append("=" * 60)

    lines.append(f"\n[bold]Applications:[/bold] {report['applications']['this_week']} this week")
    if report['applications']['change'] >= 0:
        lines.append(f"  ([green]+{report['applications']['change']}[/green] vs last week)")
    else:
        lines.append(f"  ([red]{report['applications']['change']}[/red] vs last week)")

    lines.append(f"[bold]Responses:[/bold] {report['responses_this_week']} status updates this week")
    lines.append(f"[bold]Interviews:[/bold] {report['interviews_this_week']} scheduled this week")
    if report['average_interview_rating']:
        lines.append(f"[bold]Avg Interview Rating:[/bold] {report['average_interview_rating']}/5")

    lines.append(f"\n[bold]Active Applications:[/bold] {report['active_applications']} / {report['total_applications']} total")

    lines.append("\n[bold]Pipeline:[/bold]")
    for status, count in report['pipeline'].items():
        lines.append(f"  {status}: {count}")

    lines.append("\n[bold]Sources:[/bold]")
    for source, count in report['sources'].items():
        lines.append(f"  {source or 'Unknown'}: {count}")

    lines.append("\n[bold]Conversion Rates:[/bold]")
    cr = report['conversion_rates']
    lines.append(f"  Applied -> Screen: {cr['applied_to_screen']}%")
    lines.append(f"  Screen -> Interview: {cr['screen_to_interview']}%")
    lines.append(f"  Interview -> Offer: {cr['interview_to_offer']}%")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)

def export_report_html(report, filepath="reports/weekly/latest.html"):
    from pathlib import Path
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    html = f"""<!DOCTYPE html>
<html>
<head><title>Weekly Report - {report['week_of']}</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #f5f5f5; }}
.card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
h1 {{ color: #333; }}
h2 {{ color: #555; font-size: 18px; margin-top: 0; }}
.metric {{ display: inline-block; margin-right: 30px; margin-bottom: 10px; }}
.metric-value {{ font-size: 28px; font-weight: bold; color: #2c3e50; }}
.metric-label {{ font-size: 12px; color: #777; text-transform: uppercase; }}
.positive {{ color: #27ae60; }} .negative {{ color: #e74c3c; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid #eee; }}
th {{ color: #777; font-weight: normal; font-size: 12px; text-transform: uppercase; }}
</style>
</head>
<body>
<div class="card">
<h1>Weekly Report</h1>
<p style="color:#777">Week of {report['week_of']}</p>
<div class="metric">
<div class="metric-value">{report['applications']['this_week']}</div>
<div class="metric-label">Applications</div>
</div>
<div class="metric">
<div class="metric-value {'positive' if report['applications']['change'] >= 0 else 'negative'}">{report['applications']['change']:+d}</div>
<div class="metric-label">vs Last Week</div>
</div>
<div class="metric">
<div class="metric-value">{report['responses_this_week']}</div>
<div class="metric-label">Responses</div>
</div>
<div class="metric">
<div class="metric-value">{report['interviews_this_week']}</div>
<div class="metric-label">Interviews</div>
</div>
</div>
<div class="card">
<h2>Pipeline</h2>
<table><tr><th>Status</th><th>Count</th></tr>
"""
    for status, count in report['pipeline'].items():
        html += f"<tr><td>{status}</td><td>{count}</td></tr>"
    html += """</table></div>
<div class="card">
<h2>Conversion Rates</h2>
<table><tr><th>Stage</th><th>Rate</th></tr>"""
    cr = report['conversion_rates']
    html += f"<tr><td>Applied to Screen</td><td>{cr['applied_to_screen']}%</td></tr>"
    html += f"<tr><td>Screen to Interview</td><td>{cr['screen_to_interview']}%</td></tr>"
    html += f"<tr><td>Interview to Offer</td><td>{cr['interview_to_offer']}%</td></tr>"
    html += "</table></div></body></html>"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return filepath

if __name__ == "__main__":
    r = generate_weekly_report()
    print(format_weekly_report(r))
    export_report_html(r)
    print(f"\nHTML report saved.")
