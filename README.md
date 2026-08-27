# MCP Evaluation Platform

A comprehensive evaluation platform for MCP (Model Context Protocol) servers, covering **five dimensions** that go beyond protocol compliance into semantics and behavior:

| Dimension | Cases | What It Verifies |
|-----------|-------|------------------|
| **Functional** | 8 | Handshake (protocol-version aware), tool listing, valid/invalid arguments, nonexistent tools, optional capabilities (resources/prompts), protocol version declaration |
| **Performance** | 3 | Call latency (p50/p95/p99), concurrent throughput (RPS at 1/5/10), sustained-call stability |
| **Security** | 7 | SQL injection, path traversal, oversized payloads, special characters, timeout tolerance, request replay, metadata injection (no-crash) |
| **LLM Compatibility** | per-tool | A real LLM (glm-4-plus) reads tool descriptions and must pick the right tool and fill schema-valid arguments |
| **Scenario Testing** | 6 | Multi-tool workflows with state passing (write → read → delete → verify), audit consistency, persistence round-trips, plus an LLM Agent loop for composite task planning |

Scores are aggregated into an **A+ to D grade** (functional 40% + performance 30% + security 30%).

## Standards Alignment

The evaluation methodology is aligned with the latest national and international standards (see [docs/standards-survey.md](docs/standards-survey.md)):

| Platform Dimension | Aligned Standard |
|--------------------|------------------|
| Evaluation methodology (dimension-based indicators, objective + model-in-the-loop scoring) | **GB/T 45288.2-2025**《人工智能大模型 第2部分：评测指标与方法》 |
| Quality characteristics (functional suitability, performance efficiency, reliability, security) | **ISO/IEC 25059:2023** (AI quality model, SQuaRE extension) |
| Security dimension taxonomy | **GB/T 45654-2025** (Generative AI service security baseline) + TC260《智能体交互安全要求》practice guide |
| Protocol conformance matrix | **MCP specification timeline** 2024-11-05 → 2026-07-28 (stateless core), version-aware FN-001/FN-008 |

Positioning: existing MCP benchmarks (MCP-Bench, MCP-Universe, MCPMark, MCP-SafetyBench) evaluate **models** with fixed servers; this platform evaluates **servers** with a fixed model — the complementary gap, aligned with GB/T 45288.2 methodology applied at the MCP server layer.

## Architecture

- **Streamlit web UI** (9 pages) + Python evaluation engine, SQLite persistence
- **Dual transport**: stdio (local subprocess) and SSE (remote HTTP) server connections
- **LLM integration** via z-ai CLI (glm-4-plus) with automatic 429 backoff
- **Protocol-version awareness**: FN-001 adapts to stateless-core (2026-07-28) servers; Spec Conformance matrix page tracks version/capabilities per server
- **Markdown report export** for every test run

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

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

## Benchmark Highlights

Measured on the same host (stdio transport):

| Server | Impl | Suite | Latency (mean) | Throughput (c=1) | LLM Compat |
|--------|------|-------|----------------|-------------------|------------|
| FedCtx v0.8.0 | Rust | 15/15 A+ | 0.6 ms | 1616 RPS | 100% (14/14) |
| filesystem (official) | TypeScript | 13/15 A+ | 0.8 ms | 1342 RPS | 92.9% (13/14)¹ |
| memory (official) | TypeScript | 14/15 A+ | 1.4 ms | 780 RPS | 100% (9/9) |

¹ The LLM confused `read_file` with `read_text_file` — semantic overlap in tool naming, discoverable only through real-model evaluation.

## Defect Discovery Case Studies

The platform found two real defects in the self-developed Rust server (FedCtx), both closed with fix-verify loops:

1. **stdio log pollution** — tracing logs (with ANSI codes) were written to stdout, violating the MCP spec's requirement that stdout carry only JSON-RPC messages. Fixed by redirecting the tracing writer to stderr (`e291186`); retest: 0 parse errors.
2. **Audit chain bypass** — MCP-path write operations (`insert_vector` / `add_graph_node` / `add_graph_edge`) skipped `audit.append` while the REST/gRPC paths audited, breaking the audit completeness contract. Caught by the SC-004 audit-consistency scenario; fixed in `a52aa74`; retest: 5/5 scenarios pass, audit entries grow on writes.

## License

MIT
