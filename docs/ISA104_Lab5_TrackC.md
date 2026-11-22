# ISA104 Lab 5 — Track C (workflow runtime evaluation)

Track C is the **third alternative route inside Lab 5**, not a separate Lab 6.
It is zero-install: students evaluate the *evidence a run left behind*, not how
well they can draw a workflow on a canvas. It carries the same 100-mark
equivalence as Tracks A and B, and like them it is **formative and ungraded at
module level**.

## What students receive

`ISA104_Lab5/6. ISA104_Lab5_TrackC_workflow_kit/` contains a README, a workflow
description, a case set (C01-C12 across four layers) and an execution sample
(2 executions / 10 nodes). The sample is a teaching fixture with local mocks
only: no real credentials, mail, messages or payments are involved.

The student-facing JSON deliberately keeps `generated_report_narrative.text` —
a fluent, plausible account of what the run supposedly did. It is a trap: a
generated narrative is not an execution record. The kit strips all instructor
fields (`instructor_only`, `planted_defects`, `answer_pointers`,
`do_not_plant`, `instructor_note`) before distribution.

## The method

1. Rebuild a **node ledger** from the execution record.
2. Classify each node as **confirmed / unknown / never-started**.
3. Separate a side-effect receipt from a claim that a side effect happened.
4. Decide whether the run is idempotent and whether the trace is complete.
5. Apply the case set C01-C12 and the shared 2/1/0 ambiguity rubric.
6. State a release decision with an explicit "what the evidence cannot show".

This is the same discipline as Tracks A and B: state the test condition and the
oracle, control one variable, record every setting, and do not cite a generated
summary as primary evidence.

## Where it is taught

Part 05 (slides 65-82) of the [two-hour English session](ISA104_TwoHour_Session.md)
carries the workflow-runtime line. The instructor-only answer key with the
field-level defect mapping is deliberately **not** in this repository or in
the student kit.

## Provenance

The design was prompted by a public article describing an n8n workflow
experiment. It was verified against first-hand runtime behaviour before being
adopted, and on the module leader's instruction it was merged into Lab 5 as
Track C rather than issued as a new lab.
