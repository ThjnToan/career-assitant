# CareerAssistant Pro - User Guide (Web App)

Welcome to CareerAssistant Pro! This is your personal job search command center. Track applications, schedule interviews, analyze job descriptions, and stay on top of your search - all in one beautiful web app.

---

## Quick Start

### 1. Start the App

Open a terminal in this folder and run:

```bash
python run.py
```

Then open your browser to: **http://localhost:5000**

Or simply double-click `launch_web.bat`.

### 2. Create Your Account

Click **"Sign up"** on the login page and create your account.

### 3. Set Up Your Profile

After logging in, go to **Profile** and fill in:
- Your name and contact info
- Weekly goals (how many applications you want to send per week)
- Target roles

---

## Your Daily Workflow

### Morning Check (1 minute)

Open http://localhost:5000 and look at your **Dashboard**.

It shows you:
- Today's interviews (with a yellow alert banner)
- Overdue follow-ups (with a red alert banner)
- Your progress toward weekly goals
- Upcoming interviews
- Your pipeline

### When You Apply to a Job (30 seconds)

1. Click **"New Application"** or go to **Applications > + New Application**
2. Fill in:
   - Company (required)
   - Role (required)
   - Source (LinkedIn, Referral, etc.)
3. Optionally add: location, salary, job URL, description, notes
4. Click **"Log Application"**

**Pro tip:** Paste the job description too - you can parse it later for insights.

### When You Hear Back

1. Go to **Applications**
2. Find the company and click **"Edit"**
3. Change the status:
   - Applied &rarr; Phone Screen
   - Phone Screen &rarr; Technical Screen
   - Technical Screen &rarr; Interview Round 1
   - ...and so on
4. Add notes about what happened

### When You Schedule an Interview

1. Go to the application detail page (click the company name)
2. Scroll down to **"Schedule Interview"**
3. Fill in:
   - Type (Phone Screen, Technical, Behavioral, etc.)
   - Date and time
   - Interviewer name
   - Video link (Zoom, Teams, etc.)
   - Prep notes
4. Click **"Schedule"**

### Before an Interview

1. Go to **Interviews** to see all upcoming interviews
2. Click the company name to view the application detail
3. Review your notes and the job description
4. Use the **Parser** tool to extract key skills and talking points

---

## Weekly Review (5 minutes)

Every Friday, click **"Weekly Report"** on your dashboard or go to **Report**.

You'll see:
- How many applications you sent this week
- How that compares to last week
- Your pipeline breakdown
- Conversion rates (Applied &rarr; Screen &rarr; Interview &rarr; Offer)
- Which sources are working best

Use this to answer:
- Did I hit my goal? If not, why?
- Where am I getting stuck? (Need a better resume? More practice?)
- Should I focus more on referrals vs. LinkedIn?

---

## All Features

| Feature | How to Access | What It Does |
|---------|--------------|--------------|
| **Dashboard** | Homepage | Daily briefing with alerts, goals, pipeline, upcoming interviews |
| **Applications** | Top nav | Full list with search and filter by status |
| **New Application** | Dashboard or Applications page | Log a new job application |
| **Application Detail** | Click any company name | View details, edit, delete, schedule interviews |
| **Interviews** | Top nav | All upcoming and past interviews |
| **Pipeline** | Top nav | Visual funnel of all your applications by status |
| **Follow-ups** | Dashboard alert link | List of applications needing follow-up |
| **Parser** | Top nav | Paste a job description to extract skills, experience, and get tailoring suggestions |
| **Report** | Top nav | Weekly analytics with conversion rates |
| **Profile** | Top nav | Edit your info and goals |

---

## Pro Tips

### 1. The Golden Rule
**Log every application within 60 seconds of submitting it.**

The #1 reason job search tracking fails is procrastination. The #2 reason is forgetting. Do it immediately.

### 2. Use the Parser Before Every Application
Paste the job description into the **Parser** before you apply. It tells you:
- What skills they're looking for
- How many years of experience they want
- What soft skills to emphasize
Use this to tailor your resume and cover letter.

### 3. Follow-Up Discipline
The system automatically sets follow-up dates (7 days after applying). Check your dashboard every Monday. If you see a red alert, send that follow-up email.

### 4. Interview Notes Are Gold
After every interview, update the application with notes:
- What questions they asked
- How you answered
- What to improve for next time
- Interviewer personality/culture fit

This is invaluable when you reach Round 2 or 3.

### 5. Track Everything
Log rejections too. Your conversion analytics only work with complete data. Plus, seeing "20 applied, 5 interviews, 1 offer" is motivating. "I applied to a bunch of places" is demoralizing.

### 6. Make It a Game
Set realistic weekly goals and try to hit them. The progress bar on your dashboard makes it feel like a game you want to win.

---

## File Structure

```
CareerAssistant/
  run.py                 # Start the web app
  requirements.txt       # Python dependencies
  career_app.db          # Your data (applications, users, etc.)
  USER_GUIDE.md          # This file
  DEPLOY.md              # How to share with others
  app/                   # Backend code
    __init__.py
    models.py            # Database tables
    auth.py              # Login/register
    routes.py            # Web pages
    utils.py             # Parser, reports
  templates/             # HTML pages
    base.html            # Layout
    dashboard.html       # Home
    applications.html    # List
    application_form.html # Add/Edit
    application_detail.html # Detail + interviews
    interviews.html      # Interview list
    pipeline.html        # Pipeline view
    followups.html       # Follow-ups
    parser.html          # Job parser
    report.html          # Weekly report
    profile.html         # User profile
    auth/                # Login/register pages
  launch_web.bat         # One-click launcher
```

---

## Troubleshooting

**"Cannot connect to localhost:5000"**
- Make sure you ran `python run.py` and the terminal window is still open
- Check that no other app is using port 5000

**"Module not found" errors**
- Run: `pip install -r requirements.txt`

**Forgot your password**
- Delete `career_app.db` and restart (this deletes ALL data)
- Or ask the admin to reset it

**Want to start fresh**
- Stop the server, delete `career_app.db`, restart

---

## Sharing With Friends

See **DEPLOY.md** for how to let other people use this too.

---

Good luck with your job search! Consistency wins. 🎯
