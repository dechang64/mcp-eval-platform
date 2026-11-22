# MCP Evaluation Platform

A comprehensive evaluation platform for MCP (Model Context Protocol) servers, covering **five platform dimensions** that go beyond protocol compliance into semantics and behaviour:

| Dimension | Cases | What It Verifies |
|-----------|-------|------------------|
| **Functional** | 8 | Handshake (protocol-version aware), tool listing, valid/invalid arguments, nonexistent tools, optional capabilities (resources/prompts), protocol version declaration |
| **Performance** | 3 | Call latency (p50/p95/p99), concurrent throughput (RPS at 1/5/10), sustained-call stability |
| **Security** | 7 | SQL injection, path traversal, oversized payloads, special characters, timeout tolerance, request replay, metadata injection (no-crash) |
| **LLM Compatibility** | per-tool | A real LLM (via the unified AMAX Token Router gateway) reads tool descriptions and must pick the right tool and fill schema-valid arguments |
| **Scenario Testing** | 6 | Multi-tool workflows with state passing (write -> read -> delete -> verify), audit consistency, persistence round-trips, plus an LLM Agent loop for composite task planning |

Scores are aggregated into an **A+ to D grade** (functional 40% + performance 30% + security 30%).

> These five dimensions are the platform's own implementation / teaching taxonomy. They are **not** a standards classification, and they are not the five testing dimensions on ISA104 Lecture 10 slide 8. The 18 standard cases, the A+~D grade and the 40/30/30 weights are lab implementation parameters, not a format prescribed by any standard. Metrics must not be mixed across the model / AI-system / agent-tool layers.

## Course linkage (ISA104, Weeks 1-10)

This repository is the upstream of the bundled Track B server kit in
`ISA104_Lab5/5. ISA104_Lab5_TrackB_server_kit/`. ISA104 Lab 5 now offers
**three equally weighted routes** — Track A (the XIPU AI Agent platform),
Track B (this MCP evaluation platform) and Track C (workflow runtime
evaluation, zero-install). Students choose one; each has its own 100-mark
teaching rubric. **Lab 5 is formative and carries no marks toward the module
total** — the official assessment is an in-class test (35) plus a group
demonstration (65).

| Asset | Version | What changed after the w1-w9 prior-teaching audit |
|---|---|---|
| Lecture 10 | v7, 52 slides | "Where we are in the module" replaces a stale delivery table; a visible Prior ISA104 Vocabulary card closes the deck; two agent-evaluation surveys are disambiguated |
| Lab 5 | v1.3, 43-file kit | All `[confirm: ...]` placeholders resolved; Lab LO1–Lab LO6 mapped to module LO A–E; prior-lecture bridges and an optional group-agent transfer task added |
| Two-hour session | 91 slides | Visible vocabulary card, Session LO1–Session LO6, schedule TBC with no date published |
| w1-w9 audit | v1.1 | [`docs/ISA104_Course_Alignment.md`](docs/ISA104_Course_Alignment.md) |
| This app | unified v3 | Documentation-only ISA104 Course page; all LLM traffic through one AMAX Router gateway |

The eight prior lecture decks (335 pages, four lecturers) already cover RAG
evaluation, MCP, red teaming and human-centred design. Lecture 10 and Lab 5
build on those topics rather than repeating them. Four different "five
dimensions" and two different senses of "evaluation" are in circulation across
the module; the visible vocabulary card on the last slide of both decks — and
on the app's ISA104 Course page — reconciles them. See
[`docs/ISA104_Lab5_TrackC.md`](docs/ISA104_Lab5_TrackC.md) for the third route.

The hosted demo at `https://mcp-eval.streamlit.app` is **a demo only**. A cloud
instance cannot reach `localhost:8101` / `localhost:8102` on a student's
machine, so Lab 5 must be run locally with the bundled student kit.

## Standards context (not a compliance claim)

**MCP is an industry protocol, not a standard.** The documents below provide lecture context; none of them certifies this platform, and no graded report is a standards-conformant assessment. Official URLs, full titles and publication statuses are on the Standards Map at the start of ISA104 Lecture 10 and in `ISA104_Lecture10_standards_verification_sheet.docx` (instructor copy). Status: as of 2026-11-16. See [`docs/standards-survey.md`](docs/standards-survey.md) for the full survey.

