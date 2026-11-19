# ISA104 Lab 5 — Track B companion servers

Two self-contained MCP servers are used in **ISA104 Lab 5, Track B**. Both are
pure Python standard library (no dependencies) and speak the MCP HTTP+SSE
transport.

> These two server files are distributed **only in the bundled course kit**
> (`ISA104_Lab5/5. ISA104_Lab5_TrackB_server_kit/`), not in this public
> repository — `server_b.py` contains the planted defects the lab asks you to
> discover. The commands below assume you are in the kit directory.

- `server_a.py` — reference implementation, `http://localhost:8101/sse`
- `server_b.py` — the server you will evaluate and repair, `http://localhost:8102/sse`

> This directory intentionally contains **no answer key**. The lab's learning
> objective is to infer defects from the evaluation report alone. The
> instructor's answer key and rubric ship separately with the course pack.

## Running the servers

```bash
# Terminal 1
python server_a.py

# Terminal 2
python server_b.py
```

Then start the platform from the repository root:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Register both servers in **Server Manager** with Transport = `sse`:

| Name | SSE URL |
|------|---------|
| Lab5 Server A | `http://localhost:8101/sse` |
| Lab5 Server B | `http://localhost:8102/sse` |

Run the **standard suite** on A, then on B. Open **Reports** and
**Comparison**, and export both Markdown reports.

## Important

- **Run everything on one machine.** A hosted Streamlit instance cannot reach
  `localhost` on your computer. The public demo at
  `https://mcp-eval.streamlit.app` is for demonstration only and requires
  authentication; it is not the Lab 5 environment.
- Students should use the bundled kit
  `ISA104_Lab5/5. ISA104_Lab5_TrackB_server_kit/`, which contains a Windows
  launcher, the task sheet, troubleshooting notes and the MIT licence. Do not
  ask students to clone this repository during class.
- The standard suite has **18 cases** (functional 8 + performance 3 +
  security 7). Historical benchmark figures in the root README come from a
  separate 2026-08 run against a **15-case** suite; do not rescale them.
- The five platform dimensions are a teaching taxonomy, not a standards
  classification. A graded report is evidence of traceability, **not** a
  standards-conformant assessment. See the root README and
  `docs/standards-survey.md` for the standards context.
