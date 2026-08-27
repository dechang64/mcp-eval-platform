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
elif page == "📝 Reports":
    from modules.reports import render
elif page == "🔄 Comparison":
    from modules.compare import render

render()
