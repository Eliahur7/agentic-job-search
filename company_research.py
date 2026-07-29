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

def research_company_profile(company_name: str, industry_context: str = "") -> dict:
    """
    Analyzes fiscal risk, leadership shifts, recent funding/layoffs, 
    and AI/Cloud tech stack investment signals.
    """
    # Use mock data for local testing
    if not client:
        return {
            "growth_stage": "Series D / Growth",
            "engineering_maturity": "High - Sophisticated DevOps infrastructure with multi-region deployments",
            "fiscal_health_score": 85.5,
            "recent_layoff_risk": "Low",
            "ai_cloud_strategy_signals": [
                "Expanding Kubernetes and serverless investments",
                "Building proprietary ML observability platform",
                "Hiring 50+ ML engineers in 2025"
            ],
            "strategic_talking_points": [
                "Recently migrated 90% workloads to multi-region Kubernetes",
                "Invested $200M in cloud infrastructure modernization",
                "Looking for VP-level platform architects to lead distributed systems"
            ]
        }
    
    # In a full runtime, you'd prepend a web-search tool output here
    mock_search_results = f"Recent news for {company_name}: Expanding cloud infrastructure, hiring platform leaders, strong Q1 growth, no recent layoffs reported."

    prompt = f"""
    You are an Executive Corporate Intelligence Analyst. Analyze the following target company for a candidate interviewing for a top-tier Engineering Leadership role.
    
    Company Name: {company_name}
    Context/Search Data: {mock_search_results}

    Provide a precise strategic breakdown. Return your response STRICTLY as a valid JSON object:
    {{
        "growth_stage": "e.g., Series C / Public / Enterprise",
        "engineering_maturity": "High/Medium/Low with brief reasoning",
        "fiscal_health_score": float (0.0 to 100.0),
        "recent_layoff_risk": "Low/Medium/High",
        "ai_cloud_strategy_signals": ["signal 1", "signal 2"],
        "strategic_talking_points": ["2-3 highly tailored, metric-driven talking points for an interview"]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a corporate due-diligence data extraction engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    return json.loads(response.choices[0].message.content)