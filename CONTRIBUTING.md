# 🤝 Contributing to Agentic Job Search

Thank you for your interest in contributing! This project is an open-source, community-driven job search automation engine. All contributions — bug fixes, new features, documentation improvements, and ideas — are welcome.

---

## 🚀 Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/<your-username>/agentic-job-search.git
cd agentic-job-search
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Server Locally
```bash
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Create a Feature Branch
```bash
git checkout -b feat/your-feature-name
```

---

## 🧠 Areas to Contribute

Here are some great places to start:

| Area | Ideas |
|------|-------|
| **Job Boards** | Add new scrapers (Dice, Wellfound, Built In, etc.) |
| **AI / Agents** | Improve match scoring, add interview prep agent |
| **Dashboard UI** | Improve the frontend dashboard experience |
| **Notifications** | Email/SMS alerts for new high-match jobs |
| **Testing** | Add unit and integration tests |
| **Docs** | Improve setup guides, add video walkthrough |
| **Scheduling** | Cron-based automatic daily searches |

---

## 📋 Pull Request Guidelines

1. **Keep PRs focused** — one feature or fix per PR
2. **Write clear commit messages** using [Conventional Commits](https://www.conventionalcommits.org/) format:
   - `feat: add Dice.com job scraper`
   - `fix: handle LinkedIn rate limiting`
   - `docs: improve setup instructions`
3. **Test your changes** before submitting
4. **Update the README** if you add a new feature or change behavior
5. **Be respectful** — this is a welcoming community

---

## 🐛 Reporting Bugs

Please open a [GitHub Issue](https://github.com/ran-eliahu/agentic-job-search/issues) with:
- A clear description of the bug
- Steps to reproduce it
- Expected vs. actual behavior
- Your OS and Python version

---

## 💡 Suggesting Features

Open a [GitHub Issue](https://github.com/ran-eliahu/agentic-job-search/issues) with the `enhancement` label. Describe the use case and what value it would add for job seekers.

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as this project.

---

Built with ❤️ by [Ran Eliahu](https://github.com/ran-eliahu) — contributions make this better for every job seeker who uses it.
