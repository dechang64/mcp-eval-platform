"""SQLite result store - server configs / test results / run history"""
import json
import sqlite3
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mcp_eval.db")


def get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        transport TEXT NOT NULL,
        config_json TEXT NOT NULL,
        description TEXT DEFAULT '',
        tags TEXT DEFAULT '[]',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS test_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER NOT NULL,
        server_name TEXT NOT NULL,
        suite_type TEXT NOT NULL,  -- functional/performance/security/all
        status TEXT NOT NULL,      -- running/passed/failed/error
        total_cases INTEGER DEFAULT 0,
        passed INTEGER DEFAULT 0,
        failed INTEGER DEFAULT 0,
        skipped INTEGER DEFAULT 0,
        duration_sec REAL DEFAULT 0,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        summary_json TEXT DEFAULT '{}',
        FOREIGN KEY (server_id) REFERENCES servers(id)
    );

    CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        case_id TEXT NOT NULL,
        case_name TEXT NOT NULL,
        category TEXT NOT NULL,
        status TEXT NOT NULL,     -- passed/failed/skipped/error
        duration_ms REAL DEFAULT 0,
        detail_json TEXT DEFAULT '{}',
        error_msg TEXT DEFAULT '',
        FOREIGN KEY (run_id) REFERENCES test_runs(id)
    );

    CREATE INDEX IF NOT EXISTS idx_results_run ON test_results(run_id);
    CREATE INDEX IF NOT EXISTS idx_runs_server ON test_runs(server_id);
    """)
    conn.commit()
    conn.close()


def add_server(name: str, transport: str, config: dict, description: str = "", tags: list = None) -> int:
    conn = get_db()
    now = datetime.now().isoformat()
    cur = conn.execute(
        "INSERT INTO servers (name, transport, config_json, description, tags, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        (name, transport, json.dumps(config), description, json.dumps(tags or []), now, now),
    )
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return sid


def list_servers() -> list[dict]:
    conn = get_db()
    rows = conn.execute("SELECT * FROM servers ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_server(sid: int) -> Optional[dict]:
    conn = get_db()
    row = conn.execute("SELECT * FROM servers WHERE id=?", (sid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_server(sid: int, **fields):
    conn = get_db()
    now = datetime.now().isoformat()
    fields["updated_at"] = now
    sets = ", ".join(f"{k}=?" for k in fields)
    conn.execute(f"UPDATE servers SET {sets} WHERE id=?", (*fields.values(), sid))
    conn.commit()
    conn.close()


def delete_server(sid: int):
    conn = get_db()
    # cascade delete runs and results
    run_ids = [r["id"] for r in conn.execute("SELECT id FROM test_runs WHERE server_id=?", (sid,)).fetchall()]
    for rid in run_ids:
        conn.execute("DELETE FROM test_results WHERE run_id=?", (rid,))
    conn.execute("DELETE FROM test_runs WHERE server_id=?", (sid,))
    conn.execute("DELETE FROM servers WHERE id=?", (sid,))
    conn.commit()
    conn.close()


def create_run(server_id: int, server_name: str, suite_type: str) -> int:
    conn = get_db()
    now = datetime.now().isoformat()
    cur = conn.execute(
        "INSERT INTO test_runs (server_id, server_name, suite_type, status, started_at) VALUES (?,?,?,?,?)",
        (server_id, server_name, suite_type, "running", now),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def add_result(run_id: int, case_id: str, case_name: str, category: str,
               status: str, duration_ms: float, detail: dict, error_msg: str = ""):
    conn = get_db()
    conn.execute(
        "INSERT INTO test_results (run_id, case_id, case_name, category, status, duration_ms, detail_json, error_msg) VALUES (?,?,?,?,?,?,?,?)",
        (run_id, case_id, case_name, category, status, duration_ms, json.dumps(detail), error_msg),
    )
    conn.commit()
    conn.close()


def finish_run(run_id: int, status: str, total: int, passed: int, failed: int, skipped: int, duration: float, summary: dict):
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        "UPDATE test_runs SET status=?, total_cases=?, passed=?, failed=?, skipped=?, duration_sec=?, finished_at=?, summary_json=? WHERE id=?",
        (status, total, passed, failed, skipped, duration, now, json.dumps(summary), run_id),
    )
    conn.commit()
    conn.close()


def list_runs(limit: int = 50, server_id: int = None) -> list[dict]:
    conn = get_db()
    if server_id:
        rows = conn.execute("SELECT * FROM test_runs WHERE server_id=? ORDER BY started_at DESC LIMIT ?", (server_id, limit)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM test_runs ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_run(run_id: int) -> Optional[dict]:
    conn = get_db()
    row = conn.execute("SELECT * FROM test_runs WHERE id=?", (run_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_results(run_id: int) -> list[dict]:
    conn = get_db()
    rows = conn.execute("SELECT * FROM test_results WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Aliases used by modules
get_run_results = get_results


def save_run(run_data: dict, results: list[dict]) -> int:
    """One-stop save: create run + store all results + finish"""
    rid = create_run(run_data["server_id"], run_data["server_name"], run_data["suite_type"])
    for r in results:
        add_result(rid, r["case_id"], r["case_name"], r["category"],
                   r["status"], r["duration_ms"], r.get("detail", {}), r.get("error_msg", ""))
    # Sum of case durations = total test duration (more meaningful than DB write time)
    dur = sum(r.get("duration_ms", 0) for r in results) / 1000.0
    finish_run(rid, run_data["status"], run_data["total_cases"],
               run_data["passed"], run_data["failed"], 0, dur, {})
    return rid


def get_server_runs(server_id: int) -> list[dict]:
    conn = get_db()
    rows = conn.execute("SELECT * FROM test_runs WHERE server_id=? ORDER BY started_at DESC", (server_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard_stats() -> dict:
    conn = get_db()
    servers = conn.execute("SELECT COUNT(*) as c FROM servers").fetchone()["c"]
    runs = conn.execute("SELECT COUNT(*) as c FROM test_runs").fetchone()["c"]
    passed_runs = conn.execute("SELECT COUNT(*) as c FROM test_runs WHERE status='passed'").fetchone()["c"]
    total_cases = conn.execute("SELECT COUNT(*) as c FROM test_results").fetchone()["c"]
    passed_cases = conn.execute("SELECT COUNT(*) as c FROM test_results WHERE status='passed'").fetchone()["c"]
    recent = conn.execute("SELECT * FROM test_runs ORDER BY started_at DESC LIMIT 10").fetchall()
    conn.close()
    return {
        "servers": servers,
        "runs": runs,
        "passed_runs": passed_runs,
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "recent_runs": [dict(r) for r in recent],
    }


# Initialize on import
init_db()
