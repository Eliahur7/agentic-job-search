import os
from typing import Optional

from backend.app.agents.job_hunter import fetch_live_jobs, fetch_live_jobs_with_target, analyze_and_score_job
from backend.app.agents.resume_optimizer import generate_tailored_assets
from backend.app.agents.networking_agent import generate_outreach_templates
from backend.app.workflows.daily_briefing import compile_executive_briefing
from backend.app.database import init_db, is_job_processed, mark_job_as_processed, get_all_processed_job_ids
from backend.app.utils.pdf_generator import export_text_document, export_pdf_document
from backend.app.utils.pdf_utils import extract_text_from_pdf
from company_research import research_company_profile
from backend.app.agents.github_growth import analyze_portfolio_opportunities

REAL_RESUME_CONTEXT = """
JON DOE
Chief AI Officer / VP of AI
San Francisco, CA | (555) 123-4567 | linkedin.com/in/jondoe

## EXECUTIVE PROFILE
Visionary AI Executive with 15+ years of experience leading enterprise-wide artificial intelligence strategy, machine learning initiatives, and large-scale digital transformation. Proven track record of building and scaling elite AI research and engineering organizations, driving generative AI adoption, and aligning technical execution with executive business outcomes. Deep expertise in LLMs, MLOps, and scalable AI infrastructure.

## CORE COMPETENCIES
- AI & Machine Learning Strategy | Generative AI & LLMs
- MLOps & Scalable AI Infrastructure | Data Science Leadership
- Enterprise AI Integration | AI Ethics & Governance
- Executive Stakeholder Alignment | R&D Organization Scaling

## PROFESSIONAL EXPERIENCE
### Tech Innovators Inc. | San Francisco, CA
**Vice President of AI & Data Science** | *Jan 2021 – Present*
- Architected and delivered an enterprise-wide generative AI platform, accelerating internal productivity by 40% organization-wide.
- Championed AI governance and ethics frameworks, significantly improving model fairness and regulatory compliance.
- Directed the deployment of automated MLOps pipelines, improving model availability and deployment consistency across enterprise workloads.
- Partnered with executive leadership to drive AI-driven cost reduction initiatives, delivering measurable operational savings.

**Director of Machine Learning Engineering** | *May 2017 – Dec 2020*
- Defined and executed a multi-year AI modernization roadmap focused on scalability, automation, and model resiliency.
- Led seamless migration of legacy predictive models to a modern, cloud-native ML infrastructure.
- Drove organization-wide adoption of MLOps standards and reusable model templates, eliminating deployment friction.

### Data Solutions Corp. | San Jose, CA
**Lead Data Scientist** | *Oct 2012 – Apr 2017*
- Introduced scalable data pipelines and distributed training environments, accelerating R&D timelines.
- Modernized core ML infrastructure and practices supporting enterprise analytics and future AI initiatives.

## TECHNOLOGY & PLATFORM EXPERTISE
- **AI & Machine Learning:** PyTorch, TensorFlow, Hugging Face, OpenAI API, LangChain
- **Cloud & Infrastructure:** AWS (SageMaker, EC2, S3), Kubernetes, Docker
- **MLOps & Data Platforms:** MLflow, Kubeflow, Databricks, Snowflake

## LEADERSHIP IMPACT
- Built and scaled AI engineering teams focused on innovation, operational excellence, and psychological safety.
- Recognized as a force multiplier who improves organizational effectiveness through AI enablement and strategic coaching.
- Strong advocate for AI-first engineering organizations where intelligent automation accelerates business outcomes.

## EDUCATION
### Stanford University | Stanford, CA
**Master of Science in Computer Science - Artificial Intelligence** | *2010 – 2012*

### University of California, Berkeley | Berkeley, CA
**Bachelor of Science in Computer Science** | *2006 – 2010*
"""




def _load_resume_text() -> str:
    return REAL_RESUME_CONTEXT



