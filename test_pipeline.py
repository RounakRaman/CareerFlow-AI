import os
import sys

# Ensure local imports work
sys.path.append(os.path.dirname(__file__))

from database import init_db, get_all_resumes, save_application, get_applications, check_duplicate_application
from agents.parser_agent import parse_job_post
from agents.scoring_agent import score_all_verticals
from agents.writer_agent import generate_cold_email_and_dm
from tools.mcp_tools import company_info_lookup, recent_news_lookup, salary_benchmark_tool
from services.gmail_service import send_email_via_gmail
from services.scheduler_agent import run_reply_detection_job, generate_stale_followup_drafts, run_sent_folder_reconciliation
from utils.observability import get_observability_logs

def test_full_pipeline():
    print("--- 1. Database & Seed Verification ---")
    init_db()
    resumes = get_all_resumes()
    print(f"✅ Found {len(resumes)} vertical resumes in DB.")
    assert len(resumes) == 7, f"Expected 7 resumes, got {len(resumes)}"

    print("\n--- 2. Parser & Scam Guardrail Verification ---")
    sample_jd = """
    Role: Machine Learning Engineer
    Company: BeyondTech
    Email: hr@beyondtech.ai
    Requirements:
    - Experience in Python, PyTorch, HuggingFace, and RAG architectures.
    - Strong background in building computer vision or LLM applications.
    - Degree in CS or IT preferred.
    """
    parsed = parse_job_post(sample_jd)
    print(f"✅ Extracted Company: {parsed['company']}")
    print(f"✅ Extracted Role: {parsed['role_title']}")
    print(f"✅ Guardrail Status: {parsed['guardrail_status']}")
    assert parsed['guardrail_status'] == "PASSED"

    # Scam post test
    scam_jd = "Hiring immediately! Telegram only @scammer. Wire money for registration fee. Pay for training."
    parsed_scam = parse_job_post(scam_jd)
    print(f"✅ Scam Guardrail Status: {parsed_scam['guardrail_status']} (Warnings: {len(parsed_scam['scam_warnings'])})")
    assert parsed_scam['guardrail_status'] == "FLAGGED"

    print("\n--- 3. 7-Vertical RAG ATS Scoring Engine ---")
    scores = score_all_verticals(parsed['requirements'], sample_jd)
    print(f"✅ Scored {len(scores)} verticals. Top vertical: {scores[0]['vertical_name']} with ATS score {scores[0]['ats_score']}/100.")
    assert len(scores) == 7

    print("\n--- 4. MCP Tools Verification ---")
    comp_info = company_info_lookup("BeyondTech")
    news_info = recent_news_lookup("BeyondTech")
    salary_info = salary_benchmark_tool("Machine Learning Engineer", "BeyondTech")
    print(f"✅ Company Info: {comp_info}")
    print(f"✅ News Hook: {news_info['headline']}")
    print(f"✅ Salary Benchmark: {salary_info['salary_range']}")

    print("\n--- 5. Writer Agent & A/B Subject Lines ---")
    top_vert = scores[0]['vertical_name']
    subjects, email_body, linkedin_dm = generate_cold_email_and_dm(
        company=parsed['company'],
        role_title=parsed['role_title'],
        vertical_name=top_vert,
        resume_text=resumes[0]['resume_text'],
        requirements=parsed['requirements'],
        recipient_email=parsed['recipient_email']
    )
    print(f"✅ Subject Variant A: {subjects['variant_a']}")
    print(f"✅ Subject Variant B: {subjects['variant_b']}")
    print(f"✅ Email Length: {len(email_body)} chars")
    print(f"✅ LinkedIn DM Word Count: {len(linkedin_dm.split())} words")
    assert len(linkedin_dm.split()) < 150

    print("\n--- 6. Gmail Service & DB Application Logging ---")
    email_res = send_email_via_gmail(
        recipient_email=parsed['recipient_email'],
        subject=subjects['variant_a'],
        body=email_body
    )
    app_id = save_application({
        "company": parsed['company'],
        "role_title": parsed['role_title'],
        "vertical_used": top_vert,
        "recipient_email": parsed['recipient_email'],
        "job_post_raw": sample_jd,
        "ats_score": scores[0]['ats_score'],
        "email_thread_id": email_res['email_thread_id'],
        "subject_line_variant": "A",
        "subject_line_text": subjects['variant_a']
    })
    print(f"✅ Saved application #{app_id} with thread ID {email_res['email_thread_id']}")

    print("\n--- 7. Duplicate Application Check ---")
    dup = check_duplicate_application("BeyondTech", "Machine Learning Engineer")
    print(f"✅ Duplicate Match Found: {dup['company']} - {dup['role_title']} (Score: {dup['similarity_score']})")
    assert dup is not None

    print("\n--- 8. Scheduler Agent & Follow-up Reminders ---")
    replied = run_reply_detection_job()
    stale_drafts = generate_stale_followup_drafts(days_threshold=0)
    audit = run_sent_folder_reconciliation()
    print(f"✅ Reply detection ran. Updated: {replied}")
    print(f"✅ Stale follow-up drafts generated: {len(stale_drafts)}")
    print(f"✅ Sent folder reconciliation audit: {audit}")

    print("\n--- 9. Observability & Agent Logs ---")
    obs_logs = get_observability_logs(limit=10)
    print(f"✅ Captured {len(obs_logs)} observability traces.")
    assert len(obs_logs) > 0

    print("\n🎉 ALL PIPELINE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_pipeline()
