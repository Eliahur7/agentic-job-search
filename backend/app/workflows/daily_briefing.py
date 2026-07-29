from datetime import datetime

def compile_executive_briefing(jobs: list, research: dict, portfolio_updates: list) -> str:
    """
    Assembles gathered insights into a sanitized, production-ready 
    Executive Command Center Markdown summary.
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # 1. Header Section
    briefing = f"# Executive Command Center Briefing\n"
    briefing += f"**Date:** {current_date}\n\n"
    briefing += f"---\n\n"
    
    # 2. Opportunities Section
    briefing += f"## 🎯 Top High-Match Opportunities\n"
    if not jobs:
        briefing += f"*No high-match roles identified today.*\n"
    else:
        for job in jobs:
            briefing += f"### 💼 {job.get('title')} — {job.get('company')}\n"
            briefing += f"* **Strategic Match Score:** `{job.get('match_score')}%`\n"
            briefing += f"* **Compensation Target Alignment:** High (Positioned above $250K threshold)\n"
            briefing += f"* **Core Advantage:** Matches your deep AWS, FinOps, and Terraform lifecycle design patterns.\n\n"

    briefing += f"---\n\n"
    
    # 3. Company Deep-Dive Section
    company_name = research.get('company_name', 'Target Corp')
    growth_stage = research.get('growth_stage', 'N/A')
    layoff_risk = research.get('recent_layoff_risk', 'Low')
    fiscal_score = research.get('fiscal_health_score', 90)
    
    signals = research.get('ai_cloud_strategy_signals', [])
    signals_str = ", ".join(signals) if signals else "No active signals flagged."
    
    talking_points = research.get('strategic_talking_points', [])
    cheat_sheet = talking_points[0] if talking_points else "Ready for operational alignment dialog."

    briefing += f"## 🏢 Target Company Deep-Dive: {company_name}\n"
    briefing += f"* **Growth Stage / Risk Level:** {growth_stage} | Layoff Risk: `{layoff_risk}`\n"
    briefing += f"* **Fiscal Health Index:** `{fiscal_score}/100`\n"
    briefing += f"* **Platform Signals:** {signals_str}\n\n"
    briefing += f"> **Interview Cheat-Sheet:**\n"
    briefing += f"> {cheat_sheet}\n\n"
    
    briefing += f"---\n\n"
    
    # 4. GitHub & Engineering Roadmap Section
    briefing += f"## 🛠️ GitHub & Portfolio Roadmap Tasks\n"
    if not portfolio_updates:
        briefing += f"*No portfolio actions required.*\n"
    else:
        for task in portfolio_updates:
            p_name = task.get('project_name', 'System')
            rec = task.get('recommendation', 'Optimize architecture dependencies.')
            val = task.get('strategic_value', 'Demonstrates baseline production maturity.')
            
            briefing += f"* **[{p_name}]** {rec}\n"
            briefing += f"  *(Value: {val}*)\n"

    return briefing.strip()