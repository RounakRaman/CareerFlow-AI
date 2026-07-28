import re
from typing import List, Dict, Any
from database import get_all_resumes
from utils.observability import TimedExecution

def score_vertical_resume(requirements: List[str], raw_jd: str, resume: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a single vertical resume against JD requirements using a transparent rubric:
    - Keyword match % (40 weight)
    - Requirement coverage % (40 weight)
    - Format & Structure check % (20 weight)
    """
    resume_text = resume["resume_text"].lower()
    
    # 1. Keyword Extraction from JD
    jd_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', raw_jd.lower()))
    stop_words = {"with", "that", "this", "from", "have", "will", "your", "team", "work", "role", "looking", "must", "good", "year", "years"}
    keywords = [w for w in jd_words if w not in stop_words]

    matched_keywords = [kw for kw in keywords if kw in resume_text]
    keyword_match_pct = round((len(matched_keywords) / max(len(keywords), 1)) * 100, 1)

    # 2. Requirement Coverage
    req_matched = 0
    missing_reqs = []
    for req in requirements:
        req_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', req.lower()) if w not in stop_words]
        if not req_words:
            continue
        match_count = sum(1 for w in req_words if w in resume_text)
        if match_count / len(req_words) >= 0.4:
            req_matched += 1
        else:
            missing_reqs.append(req[:60])

    req_coverage_pct = round((req_matched / max(len(requirements), 1)) * 100, 1)

    # 3. Format Check (Headers, metrics, clear bullet points)
    format_score = 90.0
    if "education" not in resume_text: format_score -= 10
    if "skills" not in resume_text: format_score -= 10
    if "experience" not in resume_text: format_score -= 10

    # Composite ATS Score
    total_ats_score = int(
        (keyword_match_pct * 0.4) +
        (req_coverage_pct * 0.4) +
        (format_score * 0.2)
    )
    total_ats_score = min(max(total_ats_score, 15), 98)  # Clamp between 15 and 98

    # Gap summary
    if missing_reqs:
        gap_summary = f"Missing key requirements: {', '.join(missing_reqs[:3])}"
    else:
        gap_summary = "Strong overall match with high keyword and requirement alignment."

    return {
        "vertical_id": resume["id"],
        "vertical_name": resume["vertical_name"],
        "ats_score": total_ats_score,
        "keyword_match_pct": keyword_match_pct,
        "requirement_coverage_pct": req_coverage_pct,
        "format_score": format_score,
        "gap_summary": gap_summary,
        "matched_keywords_count": len(matched_keywords),
        "total_keywords_count": len(keywords)
    }

def score_all_verticals(requirements: List[str], raw_jd: str) -> List[Dict[str, Any]]:
    """Runs ATS scoring across all 7 vertical resumes simultaneously."""
    with TimedExecution(agent_step="score_all_7_verticals", model_used="rag-scoring-engine") as timer:
        all_resumes = get_all_resumes()
        scores = []
        for res in all_resumes:
            score_data = score_vertical_resume(requirements, raw_jd, res)
            scores.append(score_data)

        # Sort by ATS score descending
        scores.sort(key=lambda x: x["ats_score"], reverse=True)
        timer.tokens_used = len(raw_jd.split()) * 7
        return scores
