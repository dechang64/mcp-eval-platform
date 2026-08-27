"""Module 5: Reports"""
import streamlit as st
import json

def render():
    from core.results_store import list_runs, get_run_results, get_run
    from modules.utils import status_badge, fmt_duration, fmt_timestamp

    st.header("📝 Reports")

    runs = list_runs(limit=20)
    if not runs:
        st.info("No test runs yet")
        return

    run_ids = [f"#{r['id']} - {r['server_name']} ({fmt_timestamp(r['started_at'])})" for r in runs]
    selected = st.selectbox("Select test run", run_ids)
    run_idx = run_ids.index(selected)
    run = runs[run_idx]

    run_detail = get_run(run["id"])
    results = get_run_results(run["id"])

    # Export button
    from core.report_export import export_run_markdown
    try:
        from core.scoring import compute_score as _cs
        _score = _cs(results) if results else None
    except Exception:
        _score = None
    _md = export_run_markdown(run, results, _score)
    st.download_button(
        "📥 Export Markdown Report",
        data=_md,
        file_name=f"mcp_eval_run_{run['id']}_{run['server_name']}.md",
        mime="text/markdown",
    )

    # Summary
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Server", run["server_name"])
    col2.metric("Suite", run["suite_type"])
    col3.metric("Status", status_badge(run["status"]))
    col4.metric("Passed/Total", f"{run['passed']}/{run['total_cases']}")
    col5.metric("Duration", f"{run['duration_sec']:.1f}s" if run["duration_sec"] else "-")

    st.divider()

    if not results:
        st.warning("No detailed result data (test may have failed to start)")
        return

    # Overall score card
    from core.scoring import compute_score, grade_color
    score = compute_score(results)
    sc1, sc2, sc3, sc4, sc5 = st.columns([1, 1, 1, 1, 2])
    sc1.metric("Overall Grade", score.letter, f"{score.overall:.0f}")
    sc2.metric("Functional", f"{score.functional:.0f}%")
    sc3.metric("Performance", f"{score.performance:.0f}%")
    sc4.metric("Security", f"{score.security:.0f}%")
    sc5.markdown(f"**Summary**: {score.summary}")

    st.divider()

    # Category breakdown
    cats = {}
    for r in results:
        cat = r["category"]
        if cat not in cats:
            cats[cat] = {"total": 0, "passed": 0, "failed": 0}
        cats[cat]["total"] += 1
        if r["status"] == "passed":
            cats[cat]["passed"] += 1
        elif r["status"] == "failed":
            cats[cat]["failed"] += 1

    st.subheader("Category Breakdown")
    cols = st.columns(len(cats)) if cats else [st.container()]
    for i, (cat, data) in enumerate(cats.items()):
        cols[i].metric(cat, f"{data['passed']}/{data['total']}", f"{data['passed']/data['total']*100:.0f}%")

    st.divider()

    # Detailed results
    st.subheader("Detailed Results")
    for r in results:
        icon = {"passed": "✅", "failed": "❌", "skipped": "⏭️", "error": "💥"}.get(r["status"], "❓")
        title = f"{icon} {r['case_id']} - {r['case_name']} ({r['category']})"
        with st.expander(title):
            col1, col2 = st.columns([1, 3])
            col1.markdown(f"**Status**: {r['status']}")
            col1.markdown(f"**Duration**: {fmt_duration(r['duration_ms'])}")
            col1.markdown(f"**Category**: {r['category']}")
            if r.get("error_msg"):
                col2.markdown("**Error**")
                col2.code(r["error_msg"])
            if r.get("detail"):
                try:
                    col2.markdown("**Detail**")
                    col2.json(json.loads(r["detail"]) if isinstance(r["detail"], str) else r["detail"])
                except Exception:
                    pass
