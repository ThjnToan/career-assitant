# CareerAssistant Pro

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Web%20App-green?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-Database-orange?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Dark%20Mode-Ready-purple?style=for-the-badge" />
</p>

<p align="center">
  <b>Your personal job search command center.</b><br>
  Track applications, schedule interviews, parse job descriptions, generate documents, and stay on top of your career hunt — all in one beautiful web app.
</p>

---

## Features

| Feature | Description |
|---------|-------------|
| **Interactive Dashboard** | Daily briefing with alerts, weekly goals, pipeline overview, and upcoming interviews |
| **Application Tracker** | Log and manage every job application with full lifecycle tracking |
| **Aesthetic Pipeline Funnel** | Visual gradient funnel showing your progress from Applied to Accepted |
| **Interview Scheduler** | Schedule interviews with prep notes, video links, and interviewer details |
| **Job Description Parser** | Extract skills, experience, and education requirements from any job posting |
| **Weekly Analytics** | Conversion rates, source effectiveness, and progress reports |
| **Dark Mode** | Full dark mode support with persistent preference |
| **Multi-User** | Each user has isolated data with secure authentication |
| **Document Generator** | Auto-generate tailored resumes and cover letters |

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ThjnToan/career-assitant.git
cd career-assitant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
python run.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5000**

---

## Screenshots

### Dashboard
Your daily command center with goals, alerts, pipeline, and upcoming interviews.

### Aesthetic Pipeline Funnel
Beautiful gradient funnel showing your job search journey from application to offer.

### Dark Mode
Full dark mode support across all pages. Toggle with one click.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask (Python) |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Authentication** | Flask-Login with password hashing |
| **Frontend** | Jinja2 templates + custom CSS |
| **CLI Tools** | Python with Rich console output |

---

## Project Structure

```
career-assistant/
├── app/                    # Flask application
│   ├── __init__.py        # App factory
│   ├── auth.py            # Login/register logic
│   ├── models.py          # Database models
│   ├── routes.py          # Web routes
│   └── utils.py           # Parser, reports, helpers
├── templates/             # HTML templates
│   ├── base.html          # Layout with dark mode
│   ├── dashboard.html     # Home dashboard
│   ├── pipeline.html      # Aesthetic funnel
│   ├── applications.html  # Application list
│   ├── interviews.html    # Interview calendar
│   ├── parser.html        # Job description analyzer
│   ├── report.html        # Weekly analytics
│   └── auth/              # Login/register pages
├── src/                   # CLI modules (optional)
│   ├── cli.py             # Command-line interface
│   ├── tracker.py         # Application CRUD
│   ├── parser.py          # Job description parser
│   ├── generator.py       # Resume/cover letter gen
│   ├── notifier.py        # Daily digest
│   └── reporter.py        # Weekly reports
├── resumes/               # Resume templates
├── cover_letters/         # Cover letter templates
├── data/                  # Config file
├── run.py                 # Start web app
├── career.py              # CLI entry point
└── requirements.txt       # Dependencies
```

---

## Usage

### Web App (Recommended)

1. **Register** an account at `/auth/register`
2. **Set your profile** at `/profile` (name, goals, target roles)
3. **Log applications** via the Dashboard or Applications page
4. **Track progress** on the Pipeline page
5. **Schedule interviews** from any application detail page
6. **Parse job descriptions** to extract key skills and requirements
7. **Review weekly** with the Report page

### CLI (Optional)

For terminal lovers, the CLI still works:

```bash
# Show daily dashboard
python career.py

# Quick-log an application
python career.py quick "Google" "Software Engineer"

# Interactive wizard
python career.py wizard
```

---

## Deployment

See **[DEPLOY.md](DEPLOY.md)** for detailed deployment options:

- **PythonAnywhere** (free, easiest)
- **Render** (free, auto-deploy)
- **Local Network** (share with friends on same WiFi)

---

## Roadmap

- [x] Web app with authentication
- [x] Aesthetic pipeline funnel
- [x] Dark mode
- [x] Job description parser
- [x] Weekly analytics
- [ ] Email notifications
- [ ] Resume PDF export
- [ ] Interview question bank
- [ ] Offer comparison tool
- [ ] Networking contact tracker

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## License

MIT License — feel free to use, modify, and share.

---

<p align="center">
  Built with persistence and caffeine. Good luck with your job search!
</p>
