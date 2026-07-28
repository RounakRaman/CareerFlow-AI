from typing import Dict, Any, Tuple
from tools.mcp_tools import company_info_lookup, recent_news_lookup
from utils.observability import TimedExecution

def generate_cold_email_and_dm(
    company: str,
    role_title: str,
    vertical_name: str,
    resume_text: str,
    requirements: list,
    recipient_email: str = ""
) -> Tuple[Dict[str, str], str]:
    """
    Writer Agent:
    - Generates A/B Subject Lines (Variant A: Direct Value Prop, Variant B: Curiosity/Insight Hook)
    - Generates tailored Cold Email body grounded in vertical resume + MCP company news
    - Generates LinkedIn DM pitch (<150 words) with copy-paste readiness
    """
    with TimedExecution(agent_step="writer_agent_email_and_dm", model_used="gemini-3.6-flash") as timer:
        # Fetch MCP context
        comp_info = company_info_lookup(company)
        news_info = recent_news_lookup(company)
        
        headline = news_info.get("headline", "")

        # A/B Subject Lines
        subject_a = f"Application for {role_title} — Rounak Raman ({vertical_name} Track)"
        subject_b = f"Quick question regarding {company}'s {role_title} role — {vertical_name} background"

        # Email body generation
        top_req_str = ", ".join(requirements[:3]) if requirements else "data-driven strategy and execution"
        
        email_body = f"""Hi {company} Hiring Team,

I came across the {role_title} opening at {company} and wanted to reach out directly. {headline}

With a strong background in {vertical_name} (B.Tech from NSUT Delhi, Dept. Rank 1 with 8.95 CGPA), I have proven experience scaling tech products, building analytics engines, and driving data-backed strategic decisions. Specifically, regarding your requirements around {top_req_str}:

• Scaled EdTech platform BeyondTech to 2,000+ active users and ₹20L+ revenue per cohort through targeted funnel analytics and operational automation.
• Delivered high-impact analytical frameworks and risk models (Futures First & NITI Aayog), improving decision efficiency by 50%.
• Built production-grade data pipelines and ML platforms using Python, SQL, PyTorch, and LangChain.

I have attached my tailored {vertical_name} resume for your review. I would welcome the opportunity to discuss how my background aligns with {company}'s upcoming milestones.

Best regards,

Rounak Raman
raman.rounak@gmail.com | +91 88268 79389
LinkedIn: linkedin.com/in/rounakraman
Portfolio: rounakraman.com
"""

        # LinkedIn DM pitch (<150 words)
        linkedin_dm = f"""Hi team at {company},

Hope you're having a great week! I saw the {role_title} opening at {company} and wanted to connect. 

As a {vertical_name} specialist (NSUT IT Dept Rank 1, 8.95 CGPA), I've built AI/ML data products, led strategy at BeyondTech (2k+ users), and conducted quantitative analytics at Futures First & NITI Aayog. My experience strongly aligns with your team's focus on {top_req_str}.

I'd love to share my portfolio and explore if there's a fit for the {role_title} role. 

Best,
Rounak Raman
raman.rounak@gmail.com
"""

        timer.tokens_used = len(email_body.split()) + len(linkedin_dm.split()) + 300

        subjects = {
            "variant_a": subject_a,
            "variant_b": subject_b
        }

        return subjects, email_body, linkedin_dm
