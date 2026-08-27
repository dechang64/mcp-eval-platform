"""Module 9: Spec Conformance Matrix

Protocol-version-aware conformance overview for all registered servers,
aligned with the MCP specification timeline (see docs/standards-survey.md):
2024-11-05 (original) ... 2025-11-25 (tasks/elicitation) ... 2026-07-28 (stateless core).
"""
import streamlit as st
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Capability columns shown in the matrix
CAP_KEYS = ["tools", "resources", "prompts", "logging", "elicitation", "tasks", "sampling"]


def render():
    from core.results_store import list_servers, get_db
    from modules.utils import fmt_timestamp

    st.header("📐 Spec Conformance")
    st.caption("Protocol version & capability matrix across registered servers. Aligned with the MCP spec timeline: 2024-11-05 → 2025-11-25 (session era) → 2026-07-28 (stateless core).")

    _init_conformance_table()

    servers = list_servers()
    if not servers:
        st.warning("Register an MCP Server in Server Manager first")
        return

    if st.button("🔍 Probe All Servers", type="primary"):
        _probe_all(servers)

    _render_matrix()


def _probe_all(servers):
    import asyncio
    from core.mcp_client import McpClient, McpServerConfig, version_generation
    from core.results_store import get_db

    progress = st.progress(0, text="Probing servers...")
    conn = get_db()
    now = datetime.now().isoformat()
    for i, s in enumerate(servers):
        try:
            cfg = McpServerConfig.from_dict(json.loads(s["config_json"]))
            client = McpClient(cfg)
            info = asyncio.run(client.connect())
            asyncio.run(client.close())
            pv = info.get("protocol_version", "")
            caps = {}
            for k in CAP_KEYS:
                caps[k] = bool((info.get("capabilities") or {}).get(k))
            row = {
                "protocol_version": pv,
                "generation": version_generation(pv),
                "server_info": info.get("server_info") or info.get("serverInfo") or {},
                "capabilities": caps,
            }
            conn.execute(
                "INSERT INTO spec_conformance (server_id, server_name, protocol_version, generation, capabilities_json, probed_at) VALUES (?,?,?,?,?,?)",
                (s["id"], s["name"], pv, row["generation"], json.dumps(row, ensure_ascii=False), now))
        except Exception as e:
            conn.execute(
                "INSERT INTO spec_conformance (server_id, server_name, protocol_version, generation, capabilities_json, probed_at) VALUES (?,?,?,?,?,?)",
                (s["id"], s["name"], "", "probe_failed", json.dumps({"error": str(e)[:200]}), now))
        progress.progress((i + 1) / len(servers), text=f"Probed {i+1}/{len(servers)}")
    conn.commit()
    conn.close()
    progress.progress(100, text="Done")


def _render_matrix():
    import pandas as pd
    from core.results_store import get_db
    from core.mcp_client import KNOWN_PROTOCOL_VERSIONS, STATELESS_CORE_VERSION

    conn = get_db()
    rows = conn.execute("""
        SELECT sc.* FROM spec_conformance sc
        JOIN (SELECT server_id, MAX(id) AS mid FROM spec_conformance GROUP BY server_id) latest
        ON sc.id = latest.mid
    """).fetchall()
    conn.close()

    if not rows:
        st.info("No probe data yet. Click \"Probe All Servers\" to collect the conformance matrix.")
        return

    st.divider()
    st.subheader("Version & Capability Matrix")

    table_rows = []
    for r in rows:
        data = json.loads(r["capabilities_json"] or "{}")
        caps = data.get("capabilities", {})
        gen_badge = {"stateless": "🆕 stateless", "session": "🔗 session",
                     "unknown": "❓ unknown", "probe_failed": "💥 failed"}.get(r["generation"], r["generation"])
        row = {
            "Server": r["server_name"],
            "Protocol Version": r["protocol_version"] or "-",
            "Generation": gen_badge,
        }
        for k in CAP_KEYS:
            row[k.capitalize()] = "✅" if caps.get(k) else "—"
        table_rows.append(row)

    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Spec Timeline Reference")
    st.markdown(f"""
    | Version | Era | Key Features |
    |---------|-----|--------------|
    | 2024-11-05 | session | Original release: stdio + HTTP+SSE |
    | 2025-03-26 | session | Tool result domains |
    | 2025-06-18 | session | OAuth 2.1, Streamable HTTP, structured output |
    | 2025-11-25 | session | Tasks, elicitation, resource cache control |
    | **2026-07-28** | **stateless** | **Handshake & sessions removed; per-request metadata** |

    FN-001 adapts automatically: for `{STATELESS_CORE_VERSION}`+ servers the absence of an
    initialize handshake is compliant behavior, not a failure. FN-008 requires the declared
    version to be in the known set {KNOWN_PROTOCOL_VERSIONS}.
    """)


def _init_conformance_table():
    from core.results_store import get_db
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS spec_conformance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        server_name TEXT,
        protocol_version TEXT,
        generation TEXT,
        capabilities_json TEXT,
        probed_at TEXT
    )
    """)
    conn.commit()
    conn.close()
