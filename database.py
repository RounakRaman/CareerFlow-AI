import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import difflib

DB_PATH = os.path.join(os.path.dirname(__file__), "job_agent.db")

RESUME_SEED_DATA = [
    {
        "vertical_name": "Consultant",
        "resume_text": """
ROUNAK RAMAN | Consultant & Strategy Specialist
Email: raman.rounak@gmail.com | Phone: +91 88268 79389 | Location: Delhi, India
Education: B.Tech in Information Technology, Netaji Subhas University of Technology (NSUT), CGPA: 8.95 (Dept. Rank 1)

PROFESSIONAL SUMMARY:
Analytical problem solver with 2+ years of experience delivering strategy, analytics, and operational improvements across EdTech, FinTech, and Public Policy. Proven track record of translating complex, ambiguous problems into data-driven recommendations that improved business performance for platforms adopted by 2,000+ users, generating ₹20L+ revenue per cohort. Experienced in market research, financial analysis, competitive benchmarking, business strategy, hypothesis-driven problem solving, stakeholder management, and executive communication.

WORK EXPERIENCE & CONSULTING ENGAGEMENTS:
- Co-Founder, Strategy & Operations Lead | BeyondTech - Early-Stage EdTech Platform (Dec 2024 - Present):
  • Co-led business strategy for an AI-powered EdTech startup; conducted customer discovery, market research, and competitive analysis defining GTM strategy that drove 2,000+ users in month 1.
  • Optimized customer acquisition funnel by analyzing user behavior and stakeholder feedback, managing 1,800+ qualified leads and improving paid conversion to 30% (₹20L+ revenue per cohort).
  • Streamlined operational processes through AI automation, reducing content production costs by 75%.

- Quantitative Analyst | Futures First (Jan 2025 - Present):
  • Built hypothesis-driven analytical frameworks using SQL, Python, and Advanced Excel; evaluated macroeconomic indicators and volatility to support decision-making for a $100K portfolio.
  • Monitored 12+ KPIs, synthesizing complex datasets into executive recommendations that improved trade-selection efficiency by 50%.

- Strategy & Research Associate Intern | Nation with Namo (Jul 2024 - Aug 2024):
  • Conducted quantitative & qualitative research evaluating Delhi-NCR's air pollution ecosystem; performed policy benchmarking, stakeholder mapping, and cost-benefit analysis.
  • Co-authored a 100-page policy report outlining short-, medium-, and long-term implementation strategies for sustainable air quality management.

- Strategic Border Governance Initiative (Seema Setu) | Land Ports Authority of India (LPAI) (Jun 2026):
  • Conducted process mapping and operational analysis across 10+ functional workflows for Integrated Check Posts.
  • Developed strategic implementation framework with 20+ actionable recommendations, improving cross-agency coordination.

SKILLS: Business Strategy, Market Research, Policy Benchmarking, Process Mapping, Cost-Benefit Analysis, Stakeholder Management, SQL, Python, Tableau, Power BI, Advanced Excel.
"""
    },
    {
        "vertical_name": "Data Scientist",
        "resume_text": """
ROUNAK RAMAN | Data Scientist & Machine Learning Engineer
Email: raman.rounak@gmail.com | Phone: +91 88268 79389 | Location: Delhi, India
Education: B.Tech in IT (Minor in AI & Network Security), NSUT Delhi, CGPA: 8.95 (Dept. Rank 1)

PROFESSIONAL SUMMARY:
Machine Learning & Data Scientist with 2+ years of hands-on experience building, validating, and deploying machine learning, deep learning, NLP, and computer vision models across e-commerce, fintech, and quantitative research. Built multi-label image classification achieving 90%+ accuracy on 70,000+ product images, and 35+ statistically validated predictive models improving hit rate by 13% and reducing inference latency by 20%. Proficient in PyTorch, TensorFlow, Scikit-learn, Hugging Face Transformers, LangChain, FAISS, and SQL.

WORK EXPERIENCE & PROJECTS:
- Co-Founder & Data Lead | BeyondTech (Dec 2024 - Present):
  • Built and deployed an LLM-powered learning platform serving 2,000+ users, leveraging Hugging Face Transformers, NLP, RAG, and Python for personalized feedback.
  • Developed scalable Generative AI workflows using LangChain, FAISS vector store, embedding models, and prompt engineering, reducing content production costs by 75%.

- Financial Market Analyst | Futures First (Jan 2025 - Present):
  • Developed 35+ predictive machine learning models using Python and Scikit-learn across 300+ hypotheses.
  • Built predictive models leveraging time-series forecasting (ARIMAX/SARIMAX), macroeconomic indicators, and market microstructure data.

- Meesho QuickTag | Computer Vision & Deep Learning (Aug 2025):
  • Developed multi-label computer vision model using PyTorch, Hugging Face Transformers, and Phi-3.5 Vision on 70,000+ product images achieving 90%+ accuracy.
  • Built real-time Streamlit inference platform reducing manual product tagging effort by 80%.

- CrediScope AI | Credit Risk Analytics & Loan Default Prediction (May 2026):
  • Built explainable ML classification workflow (Scikit-learn, XGBoost, Random Forest) on 32,500+ financial records optimizing ROC-AUC, Precision, Recall, and F1-score.

SKILLS: Python, SQL, PyTorch, TensorFlow, Scikit-learn, XGBoost, Hugging Face, LangChain, FAISS, RAG, Computer Vision, Time Series (ARIMAX), Streamlit, Docker.
"""
    },
    {
        "vertical_name": "Data Analyst",
        "resume_text": """
ROUNAK RAMAN | Data & Business Analytics Specialist
Email: raman.rounak@gmail.com | Phone: +91 88268 79389 | Location: Delhi, India
Education: B.Tech in IT, NSUT Delhi, CGPA: 8.95 (Dept. Rank 1)

PROFESSIONAL SUMMARY:
Data & Analytics professional with 2+ years of combined experience delivering end-to-end analytics, data engineering, and business intelligence solutions. Proficient in Python, SQL, Power BI, Tableau, Excel, PostgreSQL, Streamlit, ETL pipelines, data modeling, dashboard development, and KPI reporting. Built and deployed 6+ production-grade data products including a natural language-to-SQL analytics engine and real-time dashboards tracking 48 companies.

WORK EXPERIENCE & PROJECTS:
- Co-Founder & Data Lead | BeyondTech (Dec 2024 - Present):
  • Built & launched Python-Streamlit platform in 8 weeks, acquiring 2,000+ users.
  • Designed CRM and lead analytics workflow managing 1,800+ qualified leads per cohort, achieving 30% paid conversion and tracking main KPIs.

- Financial Market Analyst | Futures First (Jan 2025 - Present):
  • Tracked 12+ trading KPIs including VWAP, volume, liquidity, and LTQ using Python, SQL, and Advanced Excel, improving trade-selection efficiency by 50%.

- Summer Associate & Data Analyst | Nation with Namo (Jun 2024 - Aug 2024):
  • Analyzed historical PM2.5, PM10, and AQI datasets and built interactive Tableau dashboard covering six pollution sources, reducing manual processing by 60%.
  • Translated stakeholder requirements from 15+ government & industry representatives into analytical specifications.

- Mudrex Events Analytics Engine (Jun 2026):
  • Engineered SQL ETL pipeline (CTEs) standardizing 17 event types into 6 categories, reducing preprocessing time by ~80%.
  • Built AI-powered NL-to-SQL BI engine converting natural language into optimized SQL queries (<30s analysis time).

- JobScout | Job-Market Intelligence Dashboard (May 2026):
  • Designed automated Power BI / Tableau dashboards integrating Google Sheets API with data validation & deduplication, accelerating hiring insights by 95%.

SKILLS: Python, SQL (PostgreSQL, SQLite), Power BI, Tableau, Advanced Excel, ETL Pipelines, Data Modeling, Streamlit, Plotly, Jira, Agile, KPI Reporting.
"""
    },
    {
        "vertical_name": "Financial Analyst",
        "resume_text": """
ROUNAK RAMAN | Financial Analyst & Quantitative Finance Specialist
Email: raman.rounak@gmail.com | Phone: +91 88268 79389 | Location: Delhi, India
Certifications: NISM Series XA Investment Adviser, NISM Series VA Mutual Fund, NISM Series VIII Equity Derivatives, NISM Series XV Research Analyst, AMFI MFD.
Education: B.Tech in IT, NSUT Delhi, CGPA: 8.95 (Dept. Rank 1)

PROFESSIONAL SUMMARY:
Financial markets and quantitative research professional experienced in U.S. fixed income, STIR derivatives, SOFR/Fed Funds futures, yield curves, repo liquidity, central-bank policy, and live portfolio risk/P&L management on a US$500K portfolio (generating US$50K+ gross P&L). Skilled in financial modeling, DCF valuation, credit & bond analysis, YTM, backtesting, stress testing, macroeconomic forecasting, Python, SQL, Bloomberg Terminal, and Power BI.

WORK EXPERIENCE & PROJECTS:
- Financial Market Analyst | Futures First (Jan 2025 - Present):
  • Own SR3/SR1 and SR3/ZQ strategies with full market-risk and P&L responsibility for a US$100K portfolio; generated US$50K+ gross P&L via basis, curve, and butterfly strategies.
  • Built 8+ settlement-accurate backtests using Python, Excel, and Bloomberg incorporating transaction costs, slippage, and roll mechanics.
  • Analyzed FOMC, CPI, NFP, repo liquidity, Treasury swap spreads, and G-SIB funding scenarios.

- Financial Research Consultant | NITI Aayog, Govt of India (Nov 2025 - Jan 2026):
  • Evaluated startups and 15+ funding frameworks through business-model, market, unit-economics, and financial statement analysis; built DCF valuation and scenario models using forecast free cash flows, WACC, and terminal value.

- Rupicast | USD/INR Macro Intelligence & Risk Analytics Dashboard (Jun 2026):
  • Built Python-Streamlit FX analytics platform processing 10 years of daily USD/INR data; integrated 7 macroeconomic drivers (inflation, Fed/RBI policy rates, crude oil) via Yahoo Finance & FRED APIs.
  • Developed monthly ARIMAX/SARIMAX time-series forecasts with 3-12 month horizons.

- AlphaLens | Quantitative Factor Strategy Engine (Jun 2026):
  • Built quantitative factor strategy on S&P 500 combining Value, Momentum, Quality, and Low-Volatility factors, achieving 3.32% annualized alpha and 0.327 Sharpe.

SKILLS: Financial Modeling, DCF Valuation, Portfolio Risk & P&L, Fixed Income & Derivatives, SOFR/Fed Funds, Time-Series ARIMAX, Bloomberg Terminal, Python, SQL, Advanced Excel.
"""
    },
    {
        "vertical_name": "Government Roles",
        "resume_text": """
ROUNAK RAMAN | Public Policy, GovTech & Government Strategy Specialist
Email: raman.rounak@gmail.com | Phone: +91 88268 79389 | Location: Delhi, India
Education: B.Tech in IT, NSUT Delhi, CGPA: 8.95 (Dept. Rank 1)

PROFESSIONAL SUMMARY:
Public Policy, Digital Public Infrastructure (DPI), and GovTech specialist with experience working alongside apex government think-tanks (NITI Aayog) and statutory bodies (Land Ports Authority of India). Proven background in synthesizing policy frameworks, analyzing national-level ecosystems, conducting stakeholder mapping, and building open financial & governance infrastructure.

WORK EXPERIENCE & ENGAGEMENTS:
- Financial Research Consultant | NITI Aayog, Government of India (Nov 2025 - Jan 2026):
  • Conducted comparative analysis of India's innovation & startup ecosystem across 15+ policy frameworks, evaluating funding mechanisms, academic participation, and startup outcomes.
  • Supported Atal New India Challenge (ANIC) by sorting & structuring 500+ records to improve government disbursement tracking efficiency.
  • Authored analytical policy reports mapping funding mechanisms and academic-industry collaboration gaps for senior government stakeholders.

- Strategy & Research Associate Intern | Nation with Namo (Jul 2024 - Aug 2024):
  • Evaluated Delhi-NCR's air pollution ecosystem across six major emission sources; performed policy benchmarking and cost-benefit analysis.
  • Co-authored 100-page policy report outlining implementation roadmaps for sustainable urban air quality management.

- Strategic Border Governance Initiative (Seema Setu) | Land Ports Authority of India (LPAI, MHA) (Jun 2026):
  • Conducted process mapping and operational analysis across 10+ functional workflows at Integrated Check Posts (ICPs).
  • Evaluated 15+ international border management frameworks to support evidence-based modernization recommendations.

- Founding Office President | Code 4 GovTech Office NSUT x Samagra (Feb 2024 - Jun 2025):
  • Established NSUT's first GovTech office, recruiting 50+ contributors for Digital Public Goods (DPG) and DPI development on SamagraX and ONDC.

SKILLS: Public Policy Analysis, Digital Public Infrastructure (DPI), GovTech, Stakeholder Engagement, Policy Benchmarking, Institutional Coordination, Data Synthesis, Executive Reporting.
"""
    },
    {
        "vertical_name": "Research",
        "resume_text": """
ROUNAK RAMAN | Quantitative & Applied Academic Researcher
Email: raman.rounak@gmail.com | Phone: +91 88268 79389 | Location: Delhi, India
Publications: Elsevier Internet of Things (SCIE Q1, IF: 6.0), IJAHUC (Scopus, IF: 1.8), Springer ICAIA, Springer Cluster Computing (SCIE Q1, IF: 4.1).
Education: B.Tech in IT (Minor in AI & Network Security), NSUT Delhi, CGPA: 8.95 (Dept. Rank 1)

PROFESSIONAL SUMMARY:
Quantitative researcher and published computer science author with experience in systematic alpha research, statistical signal processing, Wireless Sensor Networks (WSN), IoT security, and machine learning. Ranked 1st at NSUT, 8th in India, and 56th globally on WorldQuant Brain leaderboard across 80+ countries.

RESEARCH EXPERIENCE & PUBLICATIONS:
- Quantitative Researcher | WorldQuant BRAIN (Nov 2023 - May 2024):
  • Conducted alpha research across equities & futures, testing 300+ hypotheses on price-volume, fundamental, and alternative datasets.
  • Developed 35+ validated alpha signals using feature engineering, parameter tuning, neutralization, and out-of-sample stability testing.
  • Improved signal hit rate by 13% and reduced signal response latency by 20%.

- Published Academic Papers:
  1. CONTEXT-NET: Context-Aware Nexus-Based Aggregation Protocol for Opportunistic Networks — Elsevier Internet of Things (2025), SCIE, Scopus Q1 | IF: 6.0.
  2. HKRISRP: Hierarchical Key Rotation & Sensor-Based Resilient Protocol — IJAHUC, Inderscience (2025), Scopus | IF: 1.8.
  3. ARMor-IoT: Aggregated Reliable Mechanism for Optimized Trust in IoT — Springer Nature (2025), Scopus.
  4. EESCM: Energy-Efficient Cluster Management in IoT Networks — Springer Nature Cluster Computing (2025), SCIE Q1 | IF: 4.1.

- Project: AlphaLens Factor Engine (Jun 2026):
  • Engineered 3-layer quantitative risk framework (Z-score clipping, EWMA volatility targeting, RSI regime neutralization) on S&P 500 data.

SKILLS: Statistical Hypothesis Testing, Signal Processing, Quantitative Backtesting, Peer-Reviewed Scientific Writing, Python, PyTorch, Mathematical Modeling, Latex, Algorithm Design.
"""
    },
    {
        "vertical_name": "APM/Product Analyst",
        "resume_text": """
ROUNAK RAMAN | Associate Product Manager (APM) & Product Analyst
Email: raman.rounak@gmail.com | Phone: +91 88268 79389 | Location: Delhi, India
Education: B.Tech in IT, NSUT Delhi, CGPA: 8.95 (Dept. Rank 1)

PROFESSIONAL SUMMARY:
Product Analyst and APM candidate with experience leading product strategy, user discovery, conversion funnel optimization, and automated workflows for tech platforms. Track record of growing early-stage EdTech platform from zero to 2,000+ active users with 30% paid conversion. Skilled in wireframing, PRD writing, user interview synthesis, SQL, product analytics, and A/B feature tracking.

WORK EXPERIENCE & PROJECTS:
- Co-Founder, Strategy & Product Lead | BeyondTech (Dec 2024 - Present):
  • Built & launched Python-Streamlit EdTech platform within 8 weeks, onboarding 2,000+ active students across NSUT & DTU.
  • Designed and optimized customer acquisition funnel by analyzing user behavior and feedback, managing 1,800+ leads and achieving 30% conversion (₹20L+ revenue per cohort).
  • Led cross-functional execution across engineering, academic, and business teams; automated feedback pipelines using NLP/LLMs to lower production costs by 75%.

- JobScout | Product & Hiring Intelligence Platform (May 2026):
  • Gathered stakeholder requirements and translated them into functional specs (PRD), KPIs, and wireframes for a job market dashboard tracking 48 companies.
  • Automated alert workflows and stakeholder reporting, reducing manual monitoring effort by 95%.

- Mudrex Events Analytics Engine (Jun 2026):
  • Built self-service analytics interface for non-technical business users, handling 100+ daily business queries with automated NL-to-SQL translation.

- Vice-President | Nakshatra NSUT (Jul 2023 - Jul 2024):
  • Primary organizer for flagship events, coordinating 150+ team members, securing 10+ corporate sponsorships (GAIL, Boat), and driving 1,000+ event registrations.

SKILLS: Product Strategy, PRD Authoring, Funnel Optimization, User Research, Wireframing, SQL Analytics, A/B Testing, User Metrics (CAC, LTV, Retention, Conversion), Agile/Jira.
"""
    }
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. applications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        role_title TEXT NOT NULL,
        vertical_used TEXT NOT NULL,
        recipient_email TEXT,
        job_post_raw TEXT,
        ats_score INTEGER,
        date_sent DATETIME,
        status TEXT DEFAULT 'sent', -- 'sent', 'replied', 'no_response', 'follow_up_sent'
        follow_up_sent_date DATETIME,
        email_thread_id TEXT,
        linkedin_dm_generated BOOLEAN DEFAULT 0,
        subject_line_variant TEXT, -- 'A' or 'B'
        subject_line_text TEXT,
        notes TEXT
    );
    """)

    # 2. resume_verticals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resume_verticals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vertical_name TEXT UNIQUE NOT NULL,
        resume_file_path TEXT,
        resume_text TEXT NOT NULL,
        last_updated DATETIME
    );
    """)

    # 3. scoring_log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scoring_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER,
        vertical_id INTEGER,
        ats_score INTEGER,
        keyword_match_pct REAL,
        requirement_coverage_pct REAL,
        format_score REAL,
        gap_summary TEXT,
        FOREIGN KEY (application_id) REFERENCES applications (id),
        FOREIGN KEY (vertical_id) REFERENCES resume_verticals (id)
    );
    """)

    # 4. observability_log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS observability_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER,
        agent_step TEXT NOT NULL,
        model_used TEXT NOT NULL,
        tokens_used INTEGER DEFAULT 0,
        latency_ms INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        details TEXT
    );
    """)

    conn.commit()

    # Seed 7 resume verticals if empty
    cursor.execute("SELECT COUNT(*) as count FROM resume_verticals;")
    if cursor.fetchone()["count"] == 0:
        now = datetime.now().isoformat()
        for seed in RESUME_SEED_DATA:
            cursor.execute("""
            INSERT INTO resume_verticals (vertical_name, resume_text, last_updated)
            VALUES (?, ?, ?);
            """, (seed["vertical_name"], seed["resume_text"], now))
        conn.commit()

    conn.close()

