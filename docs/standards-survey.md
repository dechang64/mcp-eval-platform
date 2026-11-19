# Standards & Landscape Survey — MCP Server Evaluation

*Original survey: 2026-08-27. **Revised: 2026-11-19.*** Scope: MCP protocol specifications, international standards (ISO/IEC, ITU-T), Chinese national standards and guidance (GB/T, GB/Z, TC260), certification syllabi, and the 2026 LLM-as-a-Judge reliability literature. Purpose: provide **lecture context** for the ISA104 Lecture 10 / Lab 5 Track B platform and record what may and may not be claimed.

> **Framing (revised 2026-11-19).** MCP is an **industry protocol, not a standard**. This survey is a landscape document, not a compliance mapping. No graded report produced by this platform is a standards-conformant assessment, and the platform's five dimensions are an **implementation / teaching taxonomy**, not a standards classification. Earlier wording ("aligned with", "the natural framework for our 5-dimension scoring", "certifiable audit chain") has been removed — it overstated the authority of the cited documents.

---

## 1. MCP Protocol Specification Evolution

The protocol under test is fast-moving. Timeline used by the code and the lecture:

| Version | Date | Key Changes | Used by |
|---------|------|-------------|---------|
| 2024-11-05 | Nov 2024 | Original release (stdio + HTTP+SSE) | code + lecture |
| 2025-03-26 | Mar 2025 | Tool result domains, completion | code + lecture |
| 2025-06-18 | Jun 2025 | OAuth 2.1 authorization; Streamable HTTP replaces HTTP+SSE; structured tool output | code + lecture |
| 2025-08-26 / 2025-11-25 | 2025 | **Lecture** lists 2025-08-26; `KNOWN_PROTOCOL_VERSIONS` in `core/mcp_client.py` lists 2025-11-25 (tasks, elicitation, resource cache control) | **differ — verify against official changelog** |
| 2026-07-28 | Jul 2026 | Stateless core — removes `initialize`/`initialized` handshake and protocol-level sessions; client metadata embedded per-request; MCP Apps; extension mechanism | code + lecture |

