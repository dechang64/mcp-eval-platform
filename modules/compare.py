"""Module 6: Cross-Server Comparison — five-dimension comprehensive view"""
import streamlit as st
import json

def render():
    from core.results_store import list_servers, list_runs, get_run_results, get_db
    from core.scoring import compute_score
    from modules.utils import status_badge, fmt_duration

    st.header("🔄 Comparison")
    st.caption("Five-dimension comprehensive benchmark across servers: functional, performance, security, LLM compatibility, scenario collaboration.")

    servers = list_servers()
    if len(servers) < 2:
        st.info("At least 2 servers are required for comparison")
        return

    server_names = [s["name"] for s in servers]
    selected = st.multiselect("Select servers (2 or more)", server_names, default=server_names[:3])

    if len(selected) < 2:
        st.warning("Please select at least 2 servers")
        return

    # ── Collect latest data per server across all three result stores ──
    data = {}
    for sname in selected:
        server = next(s for s in servers if s["name"] == sname)
        entry = {
            "grade": "-", "functional": None, "performance": None, "security": None,
            "overall": None, "p95_ms": None, "rps1": None,
            "llm_acc": None, "llm_args": None, "llm_grade": None,
            "scen_pass": None, "scen_total": None,
            "protocol_version": None, "generation": None,
        }

        # 1) Standard suite: latest run
        runs = list_runs(server_id=server["id"], limit=1)
        if runs:
            run = runs[0]
            results = get_run_results(run["id"])
            if results:
                score = compute_score(results)
                entry.update({
                    "grade": f"{score.letter} ({score.overall:.0f})",
                    "functional": score.functional,
                    "performance": score.performance,
                    "security": score.security,
                    "overall": score.overall,
                })
                # Perf details: p95 + single-concurrency RPS
                for r in results:
                    if r["category"] == "performance" and r["status"] == "passed" and r.get("detail_json"):
                        try:
                            d = json.loads(r["detail_json"])
                            if "p95_ms" in d and entry["p95_ms"] is None:
                                entry["p95_ms"] = d["p95_ms"]
                            for cr in d.get("concurrency_results", []):
                                if cr.get("concurrency") == 1:
                                    entry["rps1"] = cr.get("rps")
                        except Exception:
                            pass

        # 2) LLM compatibility: latest llm run
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM llm_runs WHERE server_id=? ORDER BY id DESC LIMIT 1",
            (server["id"],)).fetchall()
        conn.close()
        if rows:
            lr = dict(rows[0])
            entry.update({
                "llm_acc": lr.get("tool_accuracy"),
                "llm_args": lr.get("args_valid_rate"),
                "llm_grade": lr.get("grade"),
            })

        # 3) Scenarios: latest scenario run
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM scenario_runs WHERE server_id=? ORDER BY id DESC LIMIT 1",
            (server["id"],)).fetchall()
        conn.close()
        if rows:
            sr = dict(rows[0])
            # Applicable scenarios = non-skipped (tool-family mismatch is not a failure)
            applicable = sr.get("total") or 0
            passed = sr.get("passed") or 0
            try:
                details = json.loads(sr.get("details_json") or "[]")
                applicable = sum(1 for d in details if d.get("status") != "skipped")
                passed = sum(1 for d in details if d.get("status") == "passed")
            except Exception:
                pass
            entry["scen_pass"] = passed
            entry["scen_total"] = applicable

        # 4) Protocol conformance: latest probe
        conn = get_db()
        rows = conn.execute(
            "SELECT protocol_version, generation FROM spec_conformance WHERE server_id=? ORDER BY id DESC LIMIT 1",
            (server["id"],)).fetchall()
        conn.close()
        if rows:
            entry["protocol_version"] = rows[0]["protocol_version"]
            entry["generation"] = rows[0]["generation"]

        data[sname] = entry

    # ── Five-dimension table ──
    def fmt_pct(v):
        return f"{v:.0f}%" if v is not None else "-"
    def fmt_f(v, nd=1):
        return f"{v:.{nd}f}" if v is not None else "-"

    table_rows = [
        ["Overall Grade"] + [data[s]["grade"] for s in selected],
        ["Functional"] + [fmt_pct(data[s]["functional"]) for s in selected],
        ["Performance"] + [fmt_pct(data[s]["performance"]) for s in selected],
        ["Security"] + [fmt_pct(data[s]["security"]) for s in selected],
        ["LLM Compatibility"] + [
            f"{fmt_pct(data[s]['llm_acc'])} ({data[s]['llm_grade'] or '-'})" for s in selected],
        ["Scenarios Passed"] + [
            f"{data[s]['scen_pass']}/{data[s]['scen_total']}" if data[s]["scen_total"] else "-"
            for s in selected],
        ["P95 Latency"] + [f"{fmt_f(data[s]['p95_ms'])} ms" if data[s]["p95_ms"] is not None else "-" for s in selected],
        ["Throughput (conc=1)"] + [f"{fmt_f(data[s]['rps1'], 0)} RPS" if data[s]["rps1"] is not None else "-" for s in selected],
        ["Protocol Version"] + [f"{data[s]['protocol_version'] or '-'}" for s in selected],
    ]

    st.subheader("Five-Dimension Comparison")
    st.table(table_rows)

    # ── Radar chart ──
    st.subheader("Dimension Radar")
    dims = ["Functional", "Performance", "Security", "LLM Compat", "Scenarios"]
    try:
        import plotly.graph_objects as go
        fig = go.Figure()
        for sname in selected:
            e = data[sname]
            scen_pct = (e["scen_pass"] / e["scen_total"] * 100) if e["scen_total"] else 0
            values = [
                e["functional"] or 0,
                e["performance"] or 0,
                e["security"] or 0,
                e["llm_acc"] or 0,
                scen_pct,
            ]
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=dims + [dims[0]],
                fill="toself",
                name=sname,
                opacity=0.6,
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=420,
            margin=dict(l=60, r=60, t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.caption(f"Radar chart unavailable: {e}")

    st.divider()

    # ── Performance detail bar chart ──
    st.subheader("Performance Comparison")
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=1, cols=2, subplot_titles=("P95 Latency (ms)", "Throughput @ conc=1 (RPS)"))
        names = [s for s in selected if data[s]["p95_ms"] is not None]
        fig.add_trace(go.Bar(x=names, y=[data[s]["p95_ms"] for s in names], name="P95 ms",
                             marker_color="#4d23ca"), row=1, col=1)
        names2 = [s for s in selected if data[s]["rps1"] is not None]
        fig.add_trace(go.Bar(x=names2, y=[data[s]["rps1"] for s in names2], name="RPS",
                             marker_color="#8b6fe8"), row=1, col=2)
        fig.update_layout(height=330, showlegend=False, margin=dict(l=40, r=40, t=60, b=40))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.caption(f"Chart unavailable: {e}")

    st.caption("Note: scenario pass rate counts applicable scenarios only (skipped scenarios are excluded from the denominator when the tool family does not match). LLM compatibility uses the latest run with glm-4-plus.")
