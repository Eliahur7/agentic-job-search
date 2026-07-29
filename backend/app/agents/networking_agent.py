import os
from openai import OpenAI
import json

api_key = os.environ.get("OPENAI_API_KEY")
enable_openai = os.environ.get("ENABLE_OPENAI", "0") == "1"

if enable_openai and api_key and api_key != "sk-your-api-key-here":
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None
else:
    client = None

def generate_outreach_templates(company_name: str, job_title: str, user_resume_summary: str) -> dict:
    """
    Generates professional, conversion-focused LinkedIn and cold email outreach 
    templates tailored to internal executive stakeholders.
    """
    prompt = f"""
    You are an Elite Executive Talent Agent. Draft highly polished outreach messages for a candidate targeting a high-level leadership role.
    The messaging must sound incredibly professional, emphasizing scale, cloud infrastructure maturity, and transformation without sounding desperate.

    Target Position: {job_title}
    Target Company: {company_name}
    Candidate Background Focus: {user_resume_summary}

    Generate two variants:
    1. A strict 300-character-limit LinkedIn connection note.
    2. A short, impactful cold email to an internal VP or Talent Partner.

    Return your response STRICTLY as a valid JSON object matching this structure:
    {{
        "linkedin_connection_note": "string (under 300 chars)",
        "cold_email_subject": "string",
        "cold_email_body": "string"
    }}
    """

    if not client:
        return {
            "linkedin_connection_note": "Ran - Cloud infrastructure architect passionate about FinOps and scaling enterprise systems. Would love to explore how we can transform your platform architecture.",
            "cold_email_subject": "AWS Infrastructure Leadership Opportunity - Let's Discuss",
            "cold_email_body": "Hi there,\n\nI've been following your company's work in cloud modernization and would love to connect about potential leadership opportunities in your infrastructure team.\n\nLooking forward to the conversation.\n\nBest,\nRan"
        }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a master of executive corporate correspondence."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    
    return json.loads(response.choices[0].message.content)