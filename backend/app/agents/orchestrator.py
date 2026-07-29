from app.agents.job_hunter import analyze_and_score_job
from app.agents.resume_optimizer import generate_tailored_assets

def job_hunter_node(state: AgentState) -> Dict[str, Any]:
    print("[Job Hunter Node] Scoring new pipeline opportunities...")
    
    # 1. Extract context from persistent app state
    raw_resume = state["user_profile"].get("raw_resume_text", "")
    # In a full run, this loop iterates over ingested HTML/API text from web scrapers
    raw_scraped_job = "Senior Director of Platform Engineering needed to scale global core AWS landing zones and drive FinOps cost efficiency."
    
    # 2. Execute LLM Evaluation logic
    evaluation = analyze_and_score_job(raw_scraped_job, raw_resume)
    
    job_record = {
        "title": "Senior Director of Platform Engineering",
        "company": "Enterprise Scale Corp",
        "match_score": evaluation["match_score"],
        "analysis": evaluation
    }
    
    return {
        "found_jobs": [job_record],
        "next_step": "resume_optimizer",
        "logs": [f"Processed 'Enterprise Scale Corp' with a match score of {evaluation['match_score']}%."]
    }

def resume_optimizer_node(state: AgentState) -> Dict[str, Any]:
    print("[Resume Optimizer Node] Re-writing professional bullets for target application alignment...")
    
    raw_resume = state["user_profile"].get("raw_resume_text", "")
    target_job = state["found_jobs"][0]["analysis"] # Targeting the highest match scored in prior node
    
    optimization_results = generate_tailored_assets(raw_resume, str(target_job))
    
    return {
        "optimized_resume": optimization_results,
        "next_step": END,
        "logs": ["Successfully processed automated resume variants and tailored cover letter assets."]
    }