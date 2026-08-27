"""Module 1: Dashboard"""
import streamlit as st
import json

def render():
    from core.results_store import get_dashboard_stats
    from modules.utils import status_badge, fmt_timestamp

    st.header("📊 Dashboard")

    stats = get_dashboard_stats()

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registered Servers", stats["servers"])
    col2.metric("Test Runs", stats["runs"])
    col3.metric("Passed Runs", stats["passed_runs"])
    pass_rate = (stats["passed_cases"] / stats["total_cases"] * 100) if stats["total_cases"] > 0 else 0
    col4.metric("Case Pass Rate", f"{pass_rate:.1f}%")

    st.divider()

    # Recent runs
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

    st.divider()

    # Quick start guide
    st.subheader("Quick Start")
    st.markdown("""
    1. **Server Manager** → Register an MCP Server (stdio or SSE)
    2. **Test Suites** → Browse functional / performance / security test cases
    3. **Test Runs** → Pick a server and suite, run with one click
    4. **Reports** → Inspect detailed results and export Markdown
    5. **Comparison** → Cross-server benchmark analysis
    """)
