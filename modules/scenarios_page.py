"""Module 8: Scenario Testing - multi-tool workflows + LLM Agent loop"""
import asyncio
import json
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def render():
    from core.results_store import list_servers, get_db
    from core.mcp_client import McpClient, McpServerConfig
    from core.agent_scenarios import run_all_scenarios, BUILTIN_SCENARIOS
    from core.agent_loop import run_agent_loop, builtin_agent_tasks
    from modules.utils import fmt_timestamp

    st_header_scenarios()


def st_header_scenarios():
    import streamlit as st
    st.header("🎬 Scenario Testing")
    st.caption("Multi-tool collaborative workflows: data written by one step must be readable by the next. Verifies cross-tool state consistency and LLM autonomous planning.")

    _init_scenario_tables()

    tab1, tab2 = st.tabs(["📋 Builtin Scenarios", "🤖 LLM Agent Loop"])

    with tab1:
        _render_scenario_tab()
    with tab2:
        _render_agent_tab()


def _render_scenario_tab():
    import streamlit as st
    from core.results_store import list_servers

    servers = list_servers()
    if not servers:
        st.warning("Register an MCP Server in Server Manager first")
        return

    from core.agent_scenarios import BUILTIN_SCENARIOS
    st.subheader("Builtin Scenarios")
    for factory in BUILTIN_SCENARIOS:
        sc = factory()
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"**{sc.name}** — {sc.description}")
        c2.caption(f"Requires {len(sc.required_tools)} tools")

    server_names = [s["name"] for s in servers]
    selected = st.selectbox("Select MCP Server", server_names, key="scen_server")
    s = next(x for x in servers if x["name"] == selected)

    if st.button("🚀 Run Scenario Suite", key="run_scen"):
        _run_scenarios(s)

    _render_scenario_history()


