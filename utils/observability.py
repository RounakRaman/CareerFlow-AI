import sqlite3
import time
from datetime import datetime
from typing import Dict, Any, Optional
from database import get_db

def log_agent_execution(agent_step: str, model_used: str, tokens_used: int, latency_ms: int,
                        application_id: Optional[int] = None, details: str = ""):
    """Logs agent execution stats (latency, tokens, step, model) to observability_log."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO observability_log (application_id, agent_step, model_used, tokens_used, latency_ms, timestamp, details)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (application_id, agent_step, model_used, tokens_used, latency_ms, datetime.now().isoformat(), details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Observability Error] {e}")

class TimedExecution:
    def __init__(self, agent_step: str, model_used: str = "gemini-3.6-flash", application_id: Optional[int] = None):
        self.agent_step = agent_step
        self.model_used = model_used
        self.application_id = application_id
        self.start_time = 0
        self.tokens_used = 0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = int((time.time() - self.start_time) * 1000)
        details = f"Status: {'Success' if exc_type is None else f'Error: {exc_val}'}"
        log_agent_execution(
            agent_step=self.agent_step,
            model_used=self.model_used,
            tokens_used=self.tokens_used or 250,  # Estimated or captured token count
            latency_ms=latency_ms,
            application_id=self.application_id,
            details=details
        )

def get_observability_logs(limit: int = 50):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM observability_log ORDER BY id DESC LIMIT ?;", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