| Document | What it actually provides | How this platform uses it |
|---|---|---|
| ISO/IEC TS 42119-2:2025 (published 2025-11-03) with the ISO/IEC/IEEE 29119 series | Risk-driven AI-system test process | Same general test-process logic: plan -> cases -> execution -> defect lifecycle -> report |
| ISO/IEC 25059:2023 | AI quality model and terminology; 90.92 under revision, FDIS Ed.2 at approval | Background only. A quality model is not a test method and is not our five-dimension taxonomy |
| GB/T 45288.2-2025 | LLM testing metrics and methods; Chapter 6 environment -> tools -> execution -> reporting; Section 6.5 covers cross-model validation, human review and stable interfaces | Method reference. The Section 6.2 dataset baseline is known only through **secondary interpretations that disagree** (`>= 200` vs `<= 200` items per capability); verify against the official text before citing. Our 30-row teaching dataset is below any such baseline |
| GB/T 45654-2025 (issued 2025-04-25, effective 2025-11-01) | Basic security requirements for generative AI services in China; prescribes no report format | Risk-taxonomy context only; a graded MCP report is not an endorsement under this standard |
| GB/Z 185.6-2026 / GB/Z 185.7-2026 / GB/Z 242-2026 | Agent interaction, agent tool calling (incl. tool-description standardisation), agent technical requirements — national standardisation **guidance** documents | Context for the handshake and tool-description cases; not conformance tests |
| GB/Z 236-2026 / GB/Z 253-2026 | RAG-related guidance documents | Background for retrieval-adjacent scenarios; not conformance tests |
| TC260 practice guides | Standards-related technical documents. 'Guidelines for Secure Deployment and Use of Agents' is published; 'Agent Interaction Security Requirements' (2026-07-29) is a **draft for comment** | Read as guidance; never cite the draft as an in-force requirement |
| NIST AI RMF 1.0 / AI 600-1 | Voluntary framework (GOVERN / MAP / MEASURE / MANAGE) | Vocabulary for risk and continuous monitoring |
| EU AI Act, Reg (EU) 2024/1689, Art. 9 / 11-12 / 14 / 15(3) | Law | The actual "scores -> evidence" legal chain; not a standard |
| ISTQB CT-AI v2.0 / CT-GenAI | Certification syllabi | Teaching vocabulary: testing **of** AI vs testing **with** AI; not a standard text |

Official entry points: https://www.iso.org/standard/84127.html , https://www.iso.org/standard/80655.html , https://openstd.samr.gov.cn/ , https://std.samr.gov.cn/ , https://www.tc260.org.cn/ , https://www.nist.gov/itl/ai-risk-management-framework , https://eur-lex.europa.eu/eli/reg/2024/1689/oj , https://modelcontextprotocol.io/

**Positioning:** existing MCP benchmarks (MCP-Bench, MCP-Universe, MCPMark, MCP-SafetyBench) fix the servers and evaluate the **model**; this platform fixes the model and evaluates the **server** (protocol behaviour, performance, robustness, tool-description legibility, cross-tool consistency). The two are complementary. Neither is a standards-conformant assessment.

**On LLM-as-a-Judge:** the LLM-compatibility dimension uses a model for tool selection, not as a scoring judge. Where a judge is used in teaching, five failure modes need playbooks (bias, position, length, self-preference, score drift), the judge version (model snapshot + prompt + rubric) must be frozen with a changelog, and a human-labelled calibration set should be re-checked after any version change. Spearman rho, MAE, "three runs averaged" and any numeric threshold are **engineering heuristics, not standard requirements** — GB/T 45288.2 Section 6.5 sets no such threshold.

## Architecture

- **Streamlit web UI** (9 pages) + Python evaluation engine, SQLite persistence
- **Dual transport**: stdio (local subprocess) and SSE (remote HTTP) server connections
- **LLM integration** via one OpenAI-compatible gateway (`core/llm_client.py`) to the AMAX Token Router, with 429/5xx backoff; no CLI subprocess, no vendor-specific code
- **Protocol-version awareness**: FN-001 adapts to stateless-core (2026-07-28) servers; Spec Conformance matrix page tracks version/capabilities per server
- **Markdown report export** for every test run