Sources: [official spec changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [MCP blog RC post](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate), [Cloudflare analysis](https://blog.cloudflare.com/mcp-v2), [Victor Dibia newsletter](https://newsletter.victordibia.com/p/mcp-july-2026-update-stateless-core).

**Corrections to earlier notes:** there is no `2026-03-26` spec release — the fifth entry is `2025-03-26`. The code list has **five** entries, not six. Version strings in code are implementation data for version checks; the lecture timeline is a teaching simplification. Neither is a standard.

**Impact on this platform:**
- `FN-001 MCP Handshake Initialization` tests behaviour that the 2026-07-28 spec removes; the suite is protocol-version-aware (handshake required up to 2025-11-25, absence compliant for 2026-07-28 stateless core). `FN-008` checks that the declared version belongs to the known set.
- New stateless attack surfaces motivated `SEC-006` (request replay) and `SEC-007` (per-request metadata injection).
- Ecosystem scale per the MCP blog: 1,000+ community servers, 97M monthly downloads.

## 2. International Standards (ISO/IEC / ITU-T)

| Standard | Year | What it actually provides | Permitted use here |
|----------|------|---------------------------|--------------------|
| **ISO/IEC TS 42119-2:2025** | published 2025-11-03 | Risk-based testing process for AI systems, extending the ISO/IEC/IEEE 29119 series | General test-process logic: plan -> cases -> execution -> defect lifecycle -> report |
| **ISO/IEC 25059:2023** | 2023 | AI **quality model** and terminology (SQuaRE extension). 90.92 under revision; FDIS Ed.2 at approval | Background vocabulary only. **A quality model is not a test method and is not the basis of the five-dimension taxonomy** |
| **ISO/IEC TS 25058** | 2024 (AWI revision ongoing) | Guidance for quality evaluation of AI systems | Background |
| **ISO/IEC 23053** | 2022 | Framework for AI systems using ML | Architecture background |
| **ISO/IEC 42001 / 42005 / 23894** | 2023 / 2025 / 2023 | Management system / impact assessment / risk management | Governance and risk vocabulary |
| **ITU-T F.748.57** | Oct 2025 | GenAI multimedia capability & evaluation framework | Landscape |

Note: CAICT reports 10 Chinese-led AI international standardisation work items in progress (Aug 2026), including a technical report on agent classification and capability grading.

## 3. Chinese National Standards, Guidance & Policy

| Document | Title / scope | Status |
|----------|---------------|--------|
| GB/T 45288.1-2025 | AI large-scale model — Part 1: General requirements | 2025-02-28 |
| **GB/T 45288.2-2025** | AI large-scale model — Part 2: Testing and evaluation metrics and methods | 2025-02-28. Metadata (26 pp., SAC/TC 28) verified on `openstd.samr.gov.cn`; **clause text requires online preview** |
| GB/T 45288.3-2025 | Part 3: Service capability maturity assessment | 2025-02-28 |
| GB/T 45654-2025 | Cybersecurity — Basic security requirements for generative AI services | Issued 2025-04-25, effective 2025-11-01 |
| GB 45438-2025 | Labeling methods for AI-generated synthetic content | 2025 |
| GB/T 45574-2025 | Sensitive personal information processing requirements | 2025 |
| GB/Z 185.6-2026 / 185.7-2026 / 242-2026 | Agent interaction, agent tool calling (incl. tool-description standardisation), agent technical requirements | National standardisation **guidance**, not conformity standards |
| GB/Z 236-2026 / 253-2026 | RAG-related guidance | Guidance |
| 20262604-Z-469 | GenAI system interoperability security | **In development** |

### Provenance warning on GB/T 45288.2 clauses (added 2026-11-19)

Public secondary interpretations of Section 6.2 disagree on the direction of the dataset-size figure: some state **>= 200 items per capability**, others **<= 200**. The same secondary sources describe "3 independent runs per tool" and Section 6.5 (cross-model validation, scoring rules translated into prompts, human review, stable interfaces). **None of these clause texts has been verified against the official standard in this survey.** Until the official text is obtained:

- cite only the verified **metadata** (title, publication / implementation date, page count, TC);
- label every clause statement as **"secondary interpretation — verify against official text"**;
- do not write "the standard requires >= 200" or "the standard requires <= 200" into teaching material, a paper, or a report;
- do not promote an engineering heuristic (Spearman rho >= 0.8, MAE thresholds, three-run averaging, calibration set size) into a standards requirement. Section 6.5 sets no such numeric threshold.

### TC260 practice guides

- 'Guidelines for Secure Deployment and Use of Agents' — published.
- **'Agent Interaction Security Requirements' (2026-07-29) — draft for comment.** Never cite as an in-force requirement.
- The 2026 second-batch national standard demand list includes 'Generative AI System Interoperability Security Specification' (in development).

### Policy & evaluation infrastructure

- 'Implementation Opinions on the Standardised Application and Innovative Development of Agents' (CAC et al., 2026-05): calls for an agent evaluation indicator system with monitoring and dynamic adjustment.
- CESI "Qiusuo" high-level general capability testing (from 2025-09; first certificates 2026-01), executed against GB/T 45288.2.
- CAICT Trusted AI Agent evaluation system 2.0 (2026-04).
- ISTQB **CT-AI v2.0** and **CT-GenAI**: certification syllabi, not standards. Useful for the teaching distinction between testing **of** AI and testing **with** AI.

## 4. LLM-as-a-Judge Reliability (added 2026-11-19)

The Lab 5 Track A route uses LLM judging; Track B is deliberately execution-based. The 2026 literature is relevant to how the judge may be described in teaching.

| Layer | Representative first-hand sources | What is established |
|-------|-----------------------------------|---------------------|
| Bias taxonomy & agreement | Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, arXiv:2306.05685 (>80% agreement with humans, **but the same paper lists the biases**); Wang et al., *FairEval*, arXiv:2305.17926; Li et al., *AlpacaEval 2.0*, arXiv:2404.04475 (length-controlled win rate; correlation 0.94 -> 0.98); Wataoka et al., arXiv:2410.21819 (self-preference, perplexity mechanism); Gu et al., *A Survey on LLM-as-a-Judge*, arXiv:2411.15594 (human-machine agreement ~61.54%) | Bias is structural, not an edge case |
| Conditional consistency | *No Free Labels*, arXiv:2503.05061 (kappa 0.42-0.48 -> 0.68-0.78 with human references); healthcare scoping review arXiv:2605.25273 (agreement 0.66-0.96, kappa 0.59-0.88, r 0.40-0.94; switching from "at least one expert" to "expert majority" moves agreement 0.83 -> 0.51) | Human labels are **not** an unconditional gold standard |
| Bias-mitigation measurement | TMLR 2026, arXiv:2604.23178 (style/format bias effect 0.10-0.76; position bias <= 0.04, i.e. negligible on tested models) | Do not repeat "position bias is always dominant" without qualification |
| **Version drift** | arXiv:2607.08535, 2610.32986, 2609.34198 (2026 preprints; migrating stale calibration raises comparison error from 3.8 to 19.5 percentage points; ~200-call stratified anchoring audit can diagnose) | Freeze snapshot + prompt + rubric; re-baseline on change |
| Benchmark validity | *Are We Done with MMLU?*, arXiv:2406.04127 (6.49% of questions erroneous; virology subset ~57%); OpenAI, *Why SWE-bench Verified no longer measures frontier coding capabilities*, 2026-02-23 (27.6% subset / 138 tasks, 59.4% of tests flawed, gold patches reproducible -> stops reporting the score, recommends SWE-bench Pro); LiveBench, arXiv:2403.07974 | Saturation, contamination and test defects are distinct failure modes |
| Test oracle & generated cases | test-oracle SLR, arXiv:2607.05031 (IEEE Access); ISTQB CT-GenAI | An LLM cannot be its own oracle; generated reference answers require human verification against the KB |
| Construct validity / scale | arXiv:2511.04703 (NeurIPS 2025, 445 benchmarks); arXiv:2606.30219 (373 studies, eight evidence streams) | Goodhart effects, instability decomposition, version-locked evaluation |

**Evidence hygiene.** A widely blogged "large-scale judge evaluation" preprint (arXiv:2606.19544) was **withdrawn by arXiv Admin on 2026-11-03**; its kappa figures and judgement counts must not be cited. A TicNote-generated "deep research report" recycled OpenAI's 27.6% SWE-bench audit-subset figure as a "position-bias flip rate" and invented a co-signing institute; it is archived as a negative example only. Both cases are why this survey records provenance per claim rather than per document.

## 5. Academic MCP Benchmarks (Direct References)

| Benchmark | Source | What It Evaluates | Relation to Us |
|-----------|--------|-------------------|----------------|
| MCP-Bench | Accenture, ICLR 2026 | LLMs on realistic multi-step tool-use tasks | Models, not servers |
| MCP-Universe | Salesforce AI Research, arXiv:2508.14704 | LLM agents across real-world MCP servers | Models |
| MCPMark | arXiv 2026 | Stress-testing realistic MCP scenarios | Agent-side |
| MCP-Atlas | arXiv:2602.00933 | Large-scale tool-use benchmark | Model-side |
| MCP-SafetyBench | arXiv:2512.15163 | Safety of MCP agents | Agent-side safety |
| Tool-description quality | arXiv:2602.14878 | How tool descriptions affect model behaviour | Converges with our LLM-compatibility dimension |

**Gap observation:** major benchmarks fix the *servers* and evaluate the *model/agent*; this platform fixes the *LLM* and evaluates the *server*. Complementary position — but a research gap, **not** a claim of standards alignment.

## 6. Action Items (revised)

1. **Verify the GB/T 45288.2-2025 clause text** through the official preview before any clause-level claim (highest documentation priority).
2. **Unify the three version tables** — code `KNOWN_PROTOCOL_VERSIONS`, Lecture 10 five-revision teaching line, and the student kit's `PLATFORM_README.md` note (`2026-03-26` is a typo for `2025-03-26`) — against the official changelog.
3. **Unify denominators** — 2026-08 15-case comparative run vs today's 18-case suite; never rescale.
4. **Keep compliance language out of docs and reports** — describe documents as context; TC260 draft stays marked; no "certifiable audit chain".
5. **Teaching only**: add the five judge failure modes, calibration discipline, and the "test oracle" rule to Lecture 10 notes / Lab 5 A3 (already done in v5); do not present heuristics as thresholds from a standard.
6. **Watch items**: TS 42119-3 / -7 / -8 (in development), 20262604-Z-469, CAICT agent grading, ISO/IEC 25058 revision, ISO/IEC 25059 Ed.2.
