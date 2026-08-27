# Standards & Landscape Survey — MCP Server Evaluation

*Survey date: 2026-08-27. Scope: MCP protocol specifications, international standards (ISO/IEC, ITU-T), Chinese national standards (GB/T, TC260), and academic MCP benchmarks. Purpose: position the platform against the latest standards and identify compliance-aligned action items.*

---

## 1. MCP Protocol Specification Evolution

The protocol our platform tests is itself a fast-moving standard. Version timeline:

| Version | Date | Key Changes |
|---------|------|-------------|
| 2024-11-05 | Nov 2024 | Original release (stdio + HTTP+SSE) |
| 2025-06-18 | Jun 2025 | OAuth 2.1 authorization framework; Streamable HTTP replaces HTTP+SSE; structured tool output |
| 2025-11-25 | Nov 2025 | Task management; elicitation framework; resource cache control (`ttlMs`, `cacheScope`) |
| **2026-07-28** | **Jul 2026** | **Stateless core — removes `initialize`/`initialized` handshake and protocol-level sessions; client metadata embedded per-request; MCP Apps; extension mechanism** |

Sources: [official spec](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [MCP blog RC post](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate), [Cloudflare analysis](https://blog.cloudflare.com/mcp-v2), [Victor Dibia newsletter](https://newsletter.victordibia.com/p/mcp-july-2026-update-stateless-core).

**Impact on this platform (critical):**
- `FN-001 MCP Handshake Initialization` tests behavior that the **2026-07-28 spec removes**. The test suite must become protocol-version-aware: negotiate the server's declared version and adapt expectations (handshake required ≤ 2025-11-25; absent in 2026-07-28 stateless core).
- Ecosystem scale per the MCP blog: **1,000+ community servers, 97M monthly downloads** — the server-quality problem this platform addresses is real and growing.
- New attack surfaces documented for the stateless spec ([Backslash analysis](https://www.backslash.security/blog/new-mcp-spec-opens-new-attack-surfaces)) — our security suite should add cases for per-request metadata handling and stateless replay.

## 2. International Standards (ISO/IEC / ITU-T)

| Standard | Year | Relevance to Server Evaluation |
|----------|------|-------------------------------|
| **ISO/IEC 25059** — Quality model for AI systems | 2023 | Extends the SQuaRE series (ISO/IEC 25010) with AI-specific quality characteristics. The natural framework for our 5-dimension scoring. |
| **ISO/IEC TS 25058** — Guidance for quality evaluation of AI systems | 2024 (AWI revision ongoing) | Evaluation methodology guidance; complements 25059. |
| **ISO/IEC 23053** — Framework for AI systems using ML | 2022 | Architecture-level framework for ML components. |
| **ISO/IEC 42001** — AI management systems (AIMS) | 2023 | Organizational AI governance; relevant for audit-chain traceability features. |
| **ISO/IEC 23894** — AI risk management | 2023 | Risk framework; maps to our security dimension. |
| **ITU-T F.748.57** — GenAI multimedia capability & evaluation framework | Oct 2025 | ITU-T evaluation methodology, Chinese-led contributions. |

Note: CAICT reports **10 Chinese-led AI international standardization work items in progress** (Aug 2026), including a technical report on **agent classification and capability grading** — a signal that agent-capability standards are being formalized at ITU level.

## 3. Chinese National Standards & Policy

### GB/T series (released 2025)

| Standard | Title | Date |
|----------|-------|------|
| **GB/T 45288.1-2025** | AI large-scale model — Part 1: General requirements | 2025-02-28 |
| **GB/T 45288.2-2025** | AI large-scale model — **Part 2: Testing and evaluation metrics and methods** | 2025-02-28 |
| **GB/T 45288.3-2025** | AI large-scale model — Part 3: Service capability maturity assessment | 2025-02-28 |
| **GB/T 45654-2025** | Cybersecurity — Basic security requirements for generative AI services | 2025-06-30 |
| **GB 45438-2025** | Cybersecurity — Labeling methods for AI-generated synthetic content | 2025 |
| **GB/T 45574-2025** | Data security — Sensitive personal information processing requirements | 2025 |

GB/T 45288.2 structure (from published interpretations): evaluates **understanding and generation** capability families across task scenarios, single- and multi-modal, combining **objective computation and human scoring**; designed for model providers, application providers, and consumers.

### TC260 (全国网络安全标准化技术委员会) practice guides
- **《智能体交互安全要求》** (Agent interaction security requirements) — practice guide, directly covers agent-tool interaction security.
- **《大模型一体机产品安全基本要求》** — covers model-machine product security incl. an agent layer.
- **2026 second-batch national standard demand list** includes **《生成式人工智能系统互操作安全规范》** (interoperability security for genAI systems — API interfaces, identity authentication, data protection). *This is the closest upcoming national standard to MCP-server evaluation.*

### Policy & evaluation infrastructure
- **《智能体规范应用与创新发展实施意见》** (CAC et al., 2026-05): mandates an agent development **evaluation indicator system** with monitoring and dynamic adjustment.
- **CESI "求索" high-level general capability testing** (started 2025-09; first certificates issued 2026-01), executed against GB/T 45288.2.
- **CAICT Trusted AI Agent evaluation system 2.0** (2026-04): covers platform engineering + key agent capabilities (perception, decision, generation, interaction, multi-agent collaboration).

## 4. Academic MCP Benchmarks (Direct References)

| Benchmark | Source | What It Evaluates | Relation to Us |
|-----------|--------|-------------------|----------------|
| **MCP-Bench** | Accenture, ICLR 2026 (82 citations) | LLMs on realistic multi-step tool-use tasks | Evaluates **models**, not servers |
| **MCP-Universe** | Salesforce AI Research, arXiv 2508.14704 (Aug 2025) | LLM agents across real-world MCP servers | Evaluates **models** |
| **MCPMark** | arXiv 2026 | Stress-testing realistic & complex MCP scenarios | Agent-side stress testing |
| **MCP-Atlas** | arXiv 2602.00933 (Feb 2026, 37 citations) | Large-scale tool-use benchmark | Model-side |
| **MCP-SafetyBench** | arXiv 2512.15163 (Dec 2025) | Safety of MCP agents (built on MCP-Universe) | Agent-side safety |
| Tool-description quality studies | arXiv 2602.14878 (Feb 2026) | How MCP tool descriptions affect model behavior | **Converges with our LLM-compatibility dimension** |

**Gap observation:** every major benchmark fixes the *servers* and evaluates the *model/agent*. Our platform fixes the *LLM* and evaluates the *server* (protocol compliance, performance, robustness, tool-description legibility, cross-tool consistency). This is a complementary, under-served position — and the only one aligned with server-side quality standards (GB/T 45288.2-style evaluation methodology, applied to the MCP layer).

## 5. Compliance Mapping & Action Items

### Dimension mapping

| Our Dimension | ISO/IEC 25059 / SQuaRE | GB/T 45288.2 | TC260 |
|---------------|----------------------|--------------|-------|
| Functional (7 cases) | Functional suitability / protocol compliance | Testing methodology Part 2 | — |
| Performance (3) | Performance efficiency | Metrics & methods | — |
| Security (5) | Security, reliability | Security dimension | GenAI security basic reqs (45654); agent interaction security guide |
| LLM Compatibility | Usability (for a model "user") — novel extension | (no equivalent — our differentiator) | — |
| Scenario Testing | Reliability, state consistency | Lifecycle evaluation | Agent interaction security guide |

### Action items
1. **Protocol-version-aware testing** (high priority): detect the server's declared MCP version; adapt FN-001 and transport expectations for 2026-07-28 stateless servers. Consider a "spec conformance matrix" page.
2. **Security suite expansion**: add cases for per-request metadata (2026-07-28) and stateless replay; align report wording with GB/T 45654 taxonomy.
3. **Positioning language**: describe the platform as applying GB/T 45288.2-style evaluation methodology + ISO/IEC 25059 quality characteristics to the MCP server layer — a layer not covered by existing benchmarks (which evaluate models).
4. **Watch items**: TC260《生成式人工智能系统互操作安全规范》(in development), CAICT agent grading standards, ISO/IEC 25058 revision.
