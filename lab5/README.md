# ISA104 Lab 5 — Track B companion servers

Two self-contained MCP servers are used in **ISA104 Lab 5, Track B**. Both are
pure Python standard library (no dependencies) and speak the MCP HTTP+SSE
transport.

Lab 5 has **three alternative routes**: Track A (agent answers on the XIPU AI
Agent platform), Track B (this kit) and Track C (workflow runtime evaluation,
zero-install, `../6. ISA104_Lab5_TrackC_workflow_kit/` in the student pack).
Each has its own 100-mark teaching rubric. **Lab 5 is formative and carries no
marks toward the module total**; the official assessment is an in-class test
(35) plus a group demonstration (65). See
[`docs/ISA104_Lab5_TrackC.md`](../docs/ISA104_Lab5_TrackC.md).

> These two server files are distributed **only in the bundled course kit**
> (`ISA104_Lab5/5. ISA104_Lab5_TrackB_server_kit/`). On 2026-11-21 the
> historical `lab4/server_a.py` / `lab4/server_b.py` copies were removed from
> this public repository, because the defective twin carried answer-bearing
> comments. The kit copies are stripped of those comments; `server_b.py`
> contains the planted defects the lab asks you to discover. The commands
> below assume you are in the kit directory.

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
export AMAX_API_KEY="sk-..."       # unified LLM gateway; see docs/AMAX_Router_Setup.md
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
- For the accompanying 120-minute English lecture on evaluating AI agents,
  see [`docs/ISA104_TwoHour_Session.md`](../docs/ISA104_TwoHour_Session.md)
  and the [complete speaker script](../docs/ISA104_TwoHour_Speaker_Script_EN.md).

- All LLM calls in the platform now go through the single AMAX Token Router
  gateway (`core/llm_client.py`); the old `z-ai` CLI requirement is gone.
- The two-hour English session is **91 slides** with a visible Prior ISA104
  Vocabulary card; its schedule is TBC and no date is published.
