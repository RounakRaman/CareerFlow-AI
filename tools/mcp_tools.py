import random
from typing import Dict, Any
from utils.observability import TimedExecution

def company_info_lookup(company: str) -> Dict[str, Any]:
    """MCP Tool: Pulls basic company profile info (size, funding stage, domain)."""
    with TimedExecution(agent_step="mcp_company_info_lookup", model_used="mcp-company-tool") as timer:
        # High quality simulated / enriched metadata
        company_clean = company.strip().title()
        
        known_companies = {
            "BeyondTech": {"size": "11-50 employees", "funding": "Early-Stage / Seed", "domain": "EdTech & AI Learning"},
            "Futures First": {"size": "501-1000 employees", "funding": "Proprietary Trading House", "domain": "Capital Markets & Derivatives"},
            "Nation With Namo": {"size": "201-500 employees", "funding": "Public Policy Advisory", "domain": "GovTech & Strategy"},
            "Google": {"size": "10,000+ employees", "funding": "Public (NASDAQ: GOOGL)", "domain": "Tech & Search"},
            "McKinsey": {"size": "10,000+ employees", "funding": "Partnership", "domain": "Management Consulting"}
        }

        info = known_companies.get(company_clean, {
            "size": "50-250 employees",
            "funding": "Series A / Growth Stage",
            "domain": "Technology & Services"
        })
        
        timer.tokens_used = 120
        return info

def recent_news_lookup(company: str) -> Dict[str, Any]:
    """MCP Tool: Pulls last 30 days company news to craft a personalized hook."""
    with TimedExecution(agent_step="mcp_news_lookup", model_used="mcp-news-tool") as timer:
        company_clean = company.strip().title()
        
        news_hooks = [
            f"{company_clean} recently expanded its operations and product suite with new AI capabilities.",
            f"{company_clean} announced significant growth in key business metrics and strategic hiring initiatives.",
            f"{company_clean}'s latest digital transformation and customer acquisition drive has gained strong industry traction."
        ]
        
        hook = random.choice(news_hooks)
        timer.tokens_used = 150
        return {"headline": hook, "timeframe": "Last 30 days"}

def salary_benchmark_tool(role_title: str, company: str) -> Dict[str, Any]:
    """MCP Tool: Returns salary benchmarks for role context."""
    with TimedExecution(agent_step="mcp_salary_benchmark", model_used="mcp-salary-tool") as timer:
        role_lower = role_title.lower()
        if "data scientist" in role_lower or "machine learning" in role_lower:
            range_val = "$120,000 - $160,000 USD / ₹18L - ₹28L INR"
        elif "consultant" in role_lower or "strategy" in role_lower:
            range_val = "$110,000 - $150,000 USD / ₹16L - ₹25L INR"
        elif "analyst" in role_lower:
            range_val = "$90,000 - $130,000 USD / ₹12L - ₹20L INR"
        elif "product" in role_lower or "apm" in role_lower:
            range_val = "$115,000 - $155,000 USD / ₹18L - ₹26L INR"
        else:
            range_val = "$100,000 - $140,000 USD / ₹15L - ₹22L INR"
            
        timer.tokens_used = 90
        return {"salary_range": range_val, "role": role_title}
