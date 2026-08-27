#!/usr/bin/env python3
"""MCP综合评测系统 - Web平台

Usage: streamlit run app.py --server.port 8501
"""
import streamlit as st
import sys
import os

st.set_page_config(
    page_title="MCP综合评测系统",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar navigation
st.sidebar.title("MCP综合评测系统")
st.sidebar.caption("Model Context Protocol Evaluation Platform")

page = st.sidebar.radio("导航", [
    "📊 仪表板",
    "🖥️ Server管理",
    "📋 测试套件",
    "▶️ 测试运行",
    "🤖 LLM兼容性",
    "📝 报告详情",
    "🔄 横向对比",
])

if page == "📊 仪表板":
    from modules.dashboard import render
elif page == "🖥️ Server管理":
    from modules.server_manager import render
elif page == "📋 测试套件":
    from modules.test_suites import render
elif page == "▶️ 测试运行":
    from modules.test_runs import render
elif page == "🤖 LLM兼容性":
    from modules.llm_compat_page import render
elif page == "📝 报告详情":
    from modules.reports import render
elif page == "🔄 横向对比":
    from modules.compare import render

render()
