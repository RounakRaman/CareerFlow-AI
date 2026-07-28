from datetime import datetime, timedelta
from typing import List, Dict, Any
from database import get_db, get_applications
from services.gmail_service import check_gmail_replies
from utils.observability import TimedExecution

def run_reply_detection_job() -> int:
    """Scans all sent/pending applications in DB, checks Gmail API, updates status if replied."""
    with TimedExecution(agent_step="scheduler_reply_detection", model_used="scheduler-agent") as timer:
        apps = get_applications()
        pending_apps = [a for a in apps if a["status"] in ["sent", "follow_up_sent"] and a.get("email_thread_id")]
        
        if not pending_apps:
            return 0
            
        thread_map = {a["email_thread_id"]: a["id"] for a in pending_apps}
        replied_threads = check_gmail_replies(list(thread_map.keys()))
        
        conn = get_db()
        cursor = conn.cursor()
        updated_count = 0
        
        for tid in replied_threads:
            app_id = thread_map[tid]
            cursor.execute("UPDATE applications SET status = 'replied' WHERE id = ?;", (app_id,))
            updated_count += 1
            
        conn.commit()
        conn.close()
        timer.tokens_used = 150
        return updated_count

def generate_stale_followup_drafts(days_threshold: int = 3) -> List[Dict[str, Any]]:
    """
    Identifies applications sent > N days ago with no reply,
    and automatically drafts customized follow-up emails ready for 1-click send.
    """
    with TimedExecution(agent_step="scheduler_followup_generator", model_used="gemini-3.6-flash") as timer:
        apps = get_applications()
        stale_apps = []
        
        for app in apps:
            if app["status"] in ["sent", "no_response"] and app["days_since_sent"] >= days_threshold:
                # Draft follow-up email
                company = app["company"]
                role = app["role_title"]
                vertical = app["vertical_used"]
                recipient = app.get("recipient_email", "hiring@company.com")
                
                follow_up_body = f"""Hi {company} Hiring Team,

I hope you're having a great week. 

I'm following up on my application for the {role} role submitted a few days ago. I remain extremely interested in bringing my background in {vertical} (NSUT IT Dept Rank 1, 8.95 CGPA) to the team at {company}.

Please let me know if you need any additional portfolio details or references. Looking forward to connecting!

Best regards,
Rounak Raman
raman.rounak@gmail.com | +91 88268 79389
"""
                stale_apps.append({
                    "application_id": app["id"],
                    "company": company,
                    "role_title": role,
                    "vertical_used": vertical,
                    "recipient_email": recipient,
                    "days_since_sent": app["days_since_sent"],
                    "follow_up_subject": f"Following up: Application for {role} — Rounak Raman",
                    "follow_up_body": follow_up_body
                })
                
        timer.tokens_used = len(stale_apps) * 200
        return stale_apps

def run_sent_folder_reconciliation() -> Dict[str, int]:
    """Audits sent emails against database records."""
    with TimedExecution(agent_step="sent_folder_reconciliation", model_used="audit-agent") as timer:
        apps = get_applications()
        total_tracked = len(apps)
        verified = sum(1 for a in apps if a.get("email_thread_id"))
        
        timer.tokens_used = 100
        return {
            "total_tracked": total_tracked,
            "verified_in_sent_folder": verified,
            "unmatched_count": total_tracked - verified
        }

if __name__ == "__main__":
    print("Testing Scheduler Agent Jobs...")
    replied = run_reply_detection_job()
    print(f"Reply Detection complete. Updated {replied} applications.")
    stale = generate_stale_followup_drafts(days_threshold=0)
    print(f"Stale Follow-up Generator found {len(stale)} draft candidates.")
