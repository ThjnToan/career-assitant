"""CLI module - redesigned for human-centric interaction."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text

from src.database import init_db, insert_sample_data
from src.tracker import (
    add_application, update_status, get_application, list_applications,
    search_applications, delete_application, get_pipeline_counts,
    get_overdue_followups, add_interview, get_interviews_for_app,
    get_upcoming_interviews, update_interview, VALID_STATUSES
)
from src.parser import parse_job_description, generate_tailoring_suggestions
from src.generator import generate_tailored_resume, generate_cover_letter
from src.notifier import get_daily_digest, format_digest, check_and_notify
from src.reporter import generate_weekly_report, format_weekly_report, export_report_html
from src.home import render_home

console = Console()
CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

# ========== COMMANDS ==========

def cmd_init(args):
    init_db()
    if args.sample:
        insert_sample_data()
        console.print("[green]CareerAssistant initialized with sample data![/green]")
        console.print("[dim]Run `python career.py` to see your dashboard.[/dim]")
    else:
        console.print("[green]CareerAssistant initialized.[/green]")

def cmd_add(args):
    app_id = add_application(
        company=args.company,
        role=args.role,
        location=args.location or "",
        salary_range=args.salary or "",
        job_url=args.url or "",
        description=args.description or "",
        source=args.source or "",
        notes=args.notes or ""
    )
    console.print(f"[green]Logged application #{app_id}[/green] - {args.company} ({args.role})")

def cmd_quick(args):
    """Ultra-fast application entry. Only company and role required."""
    app_id = add_application(
        company=args.company,
        role=args.role,
        source=args.source or ""
    )
    console.print(f"[green]Quick-logged application #{app_id}[/green] - {args.company} ({args.role})")
    console.print("[dim]Run `python career.py show {}` to add details later.[/dim]".format(app_id))

def cmd_list(args):
    apps = list_applications(status=args.status, limit=args.limit)
    if not apps:
        console.print("[yellow]No applications found.[/yellow]")
        return

    table = Table(title="Your Applications")
    table.add_column("ID", style="cyan", no_wrap=True, width=4)
    table.add_column("Company", style="bold", width=18)
    table.add_column("Role", width=28)
    table.add_column("Status", style="magenta", width=18)
    table.add_column("Applied", style="green", width=12)
    table.add_column("Source", width=14)

    for app in apps:
        applied = app[9][:10] if app[9] else "N/A"
        table.add_row(str(app[0]), app[1], app[2], app[7], applied, app[8] or "")
    console.print(table)
    console.print(f"\n[dim]Showing {len(apps)} application(s). Use --status to filter.[/dim]")

def cmd_show(args):
    app = get_application(args.id)
    if not app:
        console.print(f"[red]Application {args.id} not found.[/red]")
        return

    status_color = {
        "Applied": "blue", "Phone Screen": "cyan", "Technical Screen": "cyan",
        "Interview Round 1": "yellow", "Interview Round 2": "yellow", "Interview Round 3": "yellow",
        "Final Round": "magenta", "Offer": "green", "Negotiating": "green", "Accepted": "bold green",
        "Rejected": "red", "Withdrawn": "dim", "Ghosted": "dim"
    }.get(app[7], "white")

    content = Text()
    content.append(f"{app[1]}\n", style="bold")
    content.append(f"{app[2]}\n", style="dim")
    content.append(f"Status: ", style="bold")
    content.append(f"{app[7]}\n", style=status_color)
    content.append(f"Location: {app[3] or 'N/A'}  |  Salary: {app[4] or 'N/A'}\n", style="dim")
    content.append(f"Source: {app[8] or 'N/A'}  |  Applied: {app[9][:10] if app[9] else 'N/A'}\n", style="dim")
    content.append(f"Follow-up: {app[11][:10] if app[11] else 'N/A'}\n", style="dim")
    if app[5]:
        content.append(f"URL: {app[5]}\n", style="dim blue")
    content.append(f"\n{app[12] or 'No notes yet.'}", style="italic" if not app[12] else "")

    console.print(Panel(content, title=f"Application #{app[0]}", border_style=status_color))

    interviews = get_interviews_for_app(args.id)
    if interviews:
        iv_table = Table(title="Interview History", show_lines=False)
        iv_table.add_column("R", style="cyan", width=3)
        iv_table.add_column("Type", width=16)
        iv_table.add_column("When", style="green", width=16)
        iv_table.add_column("Status", width=12)
        iv_table.add_column("With", width=30)
        for iv in interviews:
            when = iv[4][:16].replace('T', ' ') if iv[4] else "TBD"
            person = f"{iv[6] or ''}"
            if iv[7]:
                person += f" ({iv[7]})"
            iv_table.add_row(str(iv[2]), iv[3], when, iv[10], person)
        console.print(iv_table)
    else:
        console.print("[dim]No interviews scheduled yet.[/dim]")

def cmd_update(args):
    try:
        update_status(args.id, args.status, args.notes)
        console.print(f"[green]Updated #{args.id} to {args.status}[/green]")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")

def cmd_search(args):
    apps = search_applications(args.query)
    if not apps:
        console.print("[yellow]No matches found.[/yellow]")
        return
    table = Table(title=f"Search: '{args.query}'")
    table.add_column("ID", style="cyan")
    table.add_column("Company", style="bold")
    table.add_column("Role")
    table.add_column("Status", style="magenta")
    for app in apps:
        table.add_row(str(app[0]), app[1], app[2], app[7])
    console.print(table)

def cmd_delete(args):
    delete_application(args.id)
    console.print(f"[green]Application {args.id} deleted.[/green]")

def cmd_pipeline(args):
    counts = get_pipeline_counts()
    table = Table(title="Your Pipeline")
    table.add_column("Status", style="bold")
    table.add_column("Count", style="cyan", justify="right")
    status_order = ["Applied", "Phone Screen", "Technical Screen", "Interview Round 1", "Interview Round 2", "Interview Round 3", "Final Round", "Offer", "Negotiating", "Accepted", "Rejected", "Withdrawn", "Ghosted"]
    for status in status_order:
        if status in counts:
            table.add_row(status, str(counts[status]))
    for status, count in counts.items():
        if status not in status_order:
            table.add_row(status, str(count))
    console.print(table)

def cmd_followups(args):
    apps = get_overdue_followups()
    if not apps:
        console.print("[green]All caught up! No overdue follow-ups.[/green]")
        return
    table = Table(title="Follow-ups Needed")
    table.add_column("ID", style="cyan")
    table.add_column("Company", style="bold")
    table.add_column("Role")
    table.add_column("Applied", style="green")
    table.add_column("Due", style="red")
    for app in apps:
        table.add_row(str(app[0]), app[1], app[2],
                      app[9][:10] if app[9] else "N/A",
                      app[11][:10] if app[11] else "N/A")
    console.print(table)
    console.print("\n[dim]Tip: Use `python career.py update <id> <status> --notes` to log a follow-up.[/dim]")

def cmd_interview_add(args):
    try:
        iv_id = add_interview(
            args.application_id, args.type, args.date,
            args.duration, args.interviewer, args.title,
            args.location, args.link, args.notes
        )
        console.print(f"[green]Interview scheduled (#{iv_id})[/green]")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")

def cmd_interview_list(args):
    ivs = get_upcoming_interviews(hours=args.hours)
    if not ivs:
        console.print("[yellow]No upcoming interviews.[/yellow]")
        return
    table = Table(title=f"Upcoming Interviews")
    table.add_column("ID", style="cyan")
    table.add_column("Company", style="bold")
    table.add_column("Role")
    table.add_column("Type")
    table.add_column("When", style="green")
    table.add_column("With")
    for iv in ivs:
        when = iv[4][:16].replace('T', ' ') if iv[4] else "TBD"
        person = f"{iv[6] or ''}"
        table.add_row(str(iv[0]), iv[15], iv[16], iv[3], when, person)
    console.print(table)

def cmd_parse(args):
    text = args.file.read() if hasattr(args.file, 'read') else args.file
    result = parse_job_description(text)
    console.print("\n[bold]What the employer wants:[/bold]")
    if result['skills']:
        console.print(f"[cyan]Skills:[/cyan] {', '.join(result['skills'])}")
    if result['years_experience']:
        console.print(f"[cyan]Experience:[/cyan] {min(result['years_experience'])}+ years")
    if result['education']:
        console.print(f"[cyan]Education:[/cyan] {', '.join(result['education'])}")
    if result['soft_skills']:
        console.print(f"[cyan]Soft skills:[/cyan] {', '.join(result['soft_skills'])}")
    if args.suggest:
        suggestions = generate_tailoring_suggestions(text)
        console.print("\n[bold]How to tailor your application:[/bold]")
        for s in suggestions:
            console.print(f"  [green]->[/green] {s}")

def cmd_resume(args):
    try:
        path = generate_tailored_resume(args.description, args.role, args.company)
        console.print(f"[green]Resume ready:[/green] {path}")
    except Exception as e:
        console.print(f"[red]{e}[/red]")

def cmd_cover(args):
    try:
        path = generate_cover_letter(args.role, args.company, args.description or "")
        console.print(f"[green]Cover letter ready:[/green] {path}")
    except Exception as e:
        console.print(f"[red]{e}[/red]")

def cmd_digest(args):
    digest = get_daily_digest()
    console.print(format_digest(digest))

def cmd_today(args):
    render_home()

def cmd_report(args):
    report = generate_weekly_report()
    console.print(format_weekly_report(report))
    if args.html:
        path = export_report_html(report)
        console.print(f"[green]Report saved:[/green] {path}")

def cmd_notify(args):
    check_and_notify()
    console.print("[green]Notifications checked.[/green]")

def cmd_config(args):
    config = load_config()
    if args.view:
        console.print(json.dumps(config, indent=2))
        return
    if args.set:
        key, value = args.set
        keys = key.split(".")
        target = config
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        # Try to parse as number/bool
        if value.lower() in ("true", "yes"):
            value = True
        elif value.lower() in ("false", "no"):
            value = False
        elif value.isdigit():
            value = int(value)
        target[keys[-1]] = value
        save_config(config)
        console.print(f"[green]Updated {key} = {value}[/green]")
        return
    if args.edit:
        console.print("[yellow]Edit data/config.json directly for complex changes.[/yellow]")
        return
    # Default: show key info
    user = config.get("user", {})
    goals = config.get("goals", {})
    console.print(Panel.fit(
        f"[bold]{user.get('name', 'Not set')}[/bold]\n"
        f"{user.get('title', '')}\n"
        f"Target: {', '.join(goals.get('target_roles', []))}\n"
        f"Weekly goal: {goals.get('weekly_applications', 5)} applications, {goals.get('weekly_networking', 2)} networking",
        title="Your Profile"
    ))

# ========== INTERACTIVE WIZARD ==========

def wizard():
    console.print(Panel.fit(
        "[bold blue]CareerAssistant Pro[/bold blue]\nYour personal job search companion",
        title="Welcome", border_style="blue"
    ))

    while True:
        console.print("\n[bold]What would you like to do?[/bold]")
        console.print("  [cyan]1[/cyan]  Log a new application")
        console.print("  [cyan]2[/cyan]  View my applications")
        console.print("  [cyan]3[/cyan]  See today's dashboard")
        console.print("  [cyan]4[/cyan]  Check pipeline & stats")
        console.print("  [cyan]5[/cyan]  Generate resume / cover letter")
        console.print("  [cyan]6[/cyan]  Weekly report")
        console.print("  [cyan]7[/cyan]  Parse a job description")
        console.print("  [cyan]8[/cyan]  Follow-ups & interviews")
        console.print("  [cyan]9[/cyan]  Exit")

        choice = Prompt.ask("Pick a number", choices=["1","2","3","4","5","6","7","8","9"])

        if choice == "1":
            company = Prompt.ask("Company")
            role = Prompt.ask("Role title")
            source = Prompt.ask("Where did you find this? (LinkedIn, Referral, etc.)", default="")
            has_more = Confirm.ask("Add more details now? (location, salary, URL)", default=False)
            location = salary = url = description = notes = ""
            if has_more:
                location = Prompt.ask("Location", default="")
                salary = Prompt.ask("Salary range", default="")
                url = Prompt.ask("Job URL", default="")
                has_desc = Confirm.ask("Paste job description?", default=False)
                if has_desc:
                    console.print("[dim]Paste description, then press Ctrl+Z + Enter:[/dim]")
                    lines = []
                    while True:
                        try:
                            lines.append(input())
                        except EOFError:
                            break
                    description = "\n".join(lines)
                notes = Prompt.ask("Any notes?", default="")

            app_id = add_application(company, role, location, salary, url, description, source, notes)
            console.print(f"\n[green]Logged application #{app_id}[/green] - {company} ({role})")

            if description:
                parsed = parse_job_description(description)
                if parsed['skills']:
                    console.print(f"[dim]Top skills they want: {', '.join(parsed['skills'][:8])}[/dim]")

            if Confirm.ask("Generate documents now?", default=False):
                if Confirm.ask("Tailored resume?", default=True):
                    path = generate_tailored_resume(description, role, company)
                    console.print(f"[green]Resume: {path}[/green]")
                if Confirm.ask("Cover letter?", default=True):
                    path = generate_cover_letter(role, company, description)
                    console.print(f"[green]Cover letter: {path}[/green]")

        elif choice == "2":
            status_filter = Prompt.ask("Filter by status (or 'all')", default="all")
            status = None if status_filter == "all" else status_filter
            apps = list_applications(status=status, limit=20)
            if not apps:
                console.print("[yellow]No applications found.[/yellow]")
            else:
                table = Table(title="Your Applications")
                table.add_column("ID", style="cyan")
                table.add_column("Company", style="bold")
                table.add_column("Role")
                table.add_column("Status", style="magenta")
                for app in apps:
                    table.add_row(str(app[0]), app[1], app[2], app[7])
                console.print(table)
                if Confirm.ask("View details?", default=False):
                    app_id = IntPrompt.ask("Enter ID")
                    cmd_show(type('Args', (), {'id': app_id})())

        elif choice == "3":
            render_home()

        elif choice == "4":
            cmd_pipeline(None)
            console.print("\n[dim]Use `python career.py report --html` for full analytics.[/dim]")

        elif choice == "5":
            company = Prompt.ask("Company")
            role = Prompt.ask("Role")
            has_desc = Confirm.ask("Have a job description?", default=False)
            desc = ""
            if has_desc:
                console.print("[dim]Paste description, then press Ctrl+Z + Enter:[/dim]")
                lines = []
                while True:
                    try:
                        lines.append(input())
                    except EOFError:
                        break
                desc = "\n".join(lines)
            if Confirm.ask("Generate resume?", default=True):
                path = generate_tailored_resume(desc, role, company)
                console.print(f"[green]Resume: {path}[/green]")
            if Confirm.ask("Generate cover letter?", default=True):
                path = generate_cover_letter(role, company, desc)
                console.print(f"[green]Cover letter: {path}[/green]")

        elif choice == "6":
            cmd_report(type('Args', (), {'html': True})())

        elif choice == "7":
            console.print("[dim]Paste job description, then press Ctrl+Z + Enter:[/dim]")
            lines = []
            while True:
                try:
                    lines.append(input())
                except EOFError:
                    break
            text = "\n".join(lines)
            parsed = parse_job_description(text)
            console.print(f"\n[bold]Skills:[/bold] {', '.join(parsed['skills'])}")
            console.print(f"[bold]Experience:[/bold] {parsed['years_experience']}")
            suggestions = generate_tailoring_suggestions(text)
            console.print("\n[bold]Tailoring tips:[/bold]")
            for s in suggestions:
                console.print(f"  [green]->[/green] {s}")

        elif choice == "8":
            cmd_followups(None)
            cmd_interview_list(type('Args', (), {'hours': 168})())

        elif choice == "9":
            console.print("[blue]Good luck out there! You've got this.[/blue]")
            break

def main():
    parser = argparse.ArgumentParser(
        description="CareerAssistant Pro - your complete job search companion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
QUICK START:
  python career.py                    Show your daily dashboard (default)
  python career.py quick Google "SWE" Log an application in 2 seconds
  python career.py wizard             Interactive menu (easiest!)

COMMON COMMANDS:
  today, digest          Today's priorities & digest
  list                   All applications
  pipeline               Your hiring funnel
  followups              What needs your attention
  add                    Full application entry
  update <id> <status>   Move an application forward
  show <id>              View details & interviews
  search <query>         Find past applications
  resume, cover          Generate tailored documents
  parse                  Analyze a job description
  report --html          Weekly analytics
  config                 View/edit your profile
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init
    p_init = subparsers.add_parser("init", help="Initialize database")
    p_init.add_argument("--sample", action="store_true", help="Add sample data for testing")

    # Add / Log (synonyms)
    p_add = subparsers.add_parser("add", help="Log a job application (full)")
    p_add.add_argument("company", help="Company name")
    p_add.add_argument("role", help="Job title")
    p_add.add_argument("--location", default="", help="Location")
    p_add.add_argument("--salary", default="", help="Salary range")
    p_add.add_argument("--url", default="", help="Job posting URL")
    p_add.add_argument("--description", default="", help="Job description")
    p_add.add_argument("--source", default="", help="How you found it")
    p_add.add_argument("--notes", default="", help="Any notes")

    # Quick
    p_quick = subparsers.add_parser("quick", help="Ultra-fast log (company + role only)")
    p_quick.add_argument("company", help="Company name")
    p_quick.add_argument("role", help="Job title")
    p_quick.add_argument("--source", default="", help="Source (optional)")

    # List
    p_list = subparsers.add_parser("list", help="List applications")
    p_list.add_argument("--status", help="Filter by status")
    p_list.add_argument("--limit", type=int, default=50, help="Max results")

    # Show
    p_show = subparsers.add_parser("show", help="Show application details")
    p_show.add_argument("id", type=int, help="Application ID")

    # Update
    p_update = subparsers.add_parser("update", help="Update application status")
    p_update.add_argument("id", type=int, help="Application ID")
    p_update.add_argument("status", choices=VALID_STATUSES, help="New status")
    p_update.add_argument("--notes", default="", help="Additional notes")

    # Search
    p_search = subparsers.add_parser("search", help="Search applications")
    p_search.add_argument("query", help="Search term")

    # Delete
    p_delete = subparsers.add_parser("delete", help="Delete application")
    p_delete.add_argument("id", type=int, help="Application ID")

    # Pipeline
    subparsers.add_parser("pipeline", help="View pipeline overview")

    # Follow-ups
    subparsers.add_parser("followups", help="Show overdue follow-ups")

    # Interview add
    p_iv_add = subparsers.add_parser("interview-add", help="Schedule an interview")
    p_iv_add.add_argument("application_id", type=int, help="Application ID")
    p_iv_add.add_argument("type", help="Interview type (e.g. Behavioral, Technical)")
    p_iv_add.add_argument("date", help="Date/time (ISO format, e.g. 2026-05-01T14:00)")
    p_iv_add.add_argument("--duration", type=int, default=60, help="Duration in minutes")
    p_iv_add.add_argument("--interviewer", default="", help="Interviewer name")
    p_iv_add.add_argument("--title", default="", help="Interviewer title")
    p_iv_add.add_argument("--location", default="", help="Location / Video label")
    p_iv_add.add_argument("--link", default="", help="Video call URL")
    p_iv_add.add_argument("--notes", default="", help="Notes")

    # Interview list
    p_iv_list = subparsers.add_parser("interviews", help="List upcoming interviews")
    p_iv_list.add_argument("--hours", type=int, default=168, help="Hours ahead to look")

    # Parse
    p_parse = subparsers.add_parser("parse", help="Parse a job description")
    p_parse.add_argument("file", type=argparse.FileType('r', encoding='utf-8'), nargs='?', default=sys.stdin,
                         help="File with job description (default: paste into terminal)")
    p_parse.add_argument("--suggest", action="store_true", help="Show tailoring suggestions")

    # Resume
    p_resume = subparsers.add_parser("resume", help="Generate tailored resume")
    p_resume.add_argument("company", help="Company name")
    p_resume.add_argument("role", help="Role title")
    p_resume.add_argument("--description", default="", help="Job description text")

    # Cover letter
    p_cover = subparsers.add_parser("cover", help="Generate cover letter")
    p_cover.add_argument("company", help="Company name")
    p_cover.add_argument("role", help="Role title")
    p_cover.add_argument("--description", default="", help="Job description text")

    # Digest / Today / Home
    subparsers.add_parser("digest", help="Show daily digest")
    subparsers.add_parser("today", help="Show today's dashboard (same as default)")

    # Report
    p_report = subparsers.add_parser("report", help="Generate weekly report")
    p_report.add_argument("--html", action="store_true", help="Export as HTML")

    # Notify
    subparsers.add_parser("notify", help="Check and send notifications")

    # Wizard
    subparsers.add_parser("wizard", help="Launch interactive wizard")

    # Config
    p_config = subparsers.add_parser("config", help="View or edit your profile")
    p_config.add_argument("--view", action="store_true", help="Show full config JSON")
    p_config.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a config value (e.g. goals.weekly_applications 10)")
    p_config.add_argument("--edit", action="store_true", help="Show config file path")

    args = parser.parse_args()

    # DEFAULT: show home dashboard if no command given
    if not args.command:
        render_home()
        return

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "quick": cmd_quick,
        "list": cmd_list,
        "show": cmd_show,
        "update": cmd_update,
        "search": cmd_search,
        "delete": cmd_delete,
        "pipeline": cmd_pipeline,
        "followups": cmd_followups,
        "interview-add": cmd_interview_add,
        "interviews": cmd_interview_list,
        "parse": cmd_parse,
        "resume": cmd_resume,
        "cover": cmd_cover,
        "digest": cmd_digest,
        "today": cmd_today,
        "report": cmd_report,
        "notify": cmd_notify,
        "wizard": wizard,
        "config": cmd_config,
    }

    func = commands.get(args.command)
    if func:
        func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
