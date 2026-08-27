"""模块4: 测试运行"""
import streamlit as st
import json
import time
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def render():
    from core.results_store import list_servers, get_server, save_run, list_runs
    from core.mcp_client import McpClient, McpServerConfig
    from core.test_runner import run_suite, load_suites
    from modules.utils import status_badge, fmt_timestamp

    st.header("▶️ 测试运行")

    servers = list_servers()
    if not servers:
        st.warning("请先在「Server管理」中注册MCP Server")
        return

    # Select server
    server_names = [s["name"] for s in servers]
    selected_name = st.selectbox("选择MCP Server", server_names)
    selected_server = next(s for s in servers if s["name"] == selected_name)

    # Select suite
    suite_type = st.selectbox("测试套件", ["all", "functional", "performance", "security"],
                              format_func=lambda x: {"all": "全部", "functional": "功能", "performance": "性能", "security": "安全"}[x])

    # Config
    config = json.loads(selected_server["config_json"])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Server信息**")
        st.json({
            "name": selected_server["name"],
            "transport": selected_server["transport"],
            "command": config.get("command", ""),
            "url": config.get("url", ""),
            "description": selected_server.get("description", ""),
        })
    with col2:
        suites = load_suites()
        counts = {k: len(v) for k, v in suites.items()}
        st.markdown("**套件用例数**")
        st.json(counts)

    # Run button
    if st.button("🚀 开始测试", type="primary"):
        # Build config
        mc = McpServerConfig(
            name=selected_server["name"],
            transport=selected_server["transport"],
            command=config.get("command", ""),
            args=config.get("args", []),
            env=config.get("env", {}),
            url=config.get("url", ""),
        )

        progress = st.progress(0, text="正在连接MCP Server...")
        status_area = st.empty()

        async def execute():
            client = McpClient(mc)
            try:
                await client.connect()
                progress.progress(10, text="已连接，开始测试...")

                results = await run_suite(client, suite_type)
                progress.progress(80, text="测试完成，保存结果...")

                total = len(results)
                passed = sum(1 for r in results if r.status == "passed")
                failed = sum(1 for r in results if r.status == "failed")
                errors = sum(1 for r in results if r.status == "error")

                status = "passed" if failed == 0 and errors == 0 else "failed"
                run_data = {
                    "server_id": selected_server["id"],
                    "server_name": selected_server["name"],
                    "suite_type": suite_type,
                    "total_cases": total,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "status": status,
                }
                run_id = save_run(run_data, [r.__dict__ for r in results])
                progress.progress(100, text=f"测试完成！Run ID: {run_id}")

                return run_id, results

            except Exception as e:
                # Save as error run
                run_data = {
                    "server_id": selected_server["id"],
                    "server_name": selected_server["name"],
                    "suite_type": suite_type,
                    "total_cases": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 1,
                    "status": "error",
                }
                run_id = save_run(run_data, [])
                progress.progress(100, text=f"测试失败: {e}")
                return run_id, []

            finally:
                try:
                    await client.close()
                except Exception:
                    pass

        run_id, results = asyncio.run(execute())

        if results:
            st.success(f"测试完成！Run ID: {run_id}")
            st.markdown(f"**通过**: {sum(1 for r in results if r.status == 'passed')} | "
                        f"**失败**: {sum(1 for r in results if r.status == 'failed')} | "
                        f"**错误**: {sum(1 for r in results if r.status == 'error')}")

            # Show results table
            rows = []
            for r in results:
                rows.append({
                    "ID": r.case_id,
                    "用例": r.case_name,
                    "类别": r.category,
                    "状态": status_badge(r.status),
                    "耗时": f"{r.duration_ms:.0f}ms",
                    "详情": r.error_msg[:80] if r.error_msg else "",
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)

    # Recent runs
    st.divider()
    st.subheader("最近运行")
    runs = list_runs(limit=5)
    if runs:
        for r in runs:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            col1.markdown(f"**{r['server_name']}** - Run #{r['id']}")
            col2.markdown(status_badge(r["status"]))
            col3.markdown(f"{r['passed']}/{r['total_cases']}")
            col4.caption(fmt_timestamp(r["started_at"]))
