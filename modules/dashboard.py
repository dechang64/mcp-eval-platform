"""模块1: 仪表板"""
import streamlit as st
import json

def render():
    from core.results_store import get_dashboard_stats
    from modules.utils import status_badge, fmt_timestamp

    st.header("📊 仪表板")

    stats = get_dashboard_stats()

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("已注册Server", stats["servers"])
    col2.metric("测试运行次数", stats["runs"])
    col3.metric("通过的运行", stats["passed_runs"])
    pass_rate = (stats["passed_cases"] / stats["total_cases"] * 100) if stats["total_cases"] > 0 else 0
    col4.metric("用例通过率", f"{pass_rate:.1f}%")

    st.divider()

    # Recent runs
    st.subheader("最近测试运行")
    if not stats["recent_runs"]:
        st.info("暂无测试运行记录。前往「Server管理」注册MCP Server后开始测试。")
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
                "套件": r["suite_type"],
                "状态": status_badge(r["status"]),
                "评级": grade,
                "通过/总计": f"{r['passed']}/{r['total_cases']}",
                "耗时": f"{r['duration_sec']:.1f}s" if r["duration_sec"] else "-",
                "时间": fmt_timestamp(r["started_at"]),
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

    st.divider()

    # Quick start guide
    st.subheader("快速开始")
    st.markdown("""
    1. **Server管理** → 添加MCP Server（stdio或SSE）
    2. **测试套件** → 查看功能/性能/安全测试用例
    3. **测试运行** → 选择Server和套件，一键执行
    4. **报告详情** → 查看详细结果
    5. **横向对比** → 多Server对比分析
    """)
