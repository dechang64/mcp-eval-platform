"""Module 3: Test Suite Preview"""
import streamlit as st
import json

def render():
    from core.test_runner import load_suites

    st.header("📋 Test Suites")

    suites = load_suites()

    tab1, tab2, tab3 = st.tabs(["🔧 Functional", "⚡ Performance", "🔒 Security"])

    with tab1:
        cases = suites.get("functional", [])
        st.caption(f"{len(cases)} cases | MCP protocol compliance and core functionality")
        for c in cases:
            with st.expander(f"{c['id']} - {c['name']}"):
                st.markdown(f"**Description**: {c.get('description', '')}")
                st.markdown(f"**Method**: `{c['method']}`")
                if "params" in c:
                    st.json(c["params"])
                elif "params_template" in c:
                    st.json(c["params_template"])
                st.markdown(f"**Expected**: `{json.dumps(c['expected'], ensure_ascii=False)}`")
                st.markdown(f"**Timeout**: {c.get('timeout', 30)}s")

    with tab2:
        cases = suites.get("performance", [])
        st.caption(f"{len(cases)} cases | Latency / throughput / concurrency benchmarking")
        for c in cases:
            with st.expander(f"{c['id']} - {c['name']}"):
                st.markdown(f"**Description**: {c.get('description', '')}")
                st.markdown(f"**Iterations**: {c.get('iterations', 10)}")
                st.markdown(f"**Concurrency**: {c.get('concurrency', [1, 5, 10])}")
                st.markdown(f"**Metrics**: {', '.join(c.get('metrics', []))}")

    with tab3:
        cases = suites.get("security", [])
        st.caption(f"{len(cases)} cases | Injection / path traversal / timeout / boundary inputs")
        for c in cases:
            with st.expander(f"{c['id']} - {c['name']}"):
                st.markdown(f"**Description**: {c.get('description', '')}")
                if "params_template" in c:
                    st.json(c["params_template"])
                st.markdown(f"**Expected**: Server must not crash (`no_crash: true`)")

    st.divider()
    st.subheader("Scoring Rules")
    st.markdown("""
    | Dimension | Weight | Criteria |
    |-----------|--------|----------|
    | Functional correctness | 40% | Pass rate × weight |
    | Performance | 30% | P95 latency + concurrent throughput |
    | Security robustness | 30% | Crash rate + error handling |
    """)
