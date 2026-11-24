# ISA104 FDE source materials (instructor reference)

Two recorded evaluation training courses were delivered alongside this module.
Their original materials are **Chinese-language instructor reference** and are
kept in the local course archive; they are not student-facing content in this
English-taught module and are not uploaded to this repository.

## Lesson 1 — evaluation foundations

| Original file | What it is | Grade |
|---|---|---|
| `大模型评估基础框架.pptx` | 17-slide framework deck | Official courseware |
| `模块一_LLM-as-a-Judge.docx` | Long-form module one handout | Official courseware |
| `DeepSeek_V4.pdf` | 58-page vendor technical report | Vendor primary source |
| `llm_eval_course.zip` | Five-module evaluation code package, 38 usable files | Official teaching code |

The code package runs on DashScope (`qwen-plus` chat and a separate text
embedding model). Its `--dry-run` path uses a local character-bigram TF-IDF
retriever and makes no network call. **It is not integrated into this
application's runtime**; see the provider note below.

## Lesson 2 — evaluation system and project practice

| Original file | What it is | Grade |
|---|---|---|
| FDE seven-module course deck | 49 slides, built around one "XiaoZhu" assistant case | Official courseware |
| `小助交互Demo.html` | 122 KB pure front-end offline interaction demo, 0 network requests, 0 keys | Official teaching artefact |

The only artefact from these two lessons published in this repository is that
offline HTML page, mounted on the ISA104 Course page as an opt-in static panel.

## Evidence policy (unchanged)

1. **Primary** — official courseware, the vendor technical report, and the
   pre-generated dry-run outputs shipped with the code package.
2. **Secondary** — our own summaries, alignment notes and survey manuscript.
3. **Not evidence** — auto-generated AI "deep research" reports. Those were
   excluded from the TicNote notes library and remain excluded here.

Anything quoted from the Chinese originals must be labelled *instructor
reference* and must not be pasted into English student materials or speaker
notes, which are required to be 100% English.

## Vocabulary caution

The Agent "four layers" on slide 39 of the Lesson 2 deck are **L1 task level /
L2 trajectory level / L3 step level / L4 environment level**. Lecture 10,
Lab 5 and the 91-slide English session use **retrieval / generation / trace /
environment**. They are similar decompositions with different names and
neither is a standard. Choose one and stay consistent; the visible vocabulary
card at the end of Lecture 10 v7 and the 91-slide session records the mapping.

## Related official document (not part of FDE)

The five-page *ISA104 AI Agent Group Project Guide* is a separate official
document for the assessed group project. It defines the three phases, the
seven build steps, five risk categories, five topic directions and a Week 1-13
timeline, and states that the agent is assessed through the Week 13 live
demonstration and Q&A with marking criteria in the Week 4 **Group Project
Task Sheet**. That Task Sheet is not in our possession and no criteria are
invented here. A 20-slide instructor guidance deck
(`ISA104_GroupProject_Guidance_EN.pptx`) expands the Guide's two-line
Test/Evaluate phase into the six-step method used in this module; like the
other binaries it is instructor-facing and not stored in this repository.

## Provider note

This application uses `core/llm_client.py` -> AMAX Token Router
(`AMAX_API_KEY`, `https://ai.amaxsmp.com/v1`). The FDE code package uses
`DASHSCOPE_API_KEY` and a DashScope-compatible endpoint with a different
`chat(system, user)` signature, and its real RAG mode requires an embedding
endpoint. Whether AMAX exposes `/embeddings` is **unverified**, so no live FDE
pipeline is mounted. Only pre-generated dry-run findings are shown; see
[`docs/ISA104_FDE_DryRun_Findings.md`](https://github.com/dechang64/mcp-eval-platform/blob/main/docs/ISA104_FDE_DryRun_Findings.md).

> A real API key was found in the distributed `llm_eval_course/.env`. It must
> be rotated by the owner. No key value is reproduced anywhere in this repository.