def _run_scenarios(server: dict):
    import streamlit as st
    from core.mcp_client import McpClient, McpServerConfig
    from core.agent_scenarios import run_all_scenarios

    progress = st.progress(0, text="Connecting to server...")
    cfg = McpServerConfig.from_dict(json.loads(server["config_json"]))

    async def _run():
        client = McpClient(cfg)
        await client.connect()
        results = await run_all_scenarios(client)
        await client.close()
        return results

    try:
        results = asyncio.run(_run())
        total = len(results)
        passed = sum(1 for r in results if r.status == "passed")

        rows = []
        for r in results:
            rows.append({
                "Scenario": r.name, "Status": {"passed": "✅", "failed": "❌", "skipped": "⏭️"}.get(r.status, "❓"),
                "Steps": f"{r.passed_steps}/{len(r.steps)}", "Duration": f"{r.duration_ms:.0f}ms",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

        for r in results:
            if r.status == "skipped":
                st.caption(f"⏭️ {r.name}: required tools missing, skipped")
                continue
            icon = "✅" if r.status == "passed" else "❌"
            with st.expander(f"{icon} {r.name} ({r.passed_steps}/{len(r.steps)} steps)"):
                for i, s in enumerate(r.steps, 1):
                    mark = "·" if s.ok else "×"
                    st.markdown(f"`{mark}` **Step {i}** `{s.tool}` ({s.duration_ms:.0f}ms) — {s.message or 'OK'}")
                    if s.args:
                        st.json(s.args)
                    if s.response_snippet and not s.ok:
                        st.code(s.response_snippet)

        _save_scenario_run(server, results)
        st.success(f"Scenario suite finished: {passed}/{total} passed, saved to database")

    except Exception as e:
        st.error(f"Scenario testing failed: {e}")


def _render_agent_tab():
    import streamlit as st
    from core.results_store import list_servers
    from core.agent_loop import builtin_agent_tasks

    servers = list_servers()
    if not servers:
        st.warning("Register an MCP Server in Server Manager first")
        return

    tasks = builtin_agent_tasks()
    task_names = [t["name"] for t in tasks]
    tn = st.selectbox("Composite Task", task_names, key="agent_task")
    task_def = next(t for t in tasks if t["name"] == tn)
    st.info(task_def["task"])

    server_names = [s["name"] for s in servers]
    selected = st.selectbox("Select MCP Server", server_names, key="agent_server")
    s = next(x for x in servers if x["name"] == selected)

    max_rounds = st.slider("Max loop rounds", 4, 15, 8)

    if st.button("🤖 Start Agent Loop", key="run_agent"):
        _run_agent(s, task_def, max_rounds)

    _render_agent_history()


def _run_agent(server, task_def, max_rounds):
    import streamlit as st
    from core.mcp_client import McpClient, McpServerConfig
    from core.agent_loop import run_agent_loop

    progress = st.progress(0, text="Agent planning...")
    cfg = McpServerConfig.from_dict(json.loads(server["config_json"]))

    async def _run():
        client = McpClient(cfg)
        await client.connect()
        result = await run_agent_loop(client, task_def["task"], task_def["end_probes"], max_rounds)
        await client.close()
        return result

    try:
        result = asyncio.run(_run())
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("End-State Check", "✅ Passed" if result.completed else "❌ Failed")
        c2.metric("Tool Calls", len(result.steps))
        c3.metric("Grade", result.grade)
        c4.metric("Duration", f"{result.duration_ms:.0f}ms")

        for s in result.steps:
            icon = "✅" if s.ok else "❌"
            with st.expander(f"{icon} Round {s.round_no}: {s.tool}"):
                st.json(s.args)
                st.code(s.response_snippet)

        st.markdown(f"**Done reason**: {result.done_reason} | **End state**: {result.end_check_msg}")
        _save_agent_run(server, task_def, result)
        st.success("Agent loop finished, saved to database")

    except Exception as e:
        st.error(f"Agent loop failed: {e}")


def _init_scenario_tables():
    from core.results_store import get_db
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS scenario_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        server_name TEXT,
        total INTEGER, passed INTEGER,
        details_json TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS agent_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        server_name TEXT,
        task_name TEXT,
        completed INTEGER,
        rounds INTEGER,
        steps_json TEXT,
        grade TEXT,
        created_at TEXT
    );
    """)
    conn.commit()
    conn.close()


def _save_scenario_run(server, results):
    from core.results_store import get_db
    conn = get_db()
    total = len(results)
    passed = sum(1 for r in results if r.status == "passed")
    details = [{
        "name": r.name, "status": r.status, "duration_ms": r.duration_ms,
        "steps": [{
            "tool": s.tool, "args": s.args if isinstance(s.args, dict) else {},
            "ok": s.ok, "message": s.message, "duration_ms": s.duration_ms,
        } for s in r.steps],
    } for r in results]
    conn.execute(
        "INSERT INTO scenario_runs (server_id, server_name, total, passed, details_json, created_at) VALUES (?,?,?,?,?,?)",
        (server["id"], server["name"], total, passed, json.dumps(details, ensure_ascii=False), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def _save_agent_run(server, task_def, result):
    from core.results_store import get_db
    conn = get_db()
    steps = [{
        "round_no": s.round_no, "tool": s.tool, "args": s.args,
        "ok": s.ok, "response": s.response_snippet,
    } for s in result.steps]
    conn.execute(
        "INSERT INTO agent_runs (server_id, server_name, task_name, completed, rounds, steps_json, grade, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (server["id"], server["name"], task_def["name"], int(result.completed),
         result.rounds_used, json.dumps(steps, ensure_ascii=False), result.grade,
         datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def _render_scenario_history():
    import streamlit as st
    from core.results_store import get_db
    st.subheader("Scenario Run History")
    conn = get_db()
    rows = conn.execute("SELECT id, server_name, passed, total, created_at FROM scenario_runs ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    if not rows:
        st.caption("No history yet")
        return
    st.dataframe([{
        "ID": r["id"], "Server": r["server_name"],
        "Passed": f"{r['passed']}/{r['total']}", "Time": r["created_at"][:19],
    } for r in rows], use_container_width=True, hide_index=True)


def _render_agent_history():
    import streamlit as st
    from core.results_store import get_db
    st.subheader("Agent Run History")
    conn = get_db()
    rows = conn.execute("SELECT id, server_name, task_name, completed, rounds, grade, created_at FROM agent_runs ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    if not rows:
        st.caption("No history yet")
        return
    st.dataframe([{
        "ID": r["id"], "Server": r["server_name"], "Task": r["task_name"],
        "End-State": "✅" if r["completed"] else "❌", "Rounds": r["rounds"],
        "Grade": r["grade"], "Time": r["created_at"][:19],
    } for r in rows], use_container_width=True, hide_index=True)
