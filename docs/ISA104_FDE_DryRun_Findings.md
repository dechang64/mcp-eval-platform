# Pre-generated FDE dry-run findings (no API calls)

All numbers below come from `outputs/summary.md` shipped inside the Lesson 1
code package. They are **stored outputs of a completed `--dry-run`**, not a
live evaluation performed by this web application. Showing them requires no
model call, no API key, no subprocess and no embedding endpoint.

## Satisfaction report, 16 samples

| Version | Samples | Overall mean | Satisfaction | Dissatisfaction |
|---|---|---|---|---|
| Old | 16 | 1.12 | 0.0% | 100.0% |
| New | 16 | 4.38 | 93.8% | 6.2% |

## Dimension means

| Dimension | Old | New |
|---|---|---|
| Correctness | 2.00 | 4.88 |
| Completeness | 1.19 | 4.75 |
| Compliance | 2.31 | 4.88 |
| Expression / experience | 3.06 | 4.50 |

## By core capability

| Capability | Old mean | New mean | New satisfaction | Change |
|---|---|---|---|---|
| Task execution | 1.00 | 4.00 | 100.0% | +3.00 |
| Information lookup | 1.20 | 4.40 | 100.0% | +3.20 |
| Content generation | 1.33 | 4.00 | 66.7% | +2.67 |
| Reasoning / decision | 1.14 | 4.14 | 85.7% | +3.00 |
| Knowledge Q&A | 1.00 | 4.50 | 100.0% | +3.50 |
| Casual conversation | 1.00 | 5.00 | 100.0% | +4.00 |

## The teaching point

> Aggregation: `min`; **min vs mean label disagreement affects 62.5% of samples**.

A single aggregate hides a failing subgroup. On slide 23 of the Lesson 2 deck,
an "86% overall satisfaction" figure masks a "62% local collapse" in one
category. The 62.5% figure here is the same failure mode expressed as a
label-consistency rate. Use both when teaching why per-case results and a
layered report matter more than one headline number.

The only low-score attribution in the new version is one completeness case:
`PA-07`, where a single-dish request was treated as a two-dish plan and shared
ingredients and portion sizes were not coordinated. It is a good worked example
of an actionable Bad Case record: the observation, the affected dimension and
the reason are all named.

## What these numbers are NOT

* Not a live run of this application.
* Not a benchmark of any model served by the AMAX Token Router.
* Not an ISA104 mark, rubric or assessment weight. Lab 5 is formative; the
  module assessment is In-class Test 35 + Group Demo 65.
* Not evidence that the FDE pipeline can run here. The DashScope provider,
  the `chat(system, user)` signature and the unverified AMAX embedding
  endpoint are documented in
  [`docs/ISA104_FDE_Source_Materials.md`](https://github.com/dechang64/mcp-eval-platform/blob/main/docs/ISA104_FDE_Source_Materials.md).

Chinese-language originals are instructor reference only; see the index page.
