"""模块7: LLM兼容性测试

让真实LLM阅读被测Server的工具描述，测试：
  1. 工具选择准确率（LLM能否选对工具）
  2. 参数填充合规率（LLM填的参数能否通过schema校验）
"""
import streamlit as st
import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def render():
    from core.results_store import list_servers, get_db, DB_PATH
    from core.mcp_client import McpClient, McpServerConfig
    from modules.utils import fmt_timestamp

    st.header("🤖 LLM兼容性测试")
    st.caption("让真实LLM阅读工具描述并执行任务——检验Server的\"LLM可理解性\"。依赖 z-ai CLI + glm-4-plus。")

    # Init llm tables
    _init_llm_tables()

    servers = list_servers()
    if not servers:
        st.warning("请先在「Server管理」中注册MCP Server")
        return

    server_names = [s["name"] for s in servers]
    selected_name = st.selectbox("选择MCP Server", server_names)
    selected_server = next(s for s in servers if s["name"] == selected_name)
    max_tools = st.slider("最多测试工具数", 3, 20, 14, help="工具多时LLM任务生成和执行时间长")

    if st.button("🚀 生成任务并测试", type="primary", use_container_width=True):
        _run_llm_compat(selected_server, max_tools)

    st.divider()

    # History
    st.subheader("历史LLM兼容性测试")
    runs = _list_llm_runs()
    if not runs:
        st.info("暂无LLM兼容性测试记录")
        return
    for r in runs:
        col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
        col1.markdown(f"**{r['server_name']}** (Run #{r['id']})")
        grade_color = {"A+": "green", "A": "green", "B": "blue", "C": "orange", "D": "red"}.get(r["grade"], "gray")
        col2.markdown(f":{grade_color}[**{r['grade']}** ({r['overall']:.0f}分)]")
        col3.caption(f"工具选择 {r['tool_correct']}/{r['total']}")
        col4.caption(f"参数合规 {r['args_valid']}/{r['total']}")
        col5.caption(fmt_timestamp(r["created_at"]))

        with st.expander(f"明细 - Run #{r['id']}"):
            results = _get_llm_results(r["id"])
            rows = []
            for x in results:
                mark = "✅" if x["tool_correct"] and x["args_valid"] else ("⚠️" if x["tool_correct"] else "❌")
                rows.append({
                    "预期工具": x["tool_name"],
                    "LLM选择": x["llm_tool"],
                    "任务": x["task"][:50],
                    "选对": "✅" if x["tool_correct"] else "❌",
                    "参数合规": "✅" if x["args_valid"] else f"❌ {x['args_error'][:40]}",
                    "状态": mark,
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)


def _init_llm_tables():
    from core.results_store import get_db
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS llm_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER NOT NULL,
        server_name TEXT NOT NULL,
        model TEXT DEFAULT 'glm-4-plus',
        total INTEGER DEFAULT 0,
        tool_correct INTEGER DEFAULT 0,
        args_valid INTEGER DEFAULT 0,
        tool_accuracy REAL DEFAULT 0,
        args_valid_rate REAL DEFAULT 0,
        overall REAL DEFAULT 0,
        grade TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS llm_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        tool_name TEXT, task TEXT, llm_tool TEXT,
        tool_correct INTEGER DEFAULT 0,
        llm_args_json TEXT DEFAULT '{}',
        args_valid INTEGER DEFAULT 0,
        args_error TEXT DEFAULT '',
        duration_ms REAL DEFAULT 0,
        FOREIGN KEY(run_id) REFERENCES llm_runs(id)
    );
    """)
    conn.commit()
    conn.close()


def _run_llm_compat(server: dict, max_tools: int):
    from core.mcp_client import McpClient, McpServerConfig
    from core.llm_compat import generate_tasks, run_selection, summarize
    from core.results_store import get_db
    from modules.utils import run_async
    from datetime import datetime

    progress = st.progress(0, text="连接MCP Server...")
    try:
        cfg = McpServerConfig.from_dict(json.loads(server["config_json"]))
        client = McpClient(cfg)
        run_async(client.connect())
        tools = run_async(client.list_tools())
        run_async(client.close())
        progress.progress(10, text=f"已获取 {len(tools)} 个工具，正在生成测试任务...")

        tasks = generate_tasks(tools, max_tools=max_tools)
        progress.progress(30, text=f"已生成 {len(tasks)} 个任务，开始LLM测试（每个任务一次LLM调用）...")

        # 逐任务执行，更新进度
        results = []
        from core.llm_compat import llm_call, extract_json, _type_ok, SELECT_SYSTEM, build_tool_catalog
        catalog = build_tool_catalog(tools)
        tool_map = {t.name: t for t in tools}
        for i, task_item in enumerate(tasks):
            task = task_item["task"]
            expected_tool = task_item["tool"]
            start = time.time()
            prompt = f"""你可以调用以下MCP工具：