def run_daily_search(output_dir: Optional[str] = None, target_keywords: Optional[list] = None, target_location: Optional[str] = None, min_new_jobs: int = 10) -> dict:
    """Run the daily job search, score roles, persist them, and create tailored assets."""
    if target_keywords is None:
        target_keywords = [
            "Chief AI Officer", "Vice President of AI", "VP of AI",
            "Head of AI", "Director of Artificial Intelligence", "Head of Machine Learning",
        ]
    if target_location is None:
        target_location = "Wisconsin or Remote"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    output_dir = output_dir or os.path.join(project_root, "tailored_applications")
    os.makedirs(output_dir, exist_ok=True)

    # Ensure local storage is initialized before persisting pipeline state.
    init_db()
    processed_ids = get_all_processed_job_ids()
    resume_text = _load_resume_text()
    live_scraped_data = fetch_live_jobs_with_target(target_keywords, target_location, processed_job_ids=processed_ids, min_target=min_new_jobs)


    evaluated_jobs = []
    for job in live_scraped_data:
        job_id = job.get("id") or job.get("url") or f"{job['company']}_{job['title']}"
        job_id = str(job_id)

        if is_job_processed(job_id):
            continue

        analysis = analyze_and_score_job(job.get("description", ""), resume_text)
        evaluated_jobs.append({
            "id": job_id,
            "title": job.get("title", "Untitled Role"),
            "company": job.get("company", "Unknown Company"),
            "description": job.get("description", ""),
            "url": job.get("url"),            "apply_url": job.get("apply_url"),
            "location": job.get("location"),
            "source": job.get("source"),            "match_score": analysis["match_score"],
            "analysis": analysis,
        })

    evaluated_jobs = sorted(evaluated_jobs, key=lambda item: item["match_score"], reverse=True)

    documents_created = 0
    for job in evaluated_jobs[:2]:
        company_clean = job["company"].replace(" ", "_").strip() or "company"
        assets = generate_tailored_assets(resume_text, job["description"])
        outreach = generate_outreach_templates(job["company"], job["title"], resume_text)

        resume_md_path = os.path.join(output_dir, f"{company_clean}_Tailored_Resume.md")
        letter_md_path = os.path.join(output_dir, f"{company_clean}_Cover_Letter.md")
        networking_md_path = os.path.join(output_dir, f"{company_clean}_Outreach_Templates.md")
        resume_doc_path = os.path.join(output_dir, f"{company_clean}_Tailored_Resume.doc")
        letter_doc_path = os.path.join(output_dir, f"{company_clean}_Cover_Letter.doc")
        resume_pdf_path = os.path.join(output_dir, f"{company_clean}_Tailored_Resume.pdf")
        letter_pdf_path = os.path.join(output_dir, f"{company_clean}_Cover_Letter.pdf")

        full_resume_text = assets.get("full_tailored_resume_text", "Failed to compile full resume text.")
        cover_letter_content = assets.get("tailored_cover_letter", "Failed to compile cover letter text.")

        with open(resume_md_path, "w") as handle:
            handle.write(full_resume_text)
        with open(letter_md_path, "w") as handle:
            handle.write(cover_letter_content)
        with open(networking_md_path, "w") as handle:
            handle.write(f"# Executive Outreach Campaign for {job['company']}\n")
            handle.write(f"Target Role: {job['title']}\n\n")
            handle.write("## 🔗 LinkedIn Connection Note:\n`````\n")
            handle.write(f"{outreach.get('linkedin_connection_note')}\n")
            handle.write("`````\n\n")
            handle.write(f"## ✉️ Direct Cold Email:\n**Subject:** {outreach.get('cold_email_subject')}\n\n{outreach.get('cold_email_body')}\n")

        export_text_document(resume_doc_path, full_resume_text)
        export_text_document(letter_doc_path, cover_letter_content)
        export_pdf_document(resume_pdf_path, f"{job['company']} - Tailored Resume", full_resume_text)
        export_pdf_document(letter_pdf_path, f"{job['company']} - Cover Letter", cover_letter_content)

        documents_created += 6

    for job in evaluated_jobs:
        mark_job_as_processed(
            job["id"],
            job["company"],
            job["title"],
            job["match_score"],
            url=job.get("url"),
            apply_url=job.get("apply_url"),
            location=job.get("location"),
            source=job.get("source"),
            raw_description=job.get("description")
        )

    top_company = evaluated_jobs[0]["company"] if evaluated_jobs else "Target Enterprise"
    company_intel = research_company_profile(top_company)
    company_intel["company_name"] = top_company
    portfolio_focuses = ["Streamlit Financial Analytics Web App", "AWS Multi-Region Terraform Modules"]
    portfolio_tasks = analyze_portfolio_opportunities(portfolio_focuses)
    briefing_markdown = compile_executive_briefing(evaluated_jobs, company_intel, portfolio_tasks)

    return {
        "jobs_found": len(evaluated_jobs),
        "documents_created": documents_created,
        "briefing_markdown": briefing_markdown,
        "jobs": evaluated_jobs,
    }
