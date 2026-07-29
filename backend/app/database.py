import sqlite3
import os
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_db_path() -> str:
    return os.environ.get("EXECUTIVE_DASHBOARD_DB_PATH", os.path.join(os.path.dirname(CURRENT_DIR), "application_state.db"))


def init_db():
    """Initializes advanced tracking state memory for the executive search."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_jobs (
            id TEXT PRIMARY KEY,
            company TEXT,
            title TEXT,
            url TEXT,
            apply_url TEXT,
            location TEXT,
            source TEXT,
            raw_description TEXT,
            match_score REAL,
            processed_at TEXT,
            status TEXT DEFAULT 'Evaluated',
            applied INTEGER DEFAULT 0,
            notes TEXT
        )
    """)
    conn.commit()
    # Ensure schema evolution: add columns if older DB exists without them
    cursor.execute("PRAGMA table_info(processed_jobs)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'url' not in cols:
        try:
            cursor.execute("ALTER TABLE processed_jobs ADD COLUMN url TEXT")
        except Exception:
            pass
    if 'apply_url' not in cols:
        try:
            cursor.execute("ALTER TABLE processed_jobs ADD COLUMN apply_url TEXT")
        except Exception:
            pass
    if 'raw_description' not in cols:
        try:
            cursor.execute("ALTER TABLE processed_jobs ADD COLUMN raw_description TEXT")
        except Exception:
            pass
    if 'location' not in cols:
        try:
            cursor.execute("ALTER TABLE processed_jobs ADD COLUMN location TEXT")
        except Exception:
            pass
    if 'source' not in cols:
        try:
            cursor.execute("ALTER TABLE processed_jobs ADD COLUMN source TEXT")
        except Exception:
            pass
    if 'applied' not in cols:
        try:
            cursor.execute("ALTER TABLE processed_jobs ADD COLUMN applied INTEGER DEFAULT 0")
        except Exception:
            pass
    conn.commit()
    conn.close()


def remove_mock_jobs():
    """Remove legacy demo records so only genuine board listings appear in the UI."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM processed_jobs
        WHERE source = 'Mock'
           OR company IN ('Enterprise Cloud Systems', 'Midwest Tech Partners', 'Vanguard Data Systems')
           OR url LIKE '%3456789%'
    """)
    removed = cursor.rowcount
    conn.commit()
    conn.close()
    return removed


def remove_duplicate_jobs():
    """Keep one copy when a board exposes the same role under multiple URLs."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM processed_jobs
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM processed_jobs
            GROUP BY LOWER(COALESCE(source, '')), LOWER(COALESCE(company, '')),
                     LOWER(COALESCE(title, '')), LOWER(COALESCE(location, ''))
        )
    """)
    removed = cursor.rowcount
    conn.commit()
    conn.close()
    return removed

def is_job_processed(job_id: str) -> bool:
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_jobs WHERE id = ?", (job_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_all_processed_job_ids() -> set:
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM processed_jobs")
    rows = cursor.fetchall()
    conn.close()
    return {r[0] for r in rows}


def mark_job_as_processed(job_id: str, company: str, title: str, match_score: float, url: str = None, apply_url: str = None, location: str = None, source: str = None, raw_description: str = None):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO processed_jobs (id, company, title, url, apply_url, location, source, raw_description, match_score, processed_at, status, applied) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Evaluated', 0)
        """, (job_id, company, title, url, apply_url, location, source, raw_description, match_score, datetime.now().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        # Possibly already inserted; ignore
        pass 
    conn.close()

def update_job_status(job_id: str, new_status: str, notes: str = None):
    """Transitions a job status (e.g., Applied, Interviewing, Offer, Archived)."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    applied_flag = 1 if new_status and new_status.lower() == 'applied' else 0
    cursor.execute("""
        UPDATE processed_jobs 
        SET status = ?, notes = COALESCE(?, notes), applied = COALESCE(?, applied)
        WHERE id = ?
    """, (new_status, notes, applied_flag, job_id))
    conn.commit()
    conn.close()

def get_pipeline_snapshot():
    """Returns an executive dashboard breakdown of all pipeline stages."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, company, title, url, apply_url, location, source, raw_description, match_score, status, applied, notes, processed_at
        FROM processed_jobs
        WHERE COALESCE(source, '') != 'Mock'
          AND COALESCE(url, '') NOT LIKE '%3456789%'
        ORDER BY match_score DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
