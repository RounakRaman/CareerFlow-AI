import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from database import (
    init_db, get_applications, save_application, get_all_resumes,
    update_resume, check_duplicate_application, get_ab_subject_analytics, log_scoring
)
from agents.parser_agent import parse_job_post
from agents.scoring_agent import score_all_verticals
from agents.writer_agent import generate_cold_email_and_dm
from tools.mcp_tools import company_info_lookup, recent_news_lookup, salary_benchmark_tool
from services.gmail_service import send_email_via_gmail
from services.scheduler_agent import (
    run_reply_detection_job, generate_stale_followup_drafts, run_sent_folder_reconciliation
)
from utils.observability import get_observability_logs

# Page Config
st.set_page_config(
    page_title="AI Job Application Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# Custom Styling (Dark Terminal + Modern Clean UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@400;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #0E1117;
        color: #E0E6ED;
    }
    .metric-card {
        background: linear-gradient(135deg, #1A1F2C 0%, #11141D 100%);
        border: 1px solid #2E364F;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4F9CF9;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #8C9BAE;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .terminal-box {
        background-color: #0A0D14;
        border: 1px solid #1E2638;
        border-radius: 8px;
        padding: 16px;
        font-family: 'Fira Code', monospace;
        color: #38BDF8;
        font-size: 0.85rem;
    }
    .guardrail-alert {
        background-color: #3B1219;
        border: 1px solid #991B1B;
        border-radius: 8px;
        padding: 14px;
        color: #FCA5A5;
    }
    .duplicate-warning {
        background-color: #332A15;
        border: 1px solid #854D0E;
        border-radius: 8px;
        padding: 14px;
        color: #FDE047;
    }
    .score-card {
        background-color: #161B26;
        border: 1px solid #262E40;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation Header
st.sidebar.title("⚡ Job Application Agent")
st.sidebar.caption("LangChain Multi-Agent System | 7 Resume Verticals")
st.sidebar.markdown("---")

# Main Navigation Tabs
tab_studio, tab_dashboard, tab_followup, tab_observability, tab_resumes = st.tabs([
    "🎯 Cold Email Studio",
    "📊 History & Analytics",
    "⏰ Follow-Up & Replies",
    "🖥️ Agent Observability",
    "📄 Resume Verticals"
])

# ==========================================
# TAB 1: COLD EMAIL STUDIO & LAUNCHER
# ==========================================
with tab_studio:
    st.header("🎯 Job Application & Cold Email Studio")
    st.caption("Paste a job post (LinkedIn JD / Google Form / Email) to run multi-agent parsing, RAG scoring, and cold email drafting.")

    col_input, col_action = st.columns([2, 1])
    
    with col_input:
        sample_jd = """Hiring: Senior Data Analyst / Strategy Analyst at BeyondTech
Role: Senior Data Analyst
Company: BeyondTech
Recipient Contact: hiring@beyondtech.edu

We are looking for a Data Analyst with experience in SQL, Python, Tableau, and Streamlit dashboards.
Requirements:
- 2+ years experience in data analytics, ETL pipelines, and business intelligence.
- Proficient in building interactive dashboards (Tableau/PowerBI/Streamlit).
- Strong background in SQL query optimization and Python data manipulation.
- Experience conducting GTM customer funnel analysis and operational automation.
- Degree in CS/IT or quantitative field preferred."""

        job_post_raw = st.text_area(
            "Paste Job Post Content:",
            value=sample_jd,
            height=200,
            help="Paste raw JD, LinkedIn post text, or recruitment email."
        )

    with col_action:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🚀 Analyze & Process JD", type="primary", use_container_width=True)
        clear_btn = st.button("🔄 Reset Studio", use_container_width=True)

    if clear_btn:
        st.session_state.pop("parsed_jd", None)
        st.session_state.pop("scores", None)
        st.experimental_rerun()

    if analyze_btn or "parsed_jd" in st.session_state:
        if analyze_btn:
            with st.spinner("🤖 Parser Agent extracting requirements & running guardrails..."):
                parsed = parse_job_post(job_post_raw)
                scores = score_all_verticals(parsed["requirements"], job_post_raw)
                
                st.session_state["parsed_jd"] = parsed
                st.session_state["scores"] = scores
                st.session_state["selected_vertical"] = scores[0]["vertical_name"]

        parsed = st.session_state["parsed_jd"]
        scores = st.session_state["scores"]

        st.markdown("---")
        
        # 1. Guardrail & Scam Detector Alert
        if parsed["guardrail_status"] == "FLAGGED":
            st.markdown(f"""
            <div class="guardrail-alert">
                <strong>🚨 Trust & Safety Guardrail Alert:</strong> Suspicious post indicators detected!
                <ul>{"".join(f"<li>{w}</li>" for w in parsed["scam_warnings"])}</ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("✅ Guardrail Check Passed: Professional job posting format verified.")

        # 2. Duplicate Check
        duplicate = check_duplicate_application(parsed["company"], parsed["role_title"])
        if duplicate:
            st.markdown(f"""
            <div class="duplicate-warning">
                <strong>⚠️ Duplicate Application Warning:</strong> You previously applied for 
                <strong>{duplicate['role_title']}</strong> at <strong>{duplicate['company']}</strong> 
                on {duplicate['date_sent'][:10]} using the <em>{duplicate['vertical_used']}</em> track. (Similarity match: {duplicate['similarity_score']*100}%)
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Extracted Details Card
        col_meta1, col_meta2, col_meta3 = st.columns(3)
        with col_meta1:
            parsed_company = st.text_input("Extracted Company:", value=parsed["company"])
        with col_meta2:
            parsed_role = st.text_input("Extracted Role:", value=parsed["role_title"])
        with col_meta3:
            parsed_email = st.text_input("Recipient Email:", value=parsed["recipient_email"] or "hiring@company.com")

        st.markdown("### 📊 RAG Resume Scoring Engine (All 7 Verticals)")
        st.caption("Each vertical is benchmarked using a rubric: Keyword Coverage (40%), Requirement Match (40%), Format Check (20%).")

        # Score Matrix Display
        score_cols = st.columns(7)
        for idx, sc in enumerate(scores):
            with score_cols[idx]:
                is_top = (idx == 0)
                st.markdown(f"""
                <div class="score-card" style="border-top: 3px solid {'#38BDF8' if is_top else '#2E364F'};">
                    <div style="font-size: 0.8rem; font-weight:600; color: {'#38BDF8' if is_top else '#A0AEC0'};">{sc['vertical_name']}</div>
                    <div style="font-size: 1.6rem; font-weight:700; color: #FFFFFF;">{sc['ats_score']}<span style="font-size:0.8rem; color:#718096;">/100</span></div>
                    <div style="font-size: 0.75rem; color: #A0AEC0;">Match: {sc['requirement_coverage_pct']}%</div>
                </div>
                """, unsafe_allow_html=True)

        # 1-Click Vertical Selector
        vertical_names = [s["vertical_name"] for s in scores]
        selected_vert_name = st.selectbox(
            "Select Resume Vertical for Cold Pitch:",
            options=vertical_names,
            index=vertical_names.index(st.session_state.get("selected_vertical", vertical_names[0]))
        )
        st.session_state["selected_vertical"] = selected_vert_name

        selected_score_data = next(s for s in scores if s["vertical_name"] == selected_vert_name)
        st.info(f"**Score Breakdown ({selected_vert_name})**: {selected_score_data['gap_summary']}")

        # Fetch Resumes & MCP Context
        all_res = get_all_resumes()
        selected_res = next(r for r in all_res if r["vertical_name"] == selected_vert_name)

        subjects, email_body, linkedin_dm = generate_cold_email_and_dm(
            company=parsed_company,
            role_title=parsed_role,
            vertical_name=selected_vert_name,
            resume_text=selected_res["resume_text"],
            requirements=parsed["requirements"],
            recipient_email=parsed_email
        )

        st.markdown("---")
        st.markdown("### ✉️ Email & Pitch Studio")

        col_email, col_dm = st.columns([3, 2])

        with col_email:
            st.subheader("Cold Email Preview")
            
            ab_choice = st.radio(
                "A/B Subject Line Variant:",
                options=["Variant A (Direct Value)", "Variant B (Curiosity Hook)"],
                horizontal=True
            )
            
            chosen_variant = "A" if "Variant A" in ab_choice else "B"
            chosen_subject = subjects["variant_a"] if chosen_variant == "A" else subjects["variant_b"]
            
            subject_input = st.text_input("Subject Line:", value=chosen_subject)
            editable_email = st.text_area("Email Content (Editable):", value=email_body, height=320)
            
            st.caption(f"📎 Auto-attached: `{selected_vert_name}_Resume_Rounak_Raman.pdf`")

            send_now = st.button("✉️ Send Cold Email via Gmail API", type="primary", use_container_width=True)

            if send_now:
                with st.spinner("Dispatching cold email & logging application..."):
                    res_send = send_email_via_gmail(
                        recipient_email=parsed_email,
                        subject=subject_input,
                        body=editable_email,
                        attachment_name=f"{selected_vert_name}_Resume.pdf"
                    )
                    
                    app_id = save_application({
                        "company": parsed_company,
                        "role_title": parsed_role,
                        "vertical_used": selected_vert_name,
                        "recipient_email": parsed_email,
                        "job_post_raw": job_post_raw,
                        "ats_score": selected_score_data["ats_score"],
                        "email_thread_id": res_send["email_thread_id"],
                        "linkedin_dm_generated": True,
                        "subject_line_variant": chosen_variant,
                        "subject_line_text": subject_input,
                        "status": "sent"
                    })
                    
                    log_scoring(
                        application_id=app_id,
                        vertical_id=selected_score_data["vertical_id"],
                        ats_score=selected_score_data["ats_score"],
                        kw_pct=selected_score_data["keyword_match_pct"],
                        req_pct=selected_score_data["requirement_coverage_pct"],
                        fmt_score=selected_score_data["format_score"],
                        gap_summary=selected_score_data["gap_summary"]
                    )
                    
                    st.balloons()
                    st.success(f"🎉 Application Logged (ID: #{app_id})! Email dispatched via {res_send['mode']}.")

        with col_dm:
            st.subheader("LinkedIn DM Pitch")
            st.caption("🔒 **Compliance Note**: LinkedIn ToS prohibits automated sending. Use manual copy-paste below.")
            
            st.text_area("LinkedIn Message (<150 words):", value=linkedin_dm, height=260, key="dm_area")
            
            st.code(linkedin_dm, language="text")
            st.info("💡 Highlight and copy the snippet above for your manual LinkedIn message outreach.")

# ==========================================
# TAB 2: APPLICATION HISTORY & ANALYTICS
# ==========================================
with tab_dashboard:
    st.header("📊 Application History & Analytics Dashboard")
    st.caption("Track applications across verticals, monitor reply rates, and analyze A/B subject line conversion statistics.")

    apps = get_applications()
    
    if not apps:
        st.info("No applications logged yet. Use the Cold Email Studio to process your first application!")
    else:
        # High level metrics
        total_apps = len(apps)
        replied_count = sum(1 for a in apps if a["status"] == "replied")
        reply_rate = round((replied_count / max(total_apps, 1)) * 100, 1)
        
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Sent</div><div class="metric-value">{total_apps}</div></div>""", unsafe_allow_html=True)
        with mcol2:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Replies Received</div><div class="metric-value">{replied_count}</div></div>""", unsafe_allow_html=True)
        with mcol3:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Reply Rate</div><div class="metric-value">{reply_rate}%</div></div>""", unsafe_allow_html=True)
        with mcol4:
            top_vert = pd.DataFrame(apps)["vertical_used"].mode()[0] if not pd.DataFrame(apps).empty else "N/A"
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Top Vertical Track</div><div class="metric-value" style="font-size:1.4rem;">{top_vert}</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        df_apps = pd.DataFrame(apps)

        # Charts Section
        c_chart1, c_chart2 = st.columns(2)

        with c_chart1:
            st.subheader("Applications by Resume Vertical")
            vert_counts = df_apps.groupby(["vertical_used", "status"]).size().reset_index(name="count")
            fig_vert = px.bar(
                vert_counts,
                x="vertical_used",
                y="count",
                color="status",
                barmode="group",
                color_discrete_map={"sent": "#38BDF8", "replied": "#34D399", "follow_up_sent": "#FBBF24"},
                template="plotly_dark"
            )
            fig_vert.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_vert, use_container_width=True)

        with c_chart2:
            st.subheader("A/B Subject Line Reply Rate Experiment")
            ab_data = get_ab_subject_analytics()
            if ab_data:
                df_ab = pd.DataFrame(ab_data)
                df_ab["reply_rate_pct"] = (df_ab["total_replied"] / df_ab["total_sent"] * 100).round(1)
                fig_ab = px.bar(
                    df_ab,
                    x="subject_line_variant",
                    y="reply_rate_pct",
                    color="subject_line_variant",
                    text="reply_rate_pct",
                    labels={"subject_line_variant": "Variant", "reply_rate_pct": "Reply Rate %"},
                    template="plotly_dark",
                    color_discrete_sequence=["#6366F1", "#EC4899"]
                )
                fig_ab.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_ab, use_container_width=True)
            else:
                st.caption("Accumulating A/B experiment data...")

        st.markdown("### 📋 Application History Table")
        
        # Filtering
        selected_filter_vert = st.selectbox("Filter by Vertical:", options=["All Verticals"] + list(df_apps["vertical_used"].unique()))
        if selected_filter_vert != "All Verticals":
            df_filtered = df_apps[df_apps["vertical_used"] == selected_filter_vert]
        else:
            df_filtered = df_apps

        st.dataframe(
            df_filtered[["id", "company", "role_title", "vertical_used", "recipient_email", "ats_score", "date_sent", "status", "days_since_sent", "subject_line_variant"]],
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# TAB 3: FOLLOW-UP & REPLIES
# ==========================================
with tab_followup:
    st.header("⏰ Follow-Up Reminder & Reply Engine")
    st.caption("Autonomous monitoring engine: Auto-detects Gmail replies and prepares follow-up drafts for pending applications.")

    f_col1, f_col2 = st.columns([1, 1])
    with f_col1:
        if st.button("🔍 Run Gmail Reply Detection Job", type="primary", use_container_width=True):
            with st.spinner("Scanning inbox threads for replies..."):
                updated = run_reply_detection_job()
                st.success(f"Reply Detection complete! Updated {updated} application statuses.")

    with f_col2:
        if st.button("🔄 Run Sent-Folder Reconciliation", use_container_width=True):
            with st.spinner("Auditing DB vs Sent Folder..."):
                audit = run_sent_folder_reconciliation()
                st.info(f"Audit Complete: {audit['verified_in_sent_folder']}/{audit['total_tracked']} applications verified in sent folder.")

    st.markdown("---")
    st.markdown("### 📩 Pending Follow-Up Drafts (Stale > 3 Days)")
    
    threshold_days = st.slider("Days Threshold for Follow-Up:", min_value=0, max_value=14, value=3)
    stale_drafts = generate_stale_followup_drafts(days_threshold=threshold_days)

    if not stale_drafts:
        st.success(f"🎉 No pending follow-ups! All applications sent within {threshold_days} days are active or replied to.")
    else:
        for draft in stale_drafts:
            with st.expander(f"📌 {draft['company']} — {draft['role_title']} (Sent {draft['days_since_sent']} days ago)"):
                st.write(f"**Recipient:** `{draft['recipient_email']}`")
                st.write(f"**Subject:** {draft['follow_up_subject']}")
                fu_text = st.text_area("Follow-up Body:", value=draft['follow_up_body'], height=180, key=f"fu_{draft['application_id']}")
                
                if st.button(f"✉️ Send 1-Click Follow-Up (#{draft['application_id']})", key=f"btn_fu_{draft['application_id']}"):
                    send_email_via_gmail(draft['recipient_email'], draft['follow_up_subject'], fu_text)
                    st.success(f"Follow-up sent for application #{draft['application_id']}!")

# ==========================================
# TAB 4: AGENT OBSERVABILITY
# ==========================================
with tab_observability:
    st.header("🖥️ System Observability & Agent Logs")
    st.caption("RupiCast-style dark terminal dashboard tracking latency, tokens, and model execution steps.")

    logs = get_observability_logs(limit=100)
    
    if not logs:
        st.info("No observability logs captured yet. Execute operations in Studio to populate execution logs.")
    else:
        df_logs = pd.DataFrame(logs)

        # Overview Metrics
        o_col1, o_col2, o_col3, o_col4 = st.columns(4)
        with o_col1:
            st.metric("Total Agent Executions", len(df_logs))
        with o_col2:
            st.metric("Avg Latency (ms)", f"{int(df_logs['latency_ms'].mean())} ms")
        with o_col3:
            st.metric("Total Tokens Consumed", f"{df_logs['tokens_used'].sum():,}")
        with o_col4:
            st.metric("Primary Model", df_logs["model_used"].mode()[0] if not df_logs.empty else "N/A")

        st.markdown("<br>", unsafe_allow_html=True)

        col_obs1, col_obs2 = st.columns([1, 1])

        with col_obs1:
            st.subheader("Agent Step Latency Breakdown (ms)")
            latency_by_step = df_logs.groupby("agent_step")["latency_ms"].mean().reset_index()
            fig_lat = px.bar(
                latency_by_step,
                x="agent_step",
                y="latency_ms",
                color="agent_step",
                template="plotly_dark",
                labels={"latency_ms": "Latency (ms)", "agent_step": "Agent Step"}
            )
            fig_lat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_lat, use_container_width=True)

        with col_obs2:
            st.subheader("Dark Terminal Telemetry Log")
            log_terminal_text = ""
            for idx, r in df_logs.head(15).iterrows():
                log_terminal_text += f"[{r['timestamp'][:19]}] STEP: {r['agent_step']:<25} | MODEL: {r['model_used']:<15} | TOKENS: {r['tokens_used']:<5} | LATENCY: {r['latency_ms']}ms\n"
            
            st.markdown(f'<div class="terminal-box"><pre>{log_terminal_text}</pre></div>', unsafe_allow_html=True)

        st.markdown("### 📜 Detailed Execution Trace")
        st.dataframe(df_logs[["id", "timestamp", "agent_step", "model_used", "tokens_used", "latency_ms", "details"]], use_container_width=True, hide_index=True)

# ==========================================
# TAB 5: VERTICAL RESUMES MANAGER
# ==========================================
with tab_resumes:
    st.header("📄 Vertical Resumes Corpus Manager")
    st.caption("View, inspect, and update plain-text resumes for all 7 vertical tracks used for RAG ATS scoring.")

    resumes = get_all_resumes()
    res_names = [r["vertical_name"] for r in resumes]
    
    selected_mgr_vert = st.selectbox("Select Vertical Resume to Inspect/Edit:", options=res_names)
    target_res = next(r for r in resumes if r["vertical_name"] == selected_mgr_vert)

    st.write(f"**Last Updated:** {target_res['last_updated']}")
    
    updated_resume_text = st.text_area(
        f"Resume Plain Text ({selected_mgr_vert}):",
        value=target_res["resume_text"],
        height=400
    )

    if st.button("💾 Save Resume Updates", type="primary"):
        update_resume(selected_mgr_vert, updated_resume_text)
        st.success(f"Updated resume text for {selected_mgr_vert} successfully!")