def check_duplicate_application(company: str, role_title: str, threshold: float = 0.75) -> Optional[Dict[str, Any]]:
    """Fuzzy checks if application to same company and role already exists."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, company, role_title, date_sent, status, vertical_used FROM applications;")
    rows = cursor.fetchall()
    conn.close()

    target_str = f"{company.lower().strip()} {role_title.lower().strip()}"
    
    for row in rows:
        existing_str = f"{row['company'].lower().strip()} {row['role_title'].lower().strip()}"
        ratio = difflib.SequenceMatcher(None, target_str, existing_str).ratio()
        if ratio >= threshold:
            return {
                "id": row["id"],
                "company": row["company"],
                "role_title": row["role_title"],
                "date_sent": row["date_sent"],
                "status": row["status"],
                "vertical_used": row["vertical_used"],
                "similarity_score": round(ratio, 2)
            }
    return None

def save_application(app_data: Dict[str, Any]) -> int:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO applications (
        company, role_title, vertical_used, recipient_email, job_post_raw,
        ats_score, date_sent, status, email_thread_id, linkedin_dm_generated,
        subject_line_variant, subject_line_text, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        app_data.get("company", "Unknown"),
        app_data.get("role_title", "Unknown"),
        app_data.get("vertical_used", "General"),
        app_data.get("recipient_email", ""),
        app_data.get("job_post_raw", ""),
        app_data.get("ats_score", 0),
        now,
        app_data.get("status", "sent"),
        app_data.get("email_thread_id", f"thread_{int(datetime.now().timestamp())}"),
        app_data.get("linkedin_dm_generated", True),
        app_data.get("subject_line_variant", "A"),
        app_data.get("subject_line_text", ""),
        app_data.get("notes", "")
    ))
    app_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return app_id

def log_scoring(application_id: Optional[int], vertical_id: int, ats_score: int,
                kw_pct: float, req_pct: float, fmt_score: float, gap_summary: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO scoring_log (application_id, vertical_id, ats_score, keyword_match_pct, requirement_coverage_pct, format_score, gap_summary)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (application_id, vertical_id, ats_score, kw_pct, req_pct, fmt_score, gap_summary))
    conn.commit()
    conn.close()

def get_all_resumes() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, vertical_name, resume_text, last_updated FROM resume_verticals ORDER BY id ASC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def update_resume(vertical_name: str, new_text: str):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
    UPDATE resume_verticals SET resume_text = ?, last_updated = ? WHERE vertical_name = ?;
    """, (new_text, now, vertical_name))
    conn.commit()
    conn.close()

def get_applications() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications ORDER BY id DESC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Compute days_since_sent dynamically
    for row in rows:
        if row.get("date_sent"):
            try:
                sent_dt = datetime.fromisoformat(row["date_sent"])
                row["days_since_sent"] = (datetime.now() - sent_dt).days
            except Exception:
                row["days_since_sent"] = 0
        else:
            row["days_since_sent"] = 0
    return rows

def get_ab_subject_analytics() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        subject_line_variant,
        COUNT(*) as total_sent,
        SUM(CASE WHEN status = 'replied' THEN 1 ELSE 0 END) as total_replied
    FROM applications
    WHERE subject_line_variant IS NOT NULL
    GROUP BY subject_line_variant;
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Database initialized and 7 vertical resumes seeded successfully.")
