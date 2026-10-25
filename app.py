#!/usr/bin/env python3
"""MCP Evaluation Platform - Web UI

Usage: streamlit run app.py --server.port 8501
"""
import streamlit as st
import sys
import os

st.set_page_config(
    page_title="MCP Evaluation Platform",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _check_password() -> bool:
    """Access gate. When APP_PASSWORD is set in st.secrets, the whole app is
    locked until the password is entered (once per session). If it is not
    configured (local dev), the gate is open."""
    if st.session_state.get("password_ok"):
        return True
    try:
        app_password = st.secrets.get("APP_PASSWORD", "")
    except Exception:
        app_password = ""
    if not app_password:
        return True
    st.title("🔧 MCP Evaluation Platform")
    st.caption("Model Context Protocol Server Evaluation")
    with st.form("access_gate"):
        pwd = st.text_input("Access password", type="password")
        if st.form_submit_button("Unlock"):
            if pwd and pwd == app_password:
                st.session_state.password_ok = True
                st.rerun()
            else:
                st.error("Incorrect password")
    return False


# Sidebar navigation
st.sidebar.title("MCP Evaluation Platform")
st.sidebar.caption("Model Context Protocol Server Evaluation")

page = st.sidebar.radio("Navigation", [
    "📊 Dashboard",
    "🖥️ Server Manager",
    "📋 Test Suites",
    "▶️ Test Runs",
    "🤖 LLM Compatibility",
    "🎬 Scenario Testing",
    "📐 Spec Conformance",
    "📝 Reports",
    "🔄 Comparison",
])

if page == "📊 Dashboard":
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

if _check_password():
    render()
