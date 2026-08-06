import os
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import FileResponse
from backend.app.agents.job_hunter import fetch_live_jobs, fetch_live_jobs_with_target, analyze_and_score_job, _page_looks_closed, HEADERS
from backend.app.agents.resume_optimizer import generate_tailored_assets
from company_research import research_company_profile
from backend.app.agents.github_growth import analyze_portfolio_opportunities
from backend.app.workflows.daily_briefing import compile_executive_briefing
from backend.app.agents.networking_agent import generate_outreach_templates
from backend.app.database import init_db, remove_mock_jobs, remove_duplicate_jobs, is_job_processed, get_all_processed_job_ids, mark_job_as_processed, update_job_status, get_pipeline_snapshot
from backend.app.utils.pdf_generator import export_text_document, export_pdf_document
from backend.app.utils.pdf_utils import extract_text_from_pdf
from backend.app.automation import run_daily_search

app = FastAPI(title="Agentic Job Search API (Production Tier)", version="3.0")

@app.on_event("startup")
def startup_event():
    init_db()
    remove_mock_jobs()
    remove_duplicate_jobs()

class StatusUpdateRequest(BaseModel):
    job_id: str
    status: str
    notes: str = None


class MarkAppliedRequest(BaseModel):
    job_id: str
    notes: Optional[str] = None


class SearchRequest(BaseModel):
    keywords: Optional[list[str]] = None
    location: Optional[str] = None

# YOUR EXACT FULL REAL RESUME BASE CONTEXT
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



@app.post("/api/v1/agent/daily-briefing")
async def generate_daily_digest():
    # Focused target keywords filtering explicitly for high-level AI leadership positions
    target_keywords = [
        "Chief AI Officer", "Vice President of AI", "VP of AI",
        "Head of AI", "Director of Artificial Intelligence", "Head of Machine Learning",
    ]
    target_location = "Wisconsin or Remote"

    resume_text = REAL_RESUME_CONTEXT
    
    # 1. Fetch relevant enterprise target vacancies (ensuring at least 10 new positions)

    processed_ids = get_all_processed_job_ids()
    live_scraped_data = fetch_live_jobs_with_target(target_keywords, target_location, processed_job_ids=processed_ids, min_target=10)

    
    evaluated_jobs = []
    for job in live_scraped_data:
        job_id = str(job.get("id") or job.get("url") or f"{job['company']}_{job['title']}".replace(" ", "_"))
        
        if is_job_processed(job_id):
            print(f"[State Engine] Skipping already tracked job id: {job_id}")
            continue
            
        analysis = analyze_and_score_job(job.get("description", ""), resume_text)
        evaluated_jobs.append({
            "id": job_id,
            "title": job.get("title", "Untitled Role"),
            "company": job.get("company", "Unknown Company"),
            "description": job.get("description", ""),
            "url": job.get("url"),
            "apply_url": job.get("apply_url"),
            "location": job.get("location", "Remote"),
            "source": job.get("source", "Unknown"),
            "match_score": analysis["match_score"],
            "analysis": analysis
        })
    
    evaluated_jobs = sorted(evaluated_jobs, key=lambda x: x["match_score"], reverse=True)
    
    # 2. Setup local system storage directories
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
    output_dir = os.path.join(PROJECT_ROOT, "tailored_applications")
    os.makedirs(output_dir, exist_ok=True)

    # 3. Process documents for the top matching roles
    for job in evaluated_jobs[:2]: 
        company_clean = job["company"].replace(" ", "_").strip()
        
        # Call agents to generate the tailored full document text maps
        assets = generate_tailored_assets(resume_text, job["description"])
        outreach = generate_outreach_templates(job["company"], job["title"], resume_text)
        
        # File path blueprints
        resume_md_path = os.path.join(output_dir, f"{company_clean}_Tailored_Resume.md")
        letter_md_path = os.path.join(output_dir, f"{company_clean}_Cover_Letter.md")
        networking_md_path = os.path.join(output_dir, f"{company_clean}_Outreach_Templates.md")
        
        resume_doc_path = os.path.join(output_dir, f"{company_clean}_Tailored_Resume.doc")
        letter_doc_path = os.path.join(output_dir, f"{company_clean}_Cover_Letter.doc")
        resume_pdf_path = os.path.join(output_dir, f"{company_clean}_Tailored_Resume.pdf")
        letter_pdf_path = os.path.join(output_dir, f"{company_clean}_Cover_Letter.pdf")

        # Capture the complete rewritten text blocks
        full_resume_text = assets.get("full_tailored_resume_text", "Failed to compile full resume text.")
        cover_letter_content = assets.get("tailored_cover_letter", "Failed to compile cover letter text.")

        # Write pristine markdown formats to disk
        with open(resume_md_path, "w") as f:
            f.write(full_resume_text)
        with open(letter_md_path, "w") as f:
            f.write(cover_letter_content)

        # Write communication assets to local directory
        with open(networking_md_path, "w") as f:
            f.write(f"# Executive Outreach Campaign for {job['company']}\n")
            f.write(f"Target Role: {job['title']}\n\n")
            f.write("## 🔗 LinkedIn Connection Note:\n`````\n")
            f.write(f"{outreach.get('linkedin_connection_note')}\n")
            f.write("`````\n\n")
            f.write(f"## ✉️ Direct Cold Email:\n**Subject:** {outreach.get('cold_email_subject')}\n\n{outreach.get('cold_email_body')}\n")

        # Export clean, fully formed textual documents to disk (.doc file layouts)
        export_text_document(resume_doc_path, full_resume_text)
        export_text_document(letter_doc_path, cover_letter_content)
        # Attempt to also generate PDFs (if reportlab is installed)
        export_pdf_document(resume_pdf_path, f"{job['company']} - Tailored Resume", full_resume_text)
        export_pdf_document(letter_pdf_path, f"{job['company']} - Cover Letter", cover_letter_content)

    for job in evaluated_jobs:
        # Mark as processed in database (store url and raw description)
        mark_job_as_processed(
            job["id"],
            job["company"],
            job["title"],
            job["match_score"],
            url=job.get("url"),
            location=job.get("location"),
            source=job.get("source"),
            raw_description=job.get("description")
        )

    # 4. Generate summary view executive briefing dashboard
    top_company = evaluated_jobs[0]["company"] if evaluated_jobs else "Target Enterprise"
    company_intel = research_company_profile(top_company)
    company_intel["company_name"] = top_company
    
    portfolio_focuses = ["Streamlit Financial Analytics Web App", "AWS Multi-Region Terraform Modules"]
    portfolio_tasks = analyze_portfolio_opportunities(portfolio_focuses)
    
    markdown_briefing = compile_executive_briefing(evaluated_jobs, company_intel, portfolio_tasks)
    return Response(content=markdown_briefing, media_type="text/markdown")

