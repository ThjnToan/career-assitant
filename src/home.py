"""Home dashboard - the beautiful default view when you open CareerAssistant."""
import json
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich import box

from src.database import get_connection
from src.tracker import get_pipeline_counts, get_overdue_followups, get_upcoming_interviews
from src.notifier import get_daily_digest

console = Console()
CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def get_weekly_progress():
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0).isoformat()
    cursor.execute("SELECT COUNT(*) FROM applications WHERE applied_date >= ?", (week_start,))
    apps = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM activities WHERE activity_type = 'Networking' AND created_at >= ?", (week_start,))
    networking = cursor.fetchone()[0]
    conn.close()
    return apps, networking

def get_recent_activity(limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT activity_type, description, created_at FROM activities
        ORDER BY created_at DESC LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_motivational_quote():
    quotes = [
        "The best time to plant a tree was 20 years ago. The second best time is now.",
        "Every application is a step closer to your dream role.",
        "Consistency beats intensity. Keep showing up.",
        "Rejection is redirection. Stay focused.",
        "Your next 'yes' is coming. Track it until it arrives.",
        "Small progress is still progress.",
        "The job you want also wants you. You just haven't met yet.",
    ]
    day_of_year = datetime.now().timetuple().tm_yday
    return quotes[day_of_year % len(quotes)]

def render_home():
    config = load_config()
    goals = config.get("goals", {})
    digest = get_daily_digest()
    apps_this_week, net_this_week = get_weekly_progress()
    target_apps = goals.get("weekly_applications", 5)
    target_net = goals.get("weekly_networking", 2)
    pipeline = get_pipeline_counts()

    # Header
    now = datetime.now()
    greeting = "Good morning" if now.hour < 12 else "Good afternoon" if now.hour < 18 else "Good evening"
    user_name = config.get("user", {}).get("name", "there").split()[0]

    header_text = Text()
    header_text.append(f"{greeting}, {user_name}!\n", style="bold blue")
    header_text.append(f"Today is {now.strftime('%A, %B %d')}  |  ", style="dim")
    header_text.append(f"Week {now.isocalendar()[1]}", style="dim")
    console.print(Panel(header_text, border_style="blue", padding=(1, 2)))

    # Motivation
    console.print(f"\n[italic dim]" + get_motivational_quote() + "[/italic dim]\n")

    # Goals Progress
    console.print("[bold]Weekly Goals[/bold]")
    with Progress(TextColumn("[progress.description]{task.description}"), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}% ({task.completed}/{task.total})"), console=console) as progress:
        progress.add_task("Applications", total=target_apps, completed=min(apps_this_week, target_apps))
        progress.add_task("Networking ", total=target_net, completed=min(net_this_week, target_net))

    # Action Center
    actions = []
    today_ivs = digest.get("today_interviews", [])
    tomorrow_ivs = digest.get("tomorrow_interviews", [])
    overdue = digest.get("overdue_followups", [])

    if today_ivs:
        actions.append(("[bold red]INTERVIEW TODAY[/bold red]", f"You have {len(today_ivs)} interview(s) today. Prepare now!"))
    if tomorrow_ivs:
        actions.append(("[bold yellow]INTERVIEW TOMORROW[/bold yellow]", f"{len(tomorrow_ivs)} interview(s) tomorrow."))
    if overdue:
        actions.append(("[bold magenta]FOLLOW-UPS[/bold magenta]", f"{len(overdue)} application(s) need follow-up."))
    if apps_this_week < target_apps:
        actions.append(("[bold blue]APPLY[/bold blue]", f"Apply to {target_apps - apps_this_week} more role(s) this week to hit your goal."))
    if not actions:
        actions.append(("[bold green]ALL CAUGHT UP[/bold green]", "You're on top of everything. Great job!"))

    action_panels = [Panel(f"{title}\n[dim]{desc}[/dim]", border_style="green", padding=(1, 1)) for title, desc in actions]
    console.print(Columns(action_panels, equal=True))

    # Quick Stats
    console.print("\n[bold]At a Glance[/bold]")
    stats_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    stats_table.add_column(style="bold cyan")
    stats_table.add_column()
    total = sum(pipeline.values())
    active = total - pipeline.get("Rejected", 0) - pipeline.get("Accepted", 0) - pipeline.get("Withdrawn", 0) - pipeline.get("Ghosted", 0)
    stats_table.add_row(str(total), "Total Applications")
    stats_table.add_row(str(active), "Active in Pipeline")
    stats_table.add_row(str(pipeline.get("Offer", 0) + pipeline.get("Negotiating", 0) + pipeline.get("Accepted", 0)), "Offers")
    stats_table.add_row(str(len(today_ivs)), "Interviews Today")
    stats_table.add_row(str(len(overdue)), "Overdue Follow-ups")
    console.print(stats_table)

    # Pipeline Bar
    console.print("\n[bold]Pipeline[/bold]")
    pipe_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    pipe_table.add_column(style="bold", width=20)
    pipe_table.add_column()
    status_order = ["Applied", "Phone Screen", "Technical Screen", "Interview Round 1", "Interview Round 2", "Interview Round 3", "Final Round", "Offer", "Negotiating", "Accepted", "Rejected", "Withdrawn", "Ghosted"]
    for status in status_order:
        if status in pipeline:
            bar = "#" * pipeline[status] + "-" * (max(0, 5 - pipeline[status]))
            color = {
                "Applied": "blue", "Phone Screen": "cyan", "Technical Screen": "cyan",
                "Interview Round 1": "yellow", "Interview Round 2": "yellow", "Interview Round 3": "yellow",
                "Final Round": "magenta", "Offer": "green", "Negotiating": "green", "Accepted": "bold green",
                "Rejected": "red", "Withdrawn": "dim", "Ghosted": "dim"
            }.get(status, "white")
            pipe_table.add_row(status, f"[{color}]{bar}[/{color}]  {pipeline[status]}")
    console.print(pipe_table)

    # Upcoming
    upcoming = get_upcoming_interviews(hours=168)
    if upcoming:
        console.print("\n[bold]Upcoming Interviews[/bold]")
        iv_table = Table(box=box.SIMPLE, padding=(0, 1))
        iv_table.add_column("When", style="green", width=16)
        iv_table.add_column("Company", style="bold")
        iv_table.add_column("Type")
        for iv in upcoming[:5]:
            dt = datetime.fromisoformat(iv[4]) if iv[4] else None
            when = dt.strftime("%a %b %d %H:%M") if dt else "TBD"
            company = iv[15] if len(iv) > 15 else "?"
            role = iv[16] if len(iv) > 16 else "?"
            iv_table.add_row(when, f"{company}", f"{iv[3]} (R{iv[2]})")
        console.print(iv_table)

    # Recent Activity
    recent = get_recent_activity(5)
    if recent:
        console.print("\n[bold]Recent Activity[/bold]")
        act_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        act_table.add_column(style="dim", width=10)
        act_table.add_column()
        for act in recent:
            ts = act[2][:10] if act[2] else ""
            act_table.add_row(ts, act[1])
        console.print(act_table)

    # Quick Help
    help_text = """
[dim]Quick commands:[/dim]  [bold]add[/bold]  [bold]list[/bold]  [bold]today[/bold]  [bold]digest[/bold]  [bold]pipeline[/bold]  [bold]followups[/bold]  [bold]report[/bold]  [bold]wizard[/bold]
[dim]Documents:[/dim]  [bold]resume[/bold]  [bold]cover[/bold]  [bold]parse[/bold]
[dim]Or just run:[/dim] [bold green]python career.py wizard[/bold green] [dim]for an interactive menu[/dim]
    """
    console.print(Panel(help_text.strip(), title="[dim]How to use[/dim]", border_style="dim", padding=(1, 2)))

if __name__ == "__main__":
    render_home()
