import os
import json
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")
enable_openai = os.environ.get("ENABLE_OPENAI", "0") == "1"

if enable_openai and api_key and api_key != "sk-your-api-key-here":
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None
else:
    client = None

def analyze_portfolio_opportunities(existing_projects: list) -> list:
    """
    Evaluates current developer footprints and flags areas to inject high-leverage 
    architectural patterns (like multi-region Terraform modules or custom LLM evaluation setups).
    """
    # Use mock data for local testing
    if not client:
        return [
            {
                "project_name": "Streamlit Market Indicators Application",
                "recommendation": "Implement distributed caching layer with Redis for real-time market data aggregation across 5+ data sources, supporting 10k+ concurrent users",
                "strategic_value": "Demonstrates scalability at enterprise level; shows expertise in real-time systems and distributed architecture"
            },
            {
                "project_name": "AWS Cost Optimization Engine",
                "recommendation": "Build custom ML pipeline using SageMaker to predict and optimize reserved capacity utilization, reducing costs by 30-40%",
                "strategic_value": "Shows deep AWS expertise, ML integration, and measurable business impact that resonates with VPs/CTOs"
            }
        ]
    
    prompt = f"""
    You are a Principal Platform Architect and Technical Advisor. Review these current project focuses and recommend elite enhancements that demonstrate high-scale engineering competency.

    Current Projects/Interests: {existing_projects}

    Provide exactly 2 highly impactful, production-grade project features or roadmap items.
    Return a clean JSON list of objects:
    [
        {{
            "project_name": "Target project name",
            "recommendation": "Concrete, explicit architectural feature to implement",
            "strategic_value": "Why this stands out to a VP/CTO hiring manager"
        }}
    ]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return json.loads(response.choices[0].message.content).get("recommendation", [])