"""Module 2: MCP Server Manager"""
import streamlit as st
import json
import os

def render():
    from core.results_store import list_servers, add_server, delete_server, get_server

    st.header("🖥️ Server Manager")

    # Add new server
    with st.expander("➕ Register MCP Server", expanded=False):
        with st.form("add_server_form"):
            name = st.text_input("Name", placeholder="e.g. FedCtx MCP Server")
            description = st.text_input("Description", placeholder="Brief description")
            transport = st.selectbox("Transport", ["stdio", "sse"], help="stdio = local subprocess, sse = remote HTTP")

            if transport == "stdio":
                command = st.text_input("Command", placeholder="e.g. python or /path/to/binary")
                args_str = st.text_input("Arguments (space-separated)", placeholder="e.g. -m mcp_server --port 8080")
                env_str = st.text_input("Environment variables (KEY=VALUE, comma-separated)", placeholder="e.g. API_KEY=xxx, DEBUG=true")
            else:
                url = st.text_input("SSE URL", placeholder="e.g. http://localhost:8080/sse")

            tags_str = st.text_input("Tags (comma-separated)", placeholder="e.g. rust, vector-db, memory")

            submitted = st.form_submit_button("Register")
            if submitted and name:
                config = {"transport": transport}
                if transport == "stdio":
                    config["command"] = command
                    config["args"] = args_str.split() if args_str else []
                    config["env"] = {}
                    if env_str:
                        for pair in env_str.split(","):
                            if "=" in pair:
                                k, v = pair.strip().split("=", 1)
                                config["env"][k] = v
                    config["url"] = ""
                else:
                    config["command"] = ""
                    config["args"] = []
                    config["env"] = {}
                    config["url"] = url

                tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
                sid = add_server(name, transport, config, description, tags)
                st.success(f"Server \"{name}\" registered (ID: {sid})")
                st.rerun()

    # Server list
    st.subheader("Registered Servers")
    servers = list_servers()
    if not servers:
        st.info("No servers registered yet. Click \"Register MCP Server\" above to get started.")
    else:
        for s in servers:
            cfg = json.loads(s["config_json"])
            tags = json.loads(s["tags"]) if s["tags"] else []
            with st.container():
                col1, col2, col3 = st.columns([3, 5, 1])
                with col1:
                    st.markdown(f"**{s['name']}**")
                    st.caption(f"ID: {s['id']} | Transport: {s['transport']}")
                    if tags:
                        st.markdown(" ".join(f"`{t}`" for t in tags))
                with col2:
                    if s["transport"] == "stdio":
                        cmd_display = cfg.get("command", "")
                        args_display = " ".join(cfg.get("args", []))
                        st.code(f"$ {cmd_display} {args_display}")
                    else:
                        st.code(f"SSE: {cfg.get('url', '')}")
                    if s["description"]:
                        st.caption(s["description"])
                with col3:
                    if st.button("Delete", key=f"del_{s['id']}", type="secondary"):
                        delete_server(s["id"])
                        st.rerun()
                st.divider()
