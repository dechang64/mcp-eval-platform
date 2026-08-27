"""模块6: 横向对比"""
import streamlit as st
import json

def render():
    from core.results_store import list_servers, list_runs, get_run_results, get_run
    from modules.utils import status_badge, fmt_duration

    st.header("🔄 横向对比")

    servers = list_servers()
    if len(servers) < 2:
        st.info("至少需要2个Server才能进行横向对比")
        return

    # Select 2+ servers
    server_names = [s["name"] for s in servers]
    selected = st.multiselect("选择Server（至少2个）", server_names, default=server_names[:2])

    if len(selected) < 2:
        st.warning("请选择至少2个Server")
        return

    # For each server, find latest run
    col_headers = ["指标"] + selected
    rows = []

    # Pass rates
    pass_row = ["通过率"]
    latency_row = ["P95延迟"]
    func_row = ["功能通过率"]
    sec_row = ["安全通过率"]
    perf_row = ["性能通过率"]

    for sname in selected:
        server = next(s for s in servers if s["name"] == sname)
        runs = list_runs(server_id=server["id"], limit=1)
        if not runs:
            pass_row.append("无数据")
            latency_row.append("无数据")
            func_row.append("无数据")
            sec_row.append("无数据")
            perf_row.append("无数据")
            continue

        run = runs[0]
        results = get_run_results(run["id"])
        total = len(results)
        passed = sum(1 for r in results if r["status"] == "passed")

        if total == 0:
            pass_row.append("0%")
        else:
            pass_row.append(f"{passed/total*100:.0f}%")

        # Per category
        for cat, row in [("functional", func_row), ("security", sec_row), ("performance", perf_row)]:
            cat_results = [r for r in results if r["category"] == cat]
            if not cat_results:
                row.append("-")
            else:
                cat_pass = sum(1 for r in cat_results if r["status"] == "passed")
                row.append(f"{cat_pass}/{len(cat_results)}")

        # P95 latency from performance cases
        perf_results = [r for r in results if r["category"] == "performance" and r["status"] == "passed"]
        if perf_results:
            latencies = []
            for r in perf_results:
                try:
                    detail = json.loads(r["detail"]) if isinstance(r["detail"], str) else r["detail"]
                    if "latencies_ms" in detail:
                        latencies.extend(detail["latencies_ms"])
                except Exception:
                    pass
            if latencies:
                sorted_l = sorted(latencies)
                p95_idx = int(len(sorted_l) * 0.95)
                latency_row.append(fmt_duration(sorted_l[p95_idx]))
            else:
                latency_row.append("-")
        else:
            latency_row.append("-")

    rows = [pass_row, func_row, sec_row, perf_row, latency_row]

    st.subheader("对比表")
    st.table(rows)

    st.divider()

    # Bar chart - pass rate comparison
    st.subheader("通过率对比")
    chart_data = {"Server": selected, "通过率": []}
    for r in rows[0][1:]:
        try:
            chart_data["通过率"].append(float(r.replace("%", "")))
        except Exception:
            chart_data["通过率"].append(0)
    st.bar_chart(chart_data, x="Server", y="通过率")
