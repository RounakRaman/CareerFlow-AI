import re
from typing import Dict, Any, List
from utils.observability import TimedExecution

SCAM_KEYWORDS = [
    "pay for training", "wire money", "telegram only", "whatsapp only",
    "deposit check", "buy equipment", "crypto payment", "unpaid 6 months probation",
    "send fee", "registration fee", "no experience $100/hr"
]

SUSPICIOUS_DOMAINS = ["@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com", "@protonmail.com"]

def parse_job_post(job_text: str) -> Dict[str, Any]:
    """
    Parser Agent: Extracts company, role_title, requirements, and recipient_email
    and performs a security & guardrails check against scam patterns.
    """
    with TimedExecution(agent_step="parse_jd_and_guardrails", model_used="gemini-3.6-flash") as timer:
        # Extract email
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', job_text)
        recipient_email = email_match.group(0) if email_match else ""

        # Guardrail check
        scam_flags = []
        lowered_text = job_text.lower()
        for kw in SCAM_KEYWORDS:
            if kw in lowered_text:
                scam_flags.append(f"Contains suspicious phrase: '{kw}'")

        if recipient_email:
            for domain in SUSPICIOUS_DOMAINS:
                if recipient_email.lower().endswith(domain):
                    scam_flags.append(f"Non-corporate / generic email domain used: {recipient_email}")

        # Simple extraction heuristics (fallback LLM structured extraction prompt can be integrated)
        lines = [line.strip() for line in job_text.split('\n') if line.strip()]
        
        # Heuristic role extraction
        role_title = "Unknown Role"
        company_name = "Unknown Company"
        
        for line in lines[:5]:
            if "role:" in line.lower() or "position:" in line.lower() or "hiring:" in line.lower():
                role_title = line.split(":", 1)[-1].strip()
            elif "company:" in line.lower() or "at " in line.lower():
                company_name = line.split(":", 1)[-1].strip() if ":" in line else line.replace("at ", "").strip()

        if role_title == "Unknown Role" and len(lines) > 0:
            role_title = lines[0][:50]
        if company_name == "Unknown Company" and len(lines) > 1:
            company_name = lines[1][:40]

        # Extract requirements/skills
        req_lines = []
        in_reqs = False
        for line in lines:
            if any(h in line.lower() for h in ["requirement", "qualification", "skills", "looking for", "responsibilities"]):
                in_reqs = True
                continue
            if in_reqs:
                if line.startswith("-") or line.startswith("•") or line.startswith("*") or re.match(r'^\d+\.', line):
                    req_lines.append(re.sub(r'^[-•*\d.]+\s*', '', line))

        if not req_lines:
            # Fallback split
            req_lines = [line for line in lines if len(line) > 15][:6]

        timer.tokens_used = len(job_text.split()) * 2

        return {
            "company": company_name,
            "role_title": role_title,
            "recipient_email": recipient_email,
            "requirements": req_lines,
            "raw_text": job_text,
            "guardrail_status": "FLAGGED" if scam_flags else "PASSED",
            "scam_warnings": scam_flags
        }
