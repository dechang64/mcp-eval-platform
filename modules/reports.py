"""模块5: 报告详情"""
import streamlit as st
import json

def render():
    from core.results_store import list_runs, get_run_results, get_run
    from modules.utils import status_badge, fmt_duration, fmt_timestamp

    st.header("📝 报告详情")

    runs = list_runs(limit=20)
    if not runs:
        st.info("暂无测试运行记录")
        return

    run_ids = [f"#{r['id']} - {r['server_name']} ({fmt_timestamp(r['started_at'])})" for r in runs]
    selected = st.selectbox("选择测试运行", run_ids)
    run_idx = run_ids.index(selected)
    run = runs[run_idx]

    run_detail = get_run(run["id"])
    results = get_run_results(run["id"])

    # Summary
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Server", run["server_name"])
    col2.metric("套件", run["suite_type"])
    col3.metric("状态", status_badge(run["status"]))
    col4.metric("通过/总计", f"{run['passed']}/{run['total_cases']}")
    col5.metric("耗时", f"{run['duration_sec']:.1f}s" if run["duration_sec"] else "-")

    st.divider()

    if not results:
        st.warning("无详细结果数据（可能测试启动失败）")
        return

    # Overall score card
    from core.scoring import compute_score, grade_color
    score = compute_score(results)
    sc1, sc2, sc3, sc4, sc5 = st.columns([1, 1, 1, 1, 2])
    sc1.metric("综合评级", score.letter, f"{score.overall:.0f}分")
    sc2.metric("功能", f"{score.functional:.0f}%")
    sc3.metric("性能", f"{score.performance:.0f}%")
    sc4.metric("安全", f"{score.security:.0f}%")
    sc5.markdown(f"**评语**：{score.summary}")

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

    st.subheader("分类统计")
    cols = st.columns(len(cats)) if cats else [st.container()]
    for i, (cat, data) in enumerate(cats.items()):
        cols[i].metric(cat, f"{data['passed']}/{data['total']}", f"{data['passed']/data['total']*100:.0f}%")

    st.divider()

    # Detailed results
    st.subheader("详细结果")
    for r in results:
        icon = {"passed": "✅", "failed": "❌", "skipped": "⏭️", "error": "💥"}.get(r["status"], "❓")
        title = f"{icon} {r['case_id']} - {r['case_name']} ({r['category']})"
        with st.expander(title):
            col1, col2 = st.columns([1, 3])
            col1.markdown(f"**状态**: {r['status']}")
            col1.markdown(f"**耗时**: {fmt_duration(r['duration_ms'])}")
            col1.markdown(f"**类别**: {r['category']}")
            if r.get("error_msg"):
                col2.markdown("**错误信息**")
                col2.code(r["error_msg"])
            if r.get("detail"):
                try:
                    col2.markdown("**详情**")
                    col2.json(json.loads(r["detail"]) if isinstance(r["detail"], str) else r["detail"])
                except Exception:
                    pass