@app.get("/api/v1/pipeline/snapshot")
async def view_job_pipeline():
    return {"pipeline": get_pipeline_snapshot()}


@app.post("/api/v1/automation/run-daily-search")
async def run_daily_search_endpoint(payload: Optional[SearchRequest] = None):
    summary = run_daily_search(
        target_keywords=payload.keywords if payload and payload.keywords else None,
        target_location=payload.location if payload and payload.location else None,
    )
    return {"status": "success", "summary": summary}


@app.post("/api/v1/pipeline/{job_id}/tailor")
async def tailor_resume_for_job(job_id: str):
    """Create an on-demand, role-specific resume from the saved job description."""
    job = next((item for item in get_pipeline_snapshot() if item["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found in the pipeline.")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    resume_text = REAL_RESUME_CONTEXT
    assets = generate_tailored_assets(resume_text, job.get("raw_description") or "")


    output_dir = os.path.join(project_root, "tailored_applications")
    os.makedirs(output_dir, exist_ok=True)
    safe_company = "".join(char if char.isalnum() else "_" for char in job["company"]).strip("_") or "company"
    stem = f"{safe_company}_{job_id[:8]}_Tailored_Resume"
    markdown_path = os.path.join(output_dir, stem + ".md")
    pdf_path = os.path.join(output_dir, stem + ".pdf")
    content = assets["full_tailored_resume_text"]
    with open(markdown_path, "w") as handle:
        handle.write(content)
    export_pdf_document(pdf_path, f"{job['company']} - Tailored Resume", content)
    return {
        "status": "success",
        "resume_markdown": content,
        "resume_download_url": f"/api/v1/pipeline/{job_id}/tailored-resume",
        "company": job["company"],
        "title": job["title"],
    }


@app.get("/api/v1/pipeline/{job_id}/tailored-resume")
async def download_tailored_resume(job_id: str):
    job = next((item for item in get_pipeline_snapshot() if item["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found in the pipeline.")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    safe_company = "".join(char if char.isalnum() else "_" for char in job["company"]).strip("_") or "company"
    path = os.path.join(project_root, "tailored_applications", f"{safe_company}_{job_id[:8]}_Tailored_Resume.pdf")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Tailor this resume first.")
    return FileResponse(path, media_type="application/pdf", filename=os.path.basename(path))


@app.post("/api/v1/pipeline/{job_id}/check-active")
async def check_job_active(job_id: str):
    """Real-time active validation check for individual job postings."""
    job = next((item for item in get_pipeline_snapshot() if item["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found in the pipeline.")
    
    url = job.get("url")
    if not url or not url.startswith("http"):
        return {"status": "unknown", "message": "Cannot verify non-HTTP URL"}
        
    try:
        import requests
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 404 or _page_looks_closed(resp.text):
            update_job_status(job_id, "Archived", "Position closed/expired (verified during active status check)")
            return {"status": "inactive", "message": "Position is closed; moved to Archived"}
        else:
            return {"status": "active", "message": "Position is still active"}
    except Exception as e:
        return {"status": "unknown", "message": f"Verification error: {str(e)}"}



@app.get("/", include_in_schema=False)
async def ui_home():
    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")
    return FileResponse(
        dashboard_path,
        media_type="text/html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )

@app.patch("/api/v1/pipeline/update-status")
async def transition_job_state(payload: StatusUpdateRequest):
    update_job_status(payload.job_id, payload.status, payload.notes)
    return {"status": "success", "message": f"Job {payload.job_id} transitioned successfully to {payload.status}"}


@app.post("/api/v1/pipeline/mark-applied")
async def mark_job_applied(payload: MarkAppliedRequest):
    """Convenience endpoint to mark a tracked job as Applied."""
    update_job_status(payload.job_id, "Applied", payload.notes)
    return {"status": "success", "message": f"Job {payload.job_id} marked as Applied"}
