"""ISA104 course hub — documentation-only page.

This page never imports core, never calls an LLM, never starts a subprocess
and never writes to the results database, so it is safe in the read-only
hosted demo. It reconciles the prior nine weeks of teaching with Lecture 10,
Lab 5 and the two-hour session.
"""
import streamlit as st


def render():
    st.header("📚 ISA104 · Course Materials")
    st.caption(
        "Testing and Evaluation of AI Agents — where the prior nine weeks, "
        "Lecture 10, Lab 5 and the two-hour English session fit together."
    )

    st.subheader("Where we are in the module")
    st.markdown("""
| Stage | Taught by | What you already have | What this stage adds |
|---|---|---|---|
| Weeks 1–9 | Four lecturers, 8 decks / 335 pages | Prompt engineering, RAG and its four evaluation dimensions, agentic AI and MCP, AI safety and red teaming, human-centred design | The vocabulary and the failure modes we test against |
| Lecture 10 | This teaching block, **v7, 52 slides** | Standards Map, ISTQB CT-AI / CT-GenAI, five teaching dimensions, LLM-as-a-judge | How a test condition, an oracle and a release gate apply to an agent |
| Lab 5 | Student practical, **v1.3** | Three alternative routes, each with a 100-mark rubric | Hands-on evidence: dataset, trace or execution record |
| Two-hour session | Standalone principles lecture, **91 slides**, schedule TBC | Full English speaker script, four Checkpoints, two activities | The method end to end, from test design to a release decision |
""")

    st.subheader("Lab 5 — three routes, one method")
    st.markdown("""
| | Track A (default) | Track B (advanced) | Track C (zero-install) |
|---|---|---|---|
| Object under test | An agent's answers on the XIPU AI Agent platform | The MCP server its tools depend on | The execution record a workflow runtime left behind |
| Primary evidence | 30-row stratified dataset, run A/B | 18-case suite, exported Markdown report | Node ledger, 2 executions / 10 nodes, case set C01–C12 |
| Key idea | Retrieval vs generation failures | Protocol behaviour, robustness, tool legibility | Confirmed / unknown / never-started; a generated narrative is not a record |
| Kit | `1. ...evaluation_dataset.csv` | `5. ...TrackB_server_kit/` | `6. ...TrackC_workflow_kit/` |

All three share the same method: state the test condition and oracle, control
one variable, record every setting, and report what the evidence does and does
not support. See [`docs/ISA104_Lab5_TrackC.md`](https://github.com/dechang64/mcp-eval-platform/blob/main/docs/ISA104_Lab5_TrackC.md).
""")

    st.info(
        "**Assessment status.** Lab 5 is **formative and carries no marks toward "
        "the module total**. The official assessment is the in-class test (35: "
        "MCQ 20 + reflective 15) plus the group demonstration (65). The 100-mark "
        "rubrics inside the kits are teaching feedback scales, not module marks."
    )

    st.subheader("Prior ISA104 vocabulary — one card, four sources")
    st.caption(
        "The same visible card closes Lecture 10 v7 and the 91-slide session. "
        "It exists because the same words mean different things in different weeks."
    )
    st.markdown("""
| Phrase | Where it comes from | What it actually means here |
|---|---|---|
| Five Pillars | Week 4, AI safety | Five safety / ethics principles for AI applications |
| Five teaching dimensions | Lecture 10 | A pedagogy frame for testing AI agents, **not** a standard |
| Five platform dimensions | This repository | Functional / performance / security / LLM compatibility / scenario testing — an implementation taxonomy |
| Five agent-evaluation items | Week 6, agentic AI | A survey's list of agent evaluation concerns |
| HCI evaluation | Week 9 | SUS / ISO 9241-11 usability of an interface with a human user |
| System-test evaluation | Lecture 10 + Lab 5 | Whether a system meets a verifiable test condition |
| arXiv:2503.16416 | Cited in Week 6 | Yehudai et al., *Survey on Evaluation of LLM-based Agents* (ACL 2026 Findings) |
| arXiv:2507.21504 | Cited in Lecture 10 | A different agent-evaluation survey (KDD 2025) — do not merge the two |
""")

    st.subheader("Learning outcomes: three naming layers")
    st.markdown("""
- **Module LO A–E** — the official ISA104 module specification.
- **Lab LO1–Lab LO6** — the practical; each is mapped to module LO A–E in the Lab 5 brief.
- **Session LO1–Session LO6** — the two-hour lecture; stated on slide 4 and recalled on slide 89.

They are different sets with different numbers. Never write "LO3" without its prefix.
""")

    st.subheader("Reading list in this repository")
    st.markdown("""
- [`docs/ISA104_TwoHour_Session.md`](https://github.com/dechang64/mcp-eval-platform/blob/main/docs/ISA104_TwoHour_Session.md) — 120-minute run of show, evidence policy, standards boundary
- [`docs/ISA104_TwoHour_Speaker_Script_EN.md`](https://github.com/dechang64/mcp-eval-platform/blob/main/docs/ISA104_TwoHour_Speaker_Script_EN.md) — complete verbatim script, 91 sections
- [`docs/ISA104_Course_Alignment.md`](https://github.com/dechang64/mcp-eval-platform/blob/main/docs/ISA104_Course_Alignment.md) — w1–w9 conflict audit and what was changed
- [`docs/standards-survey.md`](https://github.com/dechang64/mcp-eval-platform/blob/main/docs/standards-survey.md) — standards context, not a compliance claim
- [`docs/AMAX_Router_Setup.md`](https://github.com/dechang64/mcp-eval-platform/blob/main/docs/AMAX_Router_Setup.md) — the unified model gateway
""")

    st.markdown("**Schedule:** TBC — no delivery date is published.")
    st.caption(
        "The two-hour session is a standalone principles lecture. Its PPTX and "
        "DOCX are instructor-facing binaries and are not stored in this repository."
    )
