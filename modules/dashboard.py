"""Module 1: Dashboard"""
import streamlit as st
import json

def render():
    from core.results_store import get_dashboard_stats, get_db
    from modules.utils import status_badge, fmt_timestamp

    st.header("📊 Dashboard")

    stats = get_dashboard_stats()

    # Row 1: standard suite KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registered Servers", stats["servers"])
    col2.metric("Test Runs", stats["runs"])
    col3.metric("Passed Runs", stats["passed_runs"])
    pass_rate = (stats["passed_cases"] / stats["total_cases"] * 100) if stats["total_cases"] > 0 else 0
    col4.metric("Case Pass Rate", f"{pass_rate:.1f}%")

    # Row 2: cross-dimension KPIs
    conn = get_db()
    llm_runs = conn.execute("SELECT COUNT(*) c, AVG(tool_accuracy) acc FROM llm_runs").fetchone()
    llm_results = conn.execute("""
        SELECT COUNT(*) total, SUM(tool_correct) tool_ok FROM llm_results""").fetchone()
    scen_runs = conn.execute("SELECT COUNT(*) c FROM scenario_runs").fetchone()
    agent_runs = conn.execute("SELECT COUNT(*) c, SUM(completed) done FROM agent_runs").fetchone()
    conn.close()

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("LLM Compat Runs", llm_runs["c"] or 0,
                f"{(llm_results['tool_ok'] or 0)}/{llm_results['total'] or 0} tool selections correct" if llm_results["total"] else None)
    tool_acc = (llm_results["tool_ok"] / llm_results["total"] * 100) if llm_results["total"] else 0
    col6.metric("Tool Selection Accuracy", f"{tool_acc:.0f}%")
    col7.metric("Scenario Runs", scen_runs["c"] or 0)
    col8.metric("Agent Tasks Completed", f"{agent_runs['done'] or 0}/{agent_runs['c'] or 0}")

    st.divider()

    # Recent runs (with grades)
    st.subheader("Recent Test Runs")
    if not stats["recent_runs"]:
        st.info("No test runs yet. Register an MCP Server in Server Manager to get started.")
    else:
        from core.results_store import get_run_results
        from core.scoring import compute_score
        rows = []
        for r in stats["recent_runs"]:
            try:
                results = get_run_results(r["id"])
                score = compute_score(results) if results else None
                grade = f"{score.letter} ({score.overall:.0f})" if score else "-"
            except Exception:
                grade = "-"
            rows.append({
                "ID": r["id"],
                "Server": r["server_name"],
                "Suite": r["suite_type"],
                "Status": status_badge(r["status"]),
                "Grade": grade,
                "Passed/Total": f"{r['passed']}/{r['total_cases']}",
                "Duration": f"{r['duration_sec']:.1f}s" if r["duration_sec"] else "-",
                "Time": fmt_timestamp(r["started_at"]),
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

    # Latest cross-dimension snapshot
    st.subheader("Cross-Dimension Snapshot (latest run per server)")
    try:
        conn = get_db()
        server_ids = [s["id"] for s in __import__("core.results_store", fromlist=["list_servers"]).list_servers()]
        snap_rows = []
        for sid in server_ids:
            r1 = conn.execute("SELECT server_name, overall, grade FROM llm_runs WHERE server_id=? ORDER BY id DESC LIMIT 1", (sid,)).fetchone()
            r2 = conn.execute("SELECT passed, total, details_json FROM scenario_runs WHERE server_id=? ORDER BY id DESC LIMIT 1", (sid,)).fetchone()
            r3 = conn.execute("SELECT protocol_version, generation FROM spec_conformance WHERE server_id=? ORDER BY id DESC LIMIT 1", (sid,)).fetchone()
            if not (r1 or r2 or r3):
                continue
            name = (r1["server_name"] if r1 else None) or (dict(r2) and None)
            scen_txt = "-"
            if r2:
                try:
                    details = json.loads(r2["details_json"] or "[]")
                    app = sum(1 for d in details if d.get("status") != "skipped")
                    passed = sum(1 for d in details if d.get("status") == "passed")
                    scen_txt = f"{passed}/{app}"
                except Exception:
                    scen_txt = f"{r2['passed']}/{r2['total']}"
            snap_rows.append({
                "Server": (r1 or {}).get("server_name") if r1 else f"#{sid}",
                "LLM Compat": f"{r1['overall']:.0f} ({r1['grade']})" if r1 else "-",
                "Scenarios (applicable)": scen_txt,
                "Protocol": f"{r3['protocol_version']} ({r3['generation']})" if r3 else "-",
            })
        conn.close()
        if snap_rows:
            st.dataframe(snap_rows, use_container_width=True, hide_index=True)
        else:
            st.caption("No LLM compatibility / scenario runs yet.")
    except Exception as e:
        st.caption(f"Snapshot unavailable: {e}")

    st.divider()

    # Quick start guide
    st.subheader("Quick Start")
    st.markdown("""
    1. **Server Manager** → Register an MCP Server (stdio or SSE)
    2. **Test Suites** → Browse functional / performance / security test cases
    3. **Test Runs** → Pick a server and suite, run with one click
    4. **LLM Compatibility / Scenario Testing** → Semantic and behavioral dimensions
    5. **Spec Conformance** → Protocol version & capability matrix
    6. **Reports / Comparison** → Export Markdown, five-dimension benchmark
    """)
