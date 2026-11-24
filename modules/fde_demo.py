"""Offline XiaoZhu interaction demo (instructor reference, Chinese UI).

The HTML is static: zero network requests, zero credentials, zero LLM calls,
zero subprocesses and no database access. It is therefore safe in
MCP_EVAL_DEMO_READONLY mode. The file is loaded only when a visitor opts in.
"""
from pathlib import Path

import streamlit as st

ASSET = Path(__file__).resolve().parent.parent / "assets" / "xiaozhu_demo.html"


def render():
    st.caption(
        "Offline interaction demo from the second recorded course. Chinese UI, "
        "instructor reference. It does not call any model."
    )
    if not ASSET.is_file():
        st.warning("Demo asset not found in this deployment.")
        return
    if not st.checkbox("Open the offline XiaoZhu interaction demo", value=False):
        return
    import streamlit.components.v1 as components
    components.html(ASSET.read_text(encoding="utf-8"),
                    height=760, scrolling=True)
    st.caption(
        "Static page only: 0 network requests, 0 API keys. Close the checkbox "
        "to unload it."
    )
