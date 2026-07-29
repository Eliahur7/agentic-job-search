# 🤖 Chief-of-Staff AI — The Ultimate Multi-Agent Executive Job Search Engine

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-009688?logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?logo=openai&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![AI Agents](https://img.shields.io/badge/Architecture-Multi--Agent-FF9900)
![Status](https://img.shields.io/badge/Status-Template-success)

> **🚀 Welcome to the Future of Job Hunting**
> An AI-powered, autonomous pipeline system that continuously scans for executive roles, meticulously tailors your resume and cover letters, and tracks your application progress through an intuitive API and CLI.

This repository is an **example template** showcasing what a modern, AI-first job search engine looks like. It is pre-configured with a fictional AI Executive ("Jon Doe") to demonstrate how you can leverage generative AI, agentic architectures, and automated pipelines to land your next leadership role. **Clone this repository to build your own personal career engine!**

### 🏷️ Recommended GitHub Tags 
Add these to your repository topics to grab attention: `ai`, `multi-agent`, `job-search`, `resume-builder`, `fastapi`, `openai`, `python`, `career-automation`, `generative-ai`

> **⚠️ Note:** This is an explorational and educational proof-of-concept. Use this as a reference or inspiration for building your own tools!

## 🎯 Features

- **Live Job Fetching**: Integrates with Remotive API to fetch remote and Milwaukee-area jobs (or use mock feed)
- **AI-Powered Matching**: Scores jobs against your background using keyword analysis
- **Resume Tailoring**: Auto-generates tailored resumes and cover letters (with OpenAI integration)
- **PDF Export**: Generates professional PDF versions of tailored documents
- **Job Pipeline Tracking**: SQLite-backed persistence with multi-status tracking (Evaluated → Applied → Interviewing → Offer)
- **REST API**: Full-featured FastAPI endpoints for pipeline management
- **CLI Tool**: Interactive command-line interface for viewing and managing your job pipeline
- **Daily Digest**: Automatic markdown briefing with matched opportunities and portfolio recommendations
- **Interactive Job Search**: Set target titles and location in the dashboard, review the title, company, match evidence, and apply link, then create a role-specific resume on demand

---

## 🚀 Quick Start

### Local Development

**Prerequisites:** Python 3.9+

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Start the FastAPI server:**
```bash
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**3. In another terminal, fetch and process jobs:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/agent/daily-briefing
```

**4. View your job pipeline:**
```bash
curl -X GET http://127.0.0.1:8000/api/v1/pipeline/snapshot | jq
```

---

## 🛠️ Configuration

### Environment Variables

Set these to enable advanced features:

```bash
# OpenAI Integration (optional)
export OPENAI_API_KEY="sk-your-key-here"
export ENABLE_OPENAI="1"  # Set to "1" to enable

# Live Job Fetching (enabled by default; set to 0 to disable)
export ENABLE_JOB_API="0"  # Disable the Remotive public API if desired

# Public board listing fetches are enabled by default. Set either to 0 to opt out.
export ENABLE_LINKEDIN_SCRAPING="0"
export ENABLE_BOARD_SCRAPING="0"  # Indeed; Glassdoor is also queried when reachable
export ENABLE_GLASSDOOR_SCRAPING="0"
```

**Default behavior (without env vars):**
- Searches public job listing pages when they are reachable; the app never inserts a demo or mock opening into the live pipeline
- Generates an evidence-preserving, local tailored resume and cover letter when OpenAI is not configured
- Persists all jobs and statuses locally in SQLite

Job boards change frequently and may restrict automated access. This app treats the returned canonical listing as the application handoff, does not attempt login or bypass access controls, and should be used in accordance with each site's terms.

---

## 📋 API Endpoints

### POST /api/v1/agent/daily-briefing
Fetch live jobs, score them, tailor resumes, and return markdown briefing.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/agent/daily-briefing
```

**Response:** Markdown digest with job matches, company intel, and portfolio recommendations.

---

### GET /api/v1/pipeline/snapshot
Retrieve all tracked jobs with status and scores.

```bash
curl -X GET http://127.0.0.1:8000/api/v1/pipeline/snapshot | jq
```

---

### POST /api/v1/pipeline/mark-applied
Mark a job as applied.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/pipeline/mark-applied \
  -H "Content-Type: application/json" \
  -d '{"job_id":"<job-id>", "notes":"Applied via LinkedIn"}'
```

---

### PATCH /api/v1/pipeline/update-status
Update job status (e.g., Applied → Interviewing).

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/pipeline/update-status \
  -H "Content-Type: application/json" \
  -d '{"job_id":"<job-id>", "status":"Interviewing", "notes":"Phone screen Friday"}'
```

---

## 🖥️ CLI Tool

Manage your pipeline from the command line:

### List all jobs:
```bash
python3 backend/app/cli.py list
```

### View daily digest:
```bash
python3 backend/app/cli.py digest
```

### Mark a job as applied:
```bash
python3 backend/app/cli.py mark "<job-id>" Applied --notes "Applied on 2026-06-25"
```

### Show job details:
```bash
python3 backend/app/cli.py show "<job-id>"
```

### Filter by status:
```bash
python3 backend/app/cli.py list --status Applied
```

---

## 🤖 Multi-Agent System

The system uses autonomous agents for different tasks:

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Job Hunter** | Fetch & score jobs | Keywords, location | Ranked job list |
| **Resume Optimizer** | Tailor resumes | Master resume, job desc | Tailored resume + cover letter (PDF) |
| **Networking Agent** | Outreach templates | Company, role, resume | LinkedIn notes + cold email |
| **GitHub Growth** | Portfolio tips | Focus areas | Project ideas & recommendations |

---

## 💾 Database

All jobs and statuses are persisted in SQLite (`application_state.db`):

```sql
CREATE TABLE processed_jobs (
    id TEXT PRIMARY KEY,              -- URL hash
    company TEXT,
    title TEXT,
    url TEXT,                         -- Job posting link
    raw_description TEXT,             -- Full job description
    match_score REAL,                 -- 0-100 score
    processed_at TEXT,                -- Timestamp
    status TEXT DEFAULT 'Evaluated',  -- Evaluated | Applied | Interviewing | Offer | Archived
    applied INTEGER DEFAULT 0,        -- 1 if Applied, 0 otherwise
    notes TEXT                        -- User notes
);
```

---

## 📦 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI server
│   ├── cli.py                  # CLI tool
│   ├── database.py             # SQLite layer
│   ├── agents/
│   │   ├── job_hunter.py       # Job fetching
│   │   ├── resume_optimizer.py # Resume tailoring
│   │   ├── networking_agent.py # Outreach
│   │   └── github_growth.py    # Portfolio tips
│   ├── utils/
│   │   ├── pdf_generator.py    # PDF export
│   │   └── pdf_utils.py        # PDF extraction
│   └── workflows/
│       └── daily_briefing.py   # Digest compilation
├── Dockerfile
└── docker-compose.yml
```

---

## 🚢 Docker Deployment

```bash
docker-compose up --build
```

Access the API at `http://localhost:8000`.

---

## 🔄 Workflow Example

1. **Fetch jobs:**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/agent/daily-briefing
   ```

2. **Review pipeline:**
   ```bash
   python3 backend/app/cli.py digest
   ```

3. **Mark jobs as applied:**
   ```bash
   python3 backend/app/cli.py mark "<job-id>" Applied
   ```

4. **Track progress:**
   ```bash
   python3 backend/app/cli.py list --status Applied
   ```

---

## 📝 Next Steps

- [ ] Add email/SMS notifications for new high-match jobs
- [ ] Build web dashboard for pipeline visualization
- [ ] Implement job scheduling (hourly/daily fetches)
- [ ] Add interview prep (auto-generate Q&A from job descriptions)
- [ ] Integrate with ATS platforms (Lever, Greenhouse, etc.)

---

## 💡 About This Template Project

**Educational & Explorational Purpose:** This template was built as a technical showcase and proof-of-concept to demonstrate what modern AI and automation can accomplish for job seekers. It serves as an open-source educational tool and reference implementation for:

- Multi-agent system architecture
- AI-powered resume optimization
- Job matching and scoring algorithms
- SQLite-based persistence and pipeline tracking
- REST API design for recruiting workflows
- CLI tool development for career management

**Use Cases for Cloning:**
- Template for building your own personal AI-driven career tech
- Educational guide on integrating multi-agent systems
- Starting point for ATS automation and auto-apply bots
- Inspiration for automated resume optimization pipelines
- A glowing portfolio piece to show off your AI engineering skills

---

## �📞 Support

For issues, open a GitHub issue or contact the maintainer.

**Latest Update:** June 25, 2026 — Multi-agent system, API, CLI, and PDF export.
