import os
from openai import OpenAI
import json
import re

api_key = os.environ.get("OPENAI_API_KEY")
enable_openai = os.environ.get("ENABLE_OPENAI", "0") == "1"

if enable_openai and api_key and api_key != "sk-your-api-key-here":
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None
else:
    client = None

def generate_tailored_assets(user_resume: str, job_description: str) -> dict:
    """
    Analyzes an executive resume against a target Director/VP job description and 
    returns a completely rewritten full resume and tailored cover letter formatted
    for concise executive impact.
    """
    prompt = f"""
    You are an Elite Executive Resume Writer specializing in Cloud Infrastructure, DevOps, and AI Platforms at the Assistant Director and Director levels.
    
    Your task is to take the candidate's core master resume and rewrite it to perfectly align with the target job description. 
    Maintain absolute technical authenticity and chronological truth while elevating bullet impact, conciseness, and executive layout.
    Clearly highlight the candidate's 12+ years of enterprise engineering and leadership experience.

    MASTER RESUME TO TAILOR:
    \"\"\"{user_resume}\"\"\"

    TARGET JOB DESCRIPTION:
    \"\"\"{job_description}\"\"\"

    CRITICAL INSTRUCTIONS:
    1. Structure the output into standard concise sections using markdown:
       ## EXECUTIVE PROFILE
       ## CORE COMPETENCIES
       ## PROFESSIONAL EXPERIENCE
       ## TECHNOLOGY & PLATFORM EXPERTISE
       ## LEADERSHIP IMPACT
       ## EDUCATION

    1a. For ## CORE COMPETENCIES, do NOT use bolding (**). Format them as plain text separated by the pipe (|) character in 2 columns (e.g., - Terraform & IaC | Cloud Strategy). Make sure these are tailored to the job description.

    2. Format Experience entries cleanly:
       ### Company Name | Location
       **Job Title** | *Month Year - Month Year*
       - Bullet points using PAR format: Action Verb + Strategic Context + Concrete Business Metric/Outcome.
       - Keep bullet points concise (1-2 lines maximum each, maximum 4-5 high-impact bullets per role).

    3. Elevate business-impact metrics (e.g., % efficiency gains, $ cost savings, scale of infrastructure, migration velocity).

    4. Typography & Hyphenation Rule: Do NOT insert spaces before or after hyphens in hyphenated compound words (e.g., write 'AI-enabling', 'large-scale', 'high-performing', 'AWS-native', 'Infrastructure-as-Code', 'self-service', 'first-of-its-kind', NEVER 'AI -enabling' or 'large -scale').

    5. Generate a highly persuasive, 3-paragraph executive cover letter addressing the specific engineering challenges in the job posting.

    Return your response STRICTLY as a valid JSON object matching this exact structure:
    {{
        "full_tailored_resume_text": "string (the complete, fully formatted markdown text of the rewritten resume)",
        "tailored_cover_letter": "string (the complete text of the executive cover letter)"
    }}
    """

    # Local fallback when OpenAI is not enabled or API key missing
    if not client:
        terms = [term for term in [
            "AWS", "Terraform", "Platform Engineering", "Cloud Infrastructure", "FinOps", 
            "AI Platforms", "Security Modernization", "Aurora", "DevOps", "SRE", "Vector DB"
        ] if re.search(r"\b" + re.escape(term) + r"\b", job_description, re.I)]
        
        matched_focus = ", ".join(terms[:5]) or "Cloud Infrastructure & Platform Engineering"
        
        # Parse job title hints from job description text
        target_role = "Assistant Director"

        # Generate dynamic core competencies based on matched terms, padding with standard executive skills
        default_skills = ["Cloud Strategy", "Terraform & IaC", "FinOps Governance", "Vault Security", "Aurora Modernization", "DevOps & SRE Operating Models", "Executive Stakeholder Alignment", "Engineering Org Scaling"]
        
        # Merge matched terms and default skills, removing duplicates
        skills = []
        for term in terms:
            if term not in skills:
                skills.append(term)
        for ds in default_skills:
            if ds not in skills:
                skills.append(ds)
        
        # Build custom tailored header & executive summary for fallback mode
        tailored_header = (
            f"RAN ELIAHU\n"
            f"{target_role} — {matched_focus}\n"
            f"Milwaukee, WI | (414) 943-7570 | linkedin.com/in/raneliahu\n\n"
            f"## EXECUTIVE PROFILE\n"
            f"Transformational engineering executive with 12+ years leading enterprise cloud modernization, AI-enabling platform strategy, "
            f"and large-scale infrastructure transformation. Proven track record building high-performing engineering organizations, "
            f"driving AWS-native platform adoption, operationalizing Infrastructure-as-Code (Terraform), and aligning technical execution "
            f"with executive business outcomes. Tailored target expertise spans {matched_focus}.\n\n"
            f"## CORE COMPETENCIES\n"
            f"- {skills[0]} | {skills[1]}\n"
            f"- {skills[2]} | {skills[3]}\n"
            f"- {skills[4]} | {skills[5]}\n"
            f"- {skills[6]} | {skills[7]}\n\n"
            f"## PROFESSIONAL EXPERIENCE\n"
            f"### Northwestern Mutual | Milwaukee, WI\n"
            f"**Assistant Director — Infrastructure & Cloud Engineering** | *Dec 2023 – Present*\n"
            f"- Architected and delivered a Terraform-driven self-service infrastructure platform, accelerating engineering provisioning velocity by 40% organization-wide.\n"
            f"- Championed enterprise security modernization through a first-of-its-kind HashiCorp Vault + AWS Aurora integration, significantly improving credential governance and audit readiness.\n"
            f"- Directed modernization of automated AWS database lifecycle management pipelines, improving platform availability and deployment consistency across enterprise workloads.\n"
            f"- Partnered with executive FinOps leadership to drive cloud cost governance initiatives, optimizing AWS utilization and delivering measurable infrastructure cost savings.\n"
            f"- Enabled AI-adjacent platform capabilities by modernizing cloud-native data infrastructure supporting analytics, vector databases, and future AI workloads.\n\n"
            f"**Engineering Manager — Infrastructure & Cloud Services** | *Apr 2021 – Dec 2023*\n"
            f"- Defined and executed a multi-year cloud modernization roadmap focused on scalability, automation, resiliency, and operational maturity.\n"
            f"- Led seamless migration of 150+ enterprise database instances from legacy RDS environments to AWS Aurora, improving platform reliability and performance-per-dollar.\n"
            f"- Drove organization-wide adoption of Terraform Infrastructure-as-Code standards and reusable automation modules, eliminating deployment friction.\n"
            f"- Spearheaded adoption of AWS Graviton infrastructure for Aurora workloads, delivering substantial compute efficiency and AWS cost reductions.\n\n"
            f"**Senior Systems Engineer / Product Owner — Data Services** | *Oct 2019 – Apr 2021*\n"
            f"- Introduced self-service provisioning capabilities using Docker, Terraform, and Ansible, accelerating environment delivery timelines.\n"
            f"- Modernized core data infrastructure and automation practices supporting enterprise analytics and future AI platform initiatives.\n\n"
            f"### Marquette University | Milwaukee, WI\n"
            f"**DBA / Business Intelligence Developer** | *Oct 2015 – Sep 2017*\n"
            f"- Designed and delivered enterprise business intelligence solutions using SQL Server, SSIS, and Power BI supporting strategic decision-making.\n"
            f"- Partnered with executive stakeholders to align reporting capabilities with organizational strategy and operational priorities.\n\n"
            f"## TECHNOLOGY & PLATFORM EXPERTISE\n"
            f"- **Cloud & Infrastructure:** AWS (Aurora, RDS, EC2, S3, Lake Formation), Terraform, Docker, Ansible\n"
            f"- **Databases & Data Platforms:** Aurora PostgreSQL, PostgreSQL, MySQL, SQL Server, Pgvector\n"
            f"- **Security & FinOps:** HashiCorp Vault, IAM Governance, Cloud Cost Governance, Audit Compliance\n\n"
            f"## LEADERSHIP IMPACT\n"
            f"- Built and scaled engineering teams focused on accountability, innovation, operational excellence, and psychological safety.\n"
            f"- Recognized as a force multiplier who improves organizational effectiveness through systems thinking, coaching, automation, and platform enablement.\n"
            f"- Strong advocate for AI-first engineering organizations where automation, cloud-native design, and developer experience accelerate business outcomes.\n"
            f"- Drives measurable results through disciplined execution, modern engineering practices, and executive-aligned prioritization.\n"
            f"- Balances strategic innovation with operational rigor, reliability, and long-term platform sustainability.\n\n"
            f"## EDUCATION\n"
            f"### The Academic College of Business Management | Tel Aviv District\n"
            f"**Bachelor of Science in Business Management** | *2008 – 2011*\n"
            f"- Major: Information Technologies | Minor: Finance"
        )

        mocked_cover = (
            "Dear Hiring Team,\n\n"
            f"I am writing to express my enthusiastic interest in this leadership opportunity. My background leading enterprise AWS modernization, "
            f"platform engineering, and cloud infrastructure transformation directly aligns with your strategic priorities around {matched_focus}.\n\n"
            "In my recent executive leadership roles, I built and scaled Terraform-driven self-service developer platforms, architected enterprise-wide security integrations "
            "with HashiCorp Vault, modernized multi-region database fleets to AWS Aurora, and partnered directly with executive FinOps leaders to drive measurable cloud cost efficiency.\n\n"
            "I welcome the opportunity to discuss how my combination of technical architecture depth, organizational leadership, and business-focused execution can accelerate your engineering vision.\n\n"
            "Sincerely,\nRan Eliahu"
        )
        return {
            "full_tailored_resume_text": tailored_header,
            "tailored_cover_letter": mocked_cover
        }


    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You excel at structuring pristine corporate executive resumes and documentation with crisp typography and concise, metric-driven language."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return json.loads(response.choices[0].message.content)

