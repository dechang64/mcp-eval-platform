# Lab 4 · Evaluate a Real MCP Server (Companion Servers)

Two self-contained MCP servers for SAT 101 Lab 4. `server_a.py` is a clean
reference implementation. `server_b.py` is its defective twin — same tools,
same business logic, **five planted defects**. Your job: evaluate both with
the [mcp-eval-platform](https://mcp-eval.streamlit.app), read the graded
reports, and locate every defect **from the failing cases alone** — then fix
them and re-grade until B earns an A.

Both servers are pure Python standard library (no dependencies), ~200 lines
each, and speak the MCP HTTP+SSE transport. Reading the source is part of
the lab — but try to diagnose from the evaluation report first, like a real
evaluator would.

## Quick Start

```bash
# Terminal 1 - the reference server
python server_a.py            # listens on http://localhost:8101/sse

# Terminal 2 - the defective twin
python server_b.py            # listens on http://localhost:8102/sse
```

Register both in the platform (Server Manager → Transport: `sse`):

| Name | SSE URL |
|------|---------|
| Lab4 Server A | `http://localhost:8101/sse` |
| Lab4 Server B | `http://localhost:8102/sse` |

Run the **standard suite** (functional + performance + security) on each,
then open **Reports** and **Comparison**.

## Expected Grades (instructor copy)

| | Functional | Performance | Security | Overall |
|---|---|---|---|---|
| Server A | 100 | ~96–100 | 100 | **A+ (~99)** |
| Server B | ~33 | ~40 | ~14 | **D (~30)** |

> The cloud instance cannot reach your `localhost`. Run the platform locally
> (`streamlit run app.py`) for this lab, or deploy the servers where the
> platform can reach them.

## The Five Defects (spoilers — diagnose before reading)

| # | Defect | Failing cases | Lesson |
|---|--------|---------------|--------|
| 1 | Declares a bogus protocol version `2027-13-99` | FN-001, FN-008 | The version declaration is a contract: the client SDK refuses the handshake outright — lying about your version breaks interop, not just paperwork |
| 2 | Unknown tool pretends success ("done") | FN-004 | Silent success is worse than an error: callers build on results that never happened |
| 3 | Invalid arguments silently accepted | FN-005 | Validation that is computed but ignored — the most common real-world validation bug |
| 4 | Path-traversal input kills the session | SEC-002 **and every security case after it** | One unhandled hostile input cascades: after the crash, the server is unresponsive, so SEC-003–007 all fail. Crash defects are not local — they take down every later interaction |
| 5 | Artificial 3s delay on every call | PF-001 (p95 ≈ 3000 ms) | Performance regressions are defects too — graders measure them |

Diagnosis shortcut: `diff server_a.py server_b.py` shows exactly five
changes — check them against your report-driven hypotheses.

## Worksheet

1. **Report reading.** Before touching the code: list every failing case for
   Server B and write a one-sentence hypothesis for each. Which failures
   share a single root cause?
2. **The cascade.** Why did SEC-003 through SEC-007 fail when Server B has
   only one security defect? What does this imply for real incident triage?
3. **The contract.** The SDK rejected Server B's handshake with
   `Unsupported protocol version from the server: 2027-13-99` — yet the rest
   of the suite still ran and produced results. Explain why (hint: where does
   the platform check `protocol_version`, and what does the server do with
   requests when it tracks no state?).
4. **Stability vs latency.** Server A deliberately does ~20 ms of simulated
   work per call. Read PF-003's detail: what is `max_min_ratio`, and why do
   sub-10 ms servers fail stability checks on pure scheduler jitter?
5. **Fix and re-grade.** Fix all five defects in `server_b.py` and re-run the
   suite until it earns an A. Submit: the fixed file + a before/after
   Comparison screenshot + your defect hypotheses from question 1.

## What the Servers Implement

- **Transport**: HTTP+SSE (MCP 2024-11-05 style) — `GET /sse` opens the event
  stream, `POST /messages?session_id=…` receives JSON-RPC requests
- **Methods**: `initialize`, `notifications/initialized`, `ping`,
  `tools/list`, `tools/call`
- **Tools**: `add(a, b)`, `echo(text)`, `lookup_order(order_id)` — pure
  in-memory logic, no I/O, nothing to actually exploit

## Grading Mapping (how the platform sees it)

- Functional 40% — handshake, tool discovery, error semantics, version contract
- Performance 30% — p95 latency ≤ 100 ms scores full; ≥ 5000 ms scores zero
- Security 30% — hostile inputs must be refused **and the server must stay
  alive**; a crash fails the case and every case after it