{catalog}

用户说："{task}"

你应该调用哪个工具？如何填参数？
只输出JSON：{{"tool": "工具名", "arguments": {{...}}}}"""
            try:
                reply = llm_call(prompt, SELECT_SYSTEM)
                data = extract_json(reply) or {}
                llm_tool = data.get("tool", "")
                llm_args = data.get("arguments", {})
                if not isinstance(llm_args, dict):
                    llm_args = {}
            except Exception as e:
                llm_tool, llm_args = "", {}
                tool_correct, args_valid = False, False
                args_error = f"LLM调用失败: {str(e)[:80]}"
                results.append(_mk_result(expected_tool, task, llm_tool, llm_args, tool_correct, args_valid, args_error, start))
                progress.progress(30 + int(60 * (i + 1) / len(tasks)), text=f"[{i+1}/{len(tasks)}] {task[:30]}...")
                continue

            tool_correct = (llm_tool == expected_tool)
            args_error = ""
            args_valid = True
            if tool_correct:
                t = tool_map[expected_tool]
                schema = t.input_schema or {}
                required = schema.get("required", [])
                missing = [r for r in required if r not in llm_args]
                if missing:
                    args_valid = False
                    args_error = f"缺少必填参数: {missing}"
                props = schema.get("properties", {})
                for k, v in llm_args.items():
                    if k in props and not _type_ok(v, props[k].get("type")):
                        args_valid = False
                        args_error += f"参数{k}类型错误 "
            else:
                args_error = f"选错工具: 期望{expected_tool}, 实际{llm_tool}"
            results.append(_mk_result(expected_tool, task, llm_tool, llm_args, tool_correct, args_valid, args_error, start))
            progress.progress(30 + int(60 * (i + 1) / len(tasks)), text=f"[{i+1}/{len(tasks)}] {task[:30]}...")

        progress.progress(95, text="汇总评分...")

        # 汇总+存库
        from core.llm_compat import CompatResult, summarize
        compat_results = [CompatResult(**r) for r in results]
        s = summarize(compat_results)

        conn = get_db()
        now = datetime.now().isoformat()
        cur = conn.execute(
            "INSERT INTO llm_runs (server_id, server_name, model, total, tool_correct, args_valid, tool_accuracy, args_valid_rate, overall, grade, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (server["id"], server["name"], "glm-4-plus", s.total,
             sum(1 for r in results if r["tool_correct"]),
             sum(1 for r in results if r["tool_correct"] and r["args_valid"]),
             s.tool_accuracy, s.args_valid_rate, s.overall, s.grade, now),
        )
        rid = cur.lastrowid
        for r in results:
            conn.execute(
                "INSERT INTO llm_results (run_id, tool_name, task, llm_tool, tool_correct, llm_args_json, args_valid, args_error, duration_ms) VALUES (?,?,?,?,?,?,?,?,?)",
                (rid, r["tool_name"], r["task"], r["llm_tool"], int(r["tool_correct"]),
                 json.dumps(r["llm_args"], ensure_ascii=False), int(r["args_valid"]), r["args_error"], r["duration_ms"]),
            )
        conn.commit()
        conn.close()

        progress.progress(100, text=f"完成！Run #{rid}")

        # 显示结果
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("综合评级", s.grade, f"{s.overall:.0f}分")
        c2.metric("工具选择准确率", f"{s.tool_accuracy:.0f}%")
        c3.metric("参数合规率", f"{s.args_valid_rate:.0f}%")
        c4.metric("测试工具数", s.total)
        st.rerun()

    except Exception as e:
        progress.progress(100, text=f"测试失败: {e}")
        st.error(f"LLM兼容性测试失败: {e}")


def _mk_result(expected_tool, task, llm_tool, llm_args, tool_correct, args_valid, args_error, start):
    return {
        "tool_name": expected_tool, "task": task, "llm_tool": llm_tool,
        "tool_correct": tool_correct, "llm_args": llm_args,
        "args_valid": args_valid, "args_error": args_error,
        "duration_ms": (time.time() - start) * 1000,
    }


def _list_llm_runs(limit: int = 20) -> list:
    from core.results_store import get_db
    conn = get_db()
    rows = conn.execute("SELECT * FROM llm_runs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _get_llm_results(run_id: int) -> list:
    from core.results_store import get_db
    conn = get_db()
    rows = conn.execute("SELECT * FROM llm_results WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