> **Version-table note.** `core/mcp_client.py` ships `KNOWN_PROTOCOL_VERSIONS` with five implementation entries: `2024-11-05`, `2025-03-26`, `2025-06-18`, `2025-11-25`, `2026-07-28`. The ISA104 Lecture 10 five-revision **teaching** timeline lists `2024-11-05 -> 2025-03-26 -> 2025-06-18 -> 2025-08-26 -> 2026-07-28`. The fourth entry differs between the code and the slide; both are implementation / teaching data, not a standard, and should be checked against the [official MCP changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) before reuse. There is no `2026-03-26` release.

## Quick Start

```bash
pip install -r requirements.txt
export AMAX_API_KEY="sk-..."       # or use .streamlit/secrets.toml
export AMAX_MODEL="gpt-4o"         # any model your account can reach
streamlit run app.py
```

The gateway uses the standard library only. See
[`docs/AMAX_Router_Setup.md`](docs/AMAX_Router_Setup.md) and
[`.streamlit/secrets.example.toml`](.streamlit/secrets.example.toml).

Register a server (e.g. the bundled reference server):

```text
Name:        test-echo
Transport:   stdio
Command:     python
Arguments:   test_server.py
```

Or an official reference server:

```text
Name:        filesystem-official
Transport:   stdio
Command:     npx
Arguments:   -y @modelcontextprotocol/server-filesystem /path/to/dir
```

For the ISA104 Lab 5 Track B servers, see `lab5/README.md` and the bundled student kit. Run everything on one machine: the platform must be able to reach `localhost:8101` and `localhost:8102`.

## Benchmark Highlights

Measured on the same host (stdio transport):

| Server | Impl | Suite | Latency (mean) | Throughput (c=1) | LLM Compat |
|--------|------|-------|----------------|-------------------|------------|
| FedCtx v0.8.0 | Rust | 15/15 A+ | 0.6 ms | 1616 RPS | 100% (14/14) |
| filesystem (official) | TypeScript | 13/15 A+ | 0.8 ms | 1342 RPS | 92.9% (13/14)¹ |
| memory (official) | TypeScript | 14/15 A+ | 1.4 ms | 780 RPS | 100% (9/9) |

¹ The LLM confused `read_file` with `read_text_file` — semantic overlap in tool naming, discoverable only through real-model evaluation.

> **Denominator note:** these figures come from a 2026-08 comparative run against the then-current **15-case** suite. Today's standard suite has **18 cases** (functional 8 + performance 3 + security 7), reflected in Lecture 10 and the Lab 5 student kit. These are different runs with different denominators: report the exported results of the actual run and do not rescale them.

## Defect Discovery Case Studies

The platform found two real defects in the self-developed Rust server (FedCtx), both closed with fix-verify loops:

1. **stdio log pollution** — tracing logs (with ANSI codes) were written to stdout, violating the MCP spec's requirement that stdout carry only JSON-RPC messages. Fixed by redirecting the tracing writer to stderr (`e291186`); retest: 0 parse errors.
2. **Audit chain bypass** — MCP-path write operations (`insert_vector` / `add_graph_node` / `add_graph_edge`) skipped `audit.append` while the REST/gRPC paths audited, breaking the audit completeness contract. Caught by the SC-004 audit-consistency scenario; fixed in `a52aa74`; retest: 5/5 scenarios pass, audit entries grow on writes.

## Hosted demo (Streamlit Cloud)

Streamlit Cloud redeploys automatically on a push to `main`. In **App settings ->
Secrets** set:

```toml
MCP_EVAL_DEMO_READONLY = "1"
AMAX_API_KEY = "sk-..."                  # never commit a real key
AMAX_BASE_URL = "https://ai.amaxsmp.com/v1"
AMAX_MODEL = "gpt-4o"                   # override with a reachable model
```

Read-only mode hides every page that can register a server, launch a
subprocess, call an LLM or write to the results database. The **ISA104 Course**
page is documentation-only and stays available. On the public demo no LLM call
is made at all. Full details: [`docs/AMAX_Router_Setup.md`](docs/AMAX_Router_Setup.md).

## License

MIT — see [LICENSE](LICENSE).
