"""模块3: 测试套件预览"""
import streamlit as st
import json

def render():
    from core.test_runner import load_suites

    st.header("📋 测试套件")

    suites = load_suites()

    tab1, tab2, tab3 = st.tabs(["🔧 功能测试", "⚡ 性能测试", "🔒 安全测试"])

    with tab1:
        cases = suites.get("functional", [])
        st.caption(f"共 {len(cases)} 个用例 | 验证MCP协议合规性和基本功能")
        for c in cases:
            with st.expander(f"{c['id']} - {c['name']}"):
                st.markdown(f"**描述**: {c.get('description', '')}")
                st.markdown(f"**方法**: `{c['method']}`")
                if "params" in c:
                    st.json(c["params"])
                elif "params_template" in c:
                    st.json(c["params_template"])
                st.markdown(f"**预期**: `{json.dumps(c['expected'], ensure_ascii=False)}`")
                st.markdown(f"**超时**: {c.get('timeout', 30)}s")

    with tab2:
        cases = suites.get("performance", [])
        st.caption(f"共 {len(cases)} 个用例 | 延迟/吞吐/并发能力基准")
        for c in cases:
            with st.expander(f"{c['id']} - {c['name']}"):
                st.markdown(f"**描述**: {c.get('description', '')}")
                st.markdown(f"**迭代次数**: {c.get('iterations', 10)}")
                st.markdown(f"**并发**: {c.get('concurrency', [1, 5, 10])}")
                st.markdown(f"**指标**: {', '.join(c.get('metrics', []))}")

    with tab3:
        cases = suites.get("security", [])
        st.caption(f"共 {len(cases)} 个用例 | 注入/路径穿越/超时/边界case")
        for c in cases:
            with st.expander(f"{c['id']} - {c['name']}"):
                st.markdown(f"**描述**: {c.get('description', '')}")
                if "params_template" in c:
                    st.json(c["params_template"])
                st.markdown(f"**预期**: 服务器不崩溃 (`no_crash: true`)")

    st.divider()
    st.subheader("评分规则")
    st.markdown("""
    | 维度 | 权重 | 评分标准 |
    |------|------|---------|
    | 功能正确性 | 40% | 通过率 × 权重 |
    | 性能基准 | 30% | P95延迟 + 并发吞吐 |
    | 安全健壮性 | 30% | 崩溃率 + 错误处理 |
    """)
