# ⚡ AI Job Application Agent

A multi-agent, RAG-powered job application system built with **LangChain**, **Streamlit**, **SQLite**, and **Gmail API**.

The application automatically parses job posts, extracts requirements & recipient contact details, flags suspicious scam listings via security guardrails, runs ATS scoring across **7 specialized resume verticals**, fetches company context via MCP tools, generates personalized cold emails with A/B subject line variants, formats copy-ready LinkedIn DMs, and logs applications to a standalone analytics dashboard.

---

## 🌟 Key Features

1. **7-Vertical RAG Resume Scoring Engine**: Benchmarks job requirements against 7 vertical tracks (*Consultant, Data Scientist, Data Analyst, Financial Analyst, Government Roles, Research, APM/Product Analyst*) using a rubric:
   - Keyword Match % (40%)
   - Requirement Coverage % (40%)
   - Format & Structure Check (20%)
   - Transparent Gap Analysis & Explanations

2. **Multi-Agent Pipeline**:
   - **Parser Agent & Guardrails**: Extracts role, company, requirements, email; flags scam/spam patterns (unpaid long probations, wire transfers, suspicious domains).
   - **Duplicate Post Detection**: Fuzzy matching (`difflib`) on `Company + Role` to prevent re-applying.
   - **MCP Tools Suite**: Company profile lookup, 30-day news search hook, and salary benchmark tools.
   - **Writer Agent with A/B Experimentation**: Generates Variant A (Direct Value) vs Variant B (Curiosity Hook) subject lines, tailored cold email body with resume attachment, and copy-paste ready LinkedIn DMs (<150 words).

3. **Autonomous Monitoring & Follow-Up System**:
   - **Reply Detection**: Cross-checks inbox for replies to tracked applications.
   - **3-Day Follow-Up Agent**: Auto-drafts follow-up emails for applications pending >3 days without reply.
   - **Sent-Folder Reconciliation**: Audits sent emails against database records.

4. **Streamlit Multi-Tab Workspace**:
   - **Tab 1: Cold Email Studio & Launcher**: Process JDs, view ATS scores, edit email & A/B subjects, copy LinkedIn DM, send email.
   - **Tab 2: History & Analytics Dashboard**: Bar & funnel charts (Sent / Pending / Replied per vertical, A/B subject line conversion rates).
   - **Tab 3: Follow-Up & Reply Digest**: Review and 1-click send auto-drafted follow-ups.
   - **Tab 4: Agent Observability**: Dark terminal aesthetic dashboard showing latency (ms), token consumption, and agent traces.
   - **Tab 5: Vertical Resumes Manager**: View/Edit all 7 resume profiles.

---

## 🛠 Project Structure

```
ai_job_application_agent/
├── app.py                      # Main Streamlit Application (5 Tabs)
├── database.py                 # SQLite schema, CRUD, and 7-Vertical Resume Seeds
├── test_pipeline.py            # End-to-end testing script
├── requirements.txt            # Python dependencies for Streamlit Cloud
├── README.md                   # Documentation & Setup Guide
├── .gitignore                  # Git ignore file
├── agents/
│   ├── parser_agent.py         # JD parser & Scam Guardrails Detector
│   ├── scoring_agent.py        # RAG Resume Scoring Engine across 7 Verticals
│   └── writer_agent.py         # Cold Email, A/B Subject Lines & LinkedIn DM Generator
├── tools/
│   └── mcp_tools.py            # Company lookup, 30-day news, salary benchmark tools
├── services/
│   ├── gmail_service.py        # Gmail API wrapper (with fallback simulation mode)
│   └── scheduler_agent.py      # Autonomous reply detection & follow-up draft generator
└── utils/
    └── observability.py        # Token & latency logger for dark terminal telemetry
```

---

## 🚀 How to Host on Streamlit Cloud

1. **Push code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of AI Job Application Agent"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-job-application-agent.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
   - Click **"New app"**.
   - Select your repository (`ai-job-application-agent`), branch (`main`), and set Main file path to `app.py`.
   - Click **"Deploy!"**.
