# ISA104 — Two-Hour English Session: Evaluating AI Agents

*Standalone teaching asset; it is a principles lecture, not a revision of
ISA104 Lecture 10. Schedule TBC — no delivery date is published.*

**Title**: *Evaluating AI Agents: From Test Design to Release Decisions*
**Format**: 120 minutes, **91 slides**, two activities, one 5-minute break,
approximately 12,481 spoken words. Every slide carries a verbatim English
speaker note; the [complete script](ISA104_TwoHour_Speaker_Script_EN.md) is
also printable as a DOCX in the instructor course pack. The final slide is a
visible **Prior ISA104 Vocabulary** reference card.

## One discipline, two directions

| Direction | Source material | Question it answers |
|---|---|---|
| Testing **WITH** AI | Zhu Shaomin & Xing Ying, *Large-Model-Driven Software Testing*, China Machine Press, 2026, ISBN 978-7-111-80383-6 (8 chapters) | How LLMs change test engineering: requirements -> test conditions -> cases -> scripts -> non-functional testing -> management -> knowledge engineering |
| Testing **OF** AI | Two recorded industry training sessions (first-hand transcripts, 2h33m + 2h37m) | How to evaluate LLM / agent systems: data -> scoring -> calibration -> RAG / agent layers -> attribution -> release gates |

The authoritative anchor is the ISTQB split between **CT-AI v2.0** (effective
2026-04-21, scope narrowed to testing AI-based systems) and **CT-GenAI**
(approved 2025-07-25, testing WITH GenAI). Five classic testing ideas survive
in both directions: test condition, oracle, coverage, traceability, regression.

## Run of show (120 minutes, 91 slides)

| Block | Clock | Minutes | Slides | Content |
|---|---|---|---|---|
| Opening | 0-8 | 8 | 1-6 | Failure case, six Session LOs, run of show |
| Part 01 | 8-25 | 17 | 7-19 | Two directions, ISTQB split, book map, two-course division, Standards Map, three "not standards", Checkpoint Q1 |
| Part 02 | 25-45 | 20 | 20-34 | Test conditions, classic case design, four oracles, three-tier dataset, sample fields, challenge tier, 2/1/0 ambiguity rubric, Checkpoint Q2 |
| Activity 1 + break | 45-58 | 13 | 35-39 | 6-minute case writing, 2-minute debrief, 5-minute break |
| Part 03 | 58-78 | 20 | 40-54 | Similarity worked example, dispatch by determinacy, Rubric, judge prompt, position bias, drift, five-step calibration |
| Part 04 | 78-90 | 12 | 55-64 | Augmentation vs synthesis, quality gates, distribution collapse, metric granularity, Checkpoint Q3 |
| Part 05 | 90-110 | 20 | 65-82 | RAG chain and retrieval metrics, four-layer attribution, **9-page workflow runtime line** |
| Part 06 | 110-120 | 10 | 83-91 | Seven-step SOP, reporting, evidence hygiene, six takeaways, assignment, Q&A, visible vocabulary card |

Timing codes are continuous from `0:00` to `2:00` with no gaps.

## Learning outcomes (Session LO1–Session LO6)

1. Distinguish the two directions and place standards, frameworks and teaching taxonomies at the right layer.
2. Turn a vague requirement into a verifiable test condition and state its oracle and method.
3. Build a three-tier dataset with executable fields, authentic queries and a quality-check policy.
4. Dispatch scoring by determinacy, then calibrate and version the judge.
5. Locate a defect at the retrieval / generation / trace / environment layer and write an actionable bad case.
6. Apply a release gate, read a layered report, and say what may be cited.

They are stated on slide 4 and recalled one by one on slide 89. **Session
LO1–LO6 are not the same set as Lab LO1–Lab LO6 or module LO A–E.**

## Prior ISA104 vocabulary (final visible slide)

Four different "five dimensions" are in circulation across Weeks 1–9 and
Lecture 10: the Week 4 Five Pillars, the Lecture 10 five teaching dimensions,
this platform's five implementation dimensions, and the Week 6 agent-evaluation
list. Week 9's HCI evaluation (SUS / ISO 9241-11) evaluates a different object
from the system-test evaluation used here. Two different surveys are also in
play: **arXiv:2503.16416** (Yehudai et al., cited in Week 6) and
**arXiv:2507.21504** (cited in Lecture 10). They must not be merged.

## Evidence policy (applies to the whole session)

| Tier | Material | Permitted use |
|---|---|---|
| Primary | Two first-hand transcripts; book contents and chapter OCR; official standard catalogues; our own protocol probes | Citable, with dates |
| Secondary | Course AI summaries | Navigation only; all technical terms re-checked against the transcript (ASR mis-recognised terms such as BERTScore) |
| **Banned from citation** | Both AI-generated "deep research" reports | The first fabricated a consortium and repurposed percentages; the second cited the course's own AI-summary CDN link, dressed blogs up as academic sources and invented an L4 tier |
| Teaching convention | 0.8 release line, 2/1/0 rubric, 86% vs 62%, 300-500 items, Recall@3=0.5, MRR=1/3 | Always labelled **lecturer's spoken example / demo setting**; never written as a standard clause, an industry consensus or a measured result |

The lecturers' self-descriptions differ between the two recordings, so the
material is treated as **anonymous industry practice** throughout: no
institution and no job title is attributed. The English book title above is a
translation of the Chinese title, not an official English edition.

## Standards and teaching boundaries

The session's Standards Map has three layers: model capability
(GB/T 45288.1/.2/.3-2025), AI-system testing (ISO/IEC TS 42119-2:2025,
ISO/IEC 25059:2023, ISO/IEC 42001 / 42005 / 23894) and agent / tool
(GB/Z 185.6/.7-2026, GB/Z 242-2026, GB/Z 236 / 253-2026). NIST AI RMF,
EU AI Act Articles 9 / 11 / 12 / 15, GB/T 45654-2025 and PIPL / GB/T 35273
are frameworks and law, **not testing standards**.

Three things are explicitly declared **not standards**: MCP is an industry
protocol; this platform's five dimensions are a custom teaching taxonomy, not
the nine characteristics of ISO/IEC 25059; and the lecturers' capability
dimensions are a team classification. The release gate, the seven-step SOP and
the red / target / observation lines are **single-team practice** and are kept
out of the Standards Map.

## Relation to this repository and to Lab 5

- Classic case-design methods (Part 02) map to Lab 5 Part 3, its
  `expected_behaviour` / `para_note` sample template and its mandatory 2/1/0
  ambiguity rubric.
- **Part 05 (slides 65-82), the workflow runtime line, maps directly to Lab 5
  Track C** — the zero-install route shipped in
  `ISA104_Lab5/6. ISA104_Lab5_TrackC_workflow_kit/`. Track C is part of Lab 5,
  not a separate Lab 6.
- Trace completeness maps to the MCP code audit ledger and the protocol probes:
  `202` with no response, timeout mis-scored as `passed`, and an SSE reset after
  `os._exit(1)`.
- Evidence hygiene maps to the four-layer credibility framework and the
  reproducibility package behind the *Judge-as-Examinee* survey.
- The ISTQB split matches the wording already used in Lecture 10 v7.

The PPTX and DOCX are deliberately **not** stored in this repository: they are
instructor-facing binaries and ship with the course pack. This repository holds
the English script and this overview so the teaching material is discoverable
and diffable.
