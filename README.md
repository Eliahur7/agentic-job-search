# 🤖 Agentic Job Search — Autonomous Executive Job Discovery Engine

<div align="center">

![CI](https://github.com/Eliahur7/agentic-job-search/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?logo=openai&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Stars](https://img.shields.io/github/stars/Eliahur7/agentic-job-search?style=social)

**Stop manually refreshing job boards. Let AI do it for you.**

An autonomous, multi-agent pipeline that continuously scans LinkedIn, Indeed, Glassdoor & Remotive for roles that match your background — then auto-tailors your resume and cover letter, and tracks every application in a slick dashboard.

[🚀 Quick Start](#-quick-start) · [📋 Features](#-features) · [🤖 How It Works](#-how-it-works) · [🛠️ API Docs](#-api-endpoints) · [🤝 Contributing](CONTRIBUTING.md)

</div>

---

![Dashboard Preview](https://raw.githubusercontent.com/Eliahur7/agentic-job-search/main/docs/dashboard_preview.png)

> **⚠️ Disclaimer:** This is an educational proof-of-concept template. Use responsibly and in accordance with each job board's terms of service. Pre-configured with a fictional candidate "Jon Doe" — clone and replace with your own details.

---

## ✨ Why This Exists

Job searching is a full-time job. You refresh the same boards daily, copy-paste your resume into every application, and lose track of where you applied. This project automates the grunt work:

- 🔍 **Scans 6+ job boards** every time you click a button
- 🎯 **Scores each role** against your resume with weighted keyword matching  
- 📄 **Generates tailored resumes + cover letters** per company (with OpenAI or local fallback)
- 📊 **Tracks your pipeline** from `Evaluated → Applied → Interviewing → Offer`
- 📬 **Writes your outreach templates** — LinkedIn notes and cold emails, ready to send

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **Live Job Fetching** | Scrapes LinkedIn, Indeed, Glassdoor, Remotive, WeWorkRemotely, RemoteOK, Jobspresso |
| **AI Scoring** | Scores each role 0–100 against your resume with evidence-based matching |
| **Resume Tailoring** | Auto-generates tailored resumes + cover letters per company |
| **PDF Export** | Exports professional PDFs of every tailored document |
| **Pipeline Tracking** | SQLite-backed status tracking — Evaluated → Applied → Interviewing → Offer |
| **REST API** | Full FastAPI backend with Swagger docs at `/docs` |
| **Web Dashboard** | Single-page dashboard to search, review, and manage your pipeline |
| **CLI Tool** | Full command-line interface for power users |
| **Outreach Templates** | LinkedIn connection notes + cold emails generated per role |
| **Time-Bounded Search** | Smart 60-second budget — returns results fast, never hangs |

---

## 🚀 Quick Start

**Prerequisites:** Python 3.9+

```bash
# 1. Clone the repo
git clone https://github.com/Eliahur7/agentic-job-search.git
cd agentic-job-search

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Add your OpenAI key for AI-powered resume tailoring
echo 'OPENAI_API_KEY=sk-your-key-here' > .env

# 4. Start the server
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open **http://127.0.0.1:8000** — the dashboard is live. Click **"Scan For Vacancies"** to run your first search.

> **No OpenAI key?** No problem. The app falls back to local keyword-based resume tailoring automatically.

---

## 🤖 How It Works

```
┌─────────────────────────────────────────────────────────┐
│                   YOU click "Scan"                       │
└──────────────────────────┬──────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │     Job Hunter Agent    │
              │  LinkedIn · Indeed      │
              │  Glassdoor · Remotive   │
              │  WWR · RemoteOK · More  │
              └────────────┬────────────┘
                           │ Ranked job list
              ┌────────────▼────────────┐
              │   Resume Optimizer      │
              │   Tailored resume +     │
              │   cover letter (PDF)    │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   Networking Agent      │
              │   LinkedIn note +       │
              │   cold email template   │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   SQLite Pipeline DB    │
              │   Track every role      │
              │   from eval → offer     │
              └─────────────────────────┘
```

### Multi-Agent Architecture

| Agent | Purpose | Output |
|-------|---------|--------|
| **Job Hunter** | Fetch & score jobs across 6+ boards | Ranked job list with match scores |
| **Resume Optimizer** | Tailor resume to job description | Tailored resume + cover letter (PDF) |
| **Networking Agent** | Write outreach copy | LinkedIn note + cold email |
| **GitHub Growth** | Portfolio recommendations | Project ideas to fill skill gaps |

---

## 🛠️ Configuration

```bash
# OpenAI (optional — enables GPT-4 resume tailoring)
export OPENAI_API_KEY="sk-your-key-here"

# Disable specific job boards (all enabled by default)
export ENABLE_LINKEDIN_SCRAPING="0"
export ENABLE_BOARD_SCRAPING="0"      # Indeed
export ENABLE_GLASSDOOR_SCRAPING="0"
export ENABLE_JOB_API="0"            # Remotive + RSS feeds
```

**Customize for yourself:** Edit `REAL_RESUME_CONTEXT` in `backend/app/main.py` with your own resume text, and update the default keywords/location.

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/automation/run-daily-search` | Scan boards, score & store jobs |
| `POST` | `/api/v1/agent/daily-briefing` | Full briefing with resume tailoring |
| `GET` | `/api/v1/pipeline/snapshot` | View all tracked jobs |
| `POST` | `/api/v1/pipeline/mark-applied` | Mark a job as applied |
| `PATCH` | `/api/v1/pipeline/update-status` | Update job status |
| `POST` | `/api/v1/pipeline/{job_id}/tailor` | On-demand resume tailoring |
| `GET` | `/api/v1/pipeline/{job_id}/tailored-resume` | Download tailored PDF |
| `POST` | `/api/v1/pipeline/{job_id}/check-active` | Verify posting is still live |

Full interactive docs at **http://127.0.0.1:8000/docs**

---

## 🖥️ CLI Tool

```bash
# List all tracked jobs
python3 backend/app/cli.py list

# View daily digest
python3 backend/app/cli.py digest

# Mark a job as applied
python3 backend/app/cli.py mark "<job-id>" Applied --notes "Applied on 2026-06-25"

# Show job details
python3 backend/app/cli.py show "<job-id>"

# Filter by status
python3 backend/app/cli.py list --status Applied
```

---

## 💾 Database Schema

All jobs are persisted in `application_state.db` (SQLite):

```sql
CREATE TABLE processed_jobs (
    id TEXT PRIMARY KEY,              -- URL hash
    company TEXT,
    title TEXT,
    url TEXT,                         -- Job posting link
    raw_description TEXT,             -- Full job description
    match_score REAL,                 -- 0–100 score
    processed_at TEXT,
    status TEXT DEFAULT 'Evaluated',  -- Evaluated | Applied | Interviewing | Offer | Archived
    applied INTEGER DEFAULT 0,
    notes TEXT
);
```

---

## 📦 Project Structure

```
agentic-job-search/
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI server & endpoints
│       ├── automation.py           # Daily search orchestrator
│       ├── cli.py                  # CLI tool
│       ├── database.py             # SQLite layer
│       ├── dashboard.html          # Web dashboard (single-file UI)
│       ├── agents/
│       │   ├── job_hunter.py       # Multi-board scraper + scorer
│       │   ├── resume_optimizer.py # Resume & cover letter tailoring
│       │   ├── networking_agent.py # Outreach template generator
│       │   └── github_growth.py    # Portfolio recommendations
│       ├── utils/
│       │   ├── pdf_generator.py    # PDF export
│       │   └── pdf_utils.py        # PDF text extraction
│       └── workflows/
│           └── daily_briefing.py   # Digest compilation
├── company_research.py             # Company intel agent
├── requirements.txt
├── .github/workflows/ci.yml        # CI pipeline
└── CONTRIBUTING.md
```

---

## 🚢 Docker

```bash
docker-compose up --build
```

API available at `http://localhost:8000`.

---

## 📝 Roadmap

- [ ] Email/SMS notifications for new high-match jobs
- [ ] Scheduled automatic daily searches (cron)
- [ ] Interview prep — auto-generate Q&A from job descriptions
- [ ] ATS integrations (Lever, Greenhouse)
- [ ] More job boards (Dice, Wellfound, Built In)
- [ ] Resume upload via UI (replace hardcoded resume context)

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas we'd love help with: new job board scrapers, improved AI scoring, UI enhancements, and tests.

---

## 👨‍💻 Author

Created by **Ran Eliahu** via **Google AntiGravity** · [GitHub](https://github.com/Eliahur7)

If this saves you time in your job search, consider giving it a ⭐ — it helps other job seekers find it!

---

## 📞 Support

Open a [GitHub Issue](https://github.com/Eliahur7/agentic-job-search/issues) for bugs or feature requests.
