#!/usr/bin/env python3
"""MCP Evaluation Platform - Web UI

Usage: streamlit run app.py --server.port 8501

Deployment note
---------------
Set MCP_EVAL_DEMO_READONLY=1 on a public / hosted deployment. Read-only mode
hides every page that can register a server, launch a subprocess, call an LLM
or write to the results database, and shows a persistent demo banner. Local
teaching use (the bundled ISA104 Lab 5 kit) leaves the variable unset.

Every LLM call goes through core/llm_client.py -> AMAX Token Router. Set
AMAX_API_KEY (and optionally AMAX_BASE_URL / AMAX_MODEL) in the environment or
in Streamlit Cloud Secrets; the key is never displayed in the UI.
"""
import os
import streamlit as st

DEMO_READONLY = os.environ.get("MCP_EVAL_DEMO_READONLY", "").strip().lower() in (
    "1", "true", "yes", "on")

st.set_page_config(
    page_title="MCP Evaluation Platform",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar navigation
st.sidebar.title("MCP Evaluation Platform")
st.sidebar.caption("Model Context Protocol Server Evaluation")
st.sidebar.warning(
    "DEMO ONLY. This hosted instance is for demonstration and cannot reach "
    "localhost servers on your machine. ISA104 Lab 5 must be run locally with "
    "the bundled student kit.")

ALL_PAGES = [
    "📚 ISA104 Course",
    "📊 Dashboard",
    "🖥️ Server Manager",
    "📋 Test Suites",
    "▶️ Test Runs",
    "🤖 LLM Compatibility",
    "🎬 Scenario Testing",
    "📐 Spec Conformance",
    "📝 Reports",
    "🔄 Comparison",
]
# Pages that only read already-stored results. Everything that can register a
# server, start a subprocess, call an LLM or write to the database is hidden.
READONLY_PAGES = [
    "📚 ISA104 Course",
    "📊 Dashboard",
    "📐 Spec Conformance",
    "📝 Reports",
    "🔄 Comparison",
]
PAGES = READONLY_PAGES if DEMO_READONLY else ALL_PAGES
page = st.sidebar.radio("Navigation", PAGES)

# Unified gateway status. Never show the key, not even a masked fragment.
if DEMO_READONLY:
    st.sidebar.caption("LLM calls disabled in this read-only demo")
else:
    try:
        from core.llm_client import status as _gateway_status
        _gw = _gateway_status()
        st.sidebar.caption("LLM gateway: " + _gw["transport"])
        st.sidebar.caption(
            ("Model: " + _gw["model"]) if _gw["configured"]
            else "AMAX_API_KEY: not configured")
    except Exception:
        st.sidebar.caption("LLM gateway: unavailable")

if DEMO_READONLY:
    st.info(
        "READ-ONLY DEMO MODE is active. Server registration, test execution, "
        "LLM compatibility checks and scenario runs are disabled on this hosted "
        "instance; the pages above show stored demonstration data only. "
        "Set MCP_EVAL_DEMO_READONLY=0 locally to enable the full lab workflow.")

if page == "📚 ISA104 Course":
    from modules.course_hub import render
elif page == "📊 Dashboard":
    from modules.dashboard import render
elif page == "🖥️ Server Manager":
    from modules.server_manager import render
elif page == "📋 Test Suites":
    from modules.test_suites import render
elif page == "▶️ Test Runs":
    from modules.test_runs import render
elif page == "🤖 LLM Compatibility":
    from modules.llm_compat_page import render
elif page == "🎬 Scenario Testing":
    from modules.scenarios_page import render
elif page == "📐 Spec Conformance":
    from modules.conformance import render
elif page == "📝 Reports":
    from modules.reports import render
elif page == "🔄 Comparison":
    from modules.compare import render

render()
