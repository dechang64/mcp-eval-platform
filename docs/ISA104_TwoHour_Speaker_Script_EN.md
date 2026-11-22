# ISA104 | Two-Hour English Session | Complete Speaker Script

**Evaluating AI Agents: From Test Design to Release Decisions**

Two-hour English session | 91 slides | 2 activities | 1 break | approximately 12,481 spoken words.

> The verbatim script for every slide is also embedded in the PPTX speaker notes. Timing codes are cumulative clock positions. Evidence lines are for instructor auditing and are not read aloud.

## Run of show

| Block | Clock | Minutes | Content |
|---|---|---|---|
| Opening | 0-8 | 8 | Failure case, learning outcomes, run of show |
| Part 01 | 8-25 | 17 | One discipline, two directions; standards map |
| Part 02 | 25-45 | 20 | Designing the evidence |
| Activity 1 + break | 45-58 | 13 | 6-min case-writing, debrief, 5-min break |
| Part 03 | 58-78 | 20 | Rules, judges, rubrics, drift, calibration |
| Part 04 | 78-90 | 12 | Data engineering and quality |
| Part 05 | 90-110 | 20 | RAG, agent evaluation, workflow runtime and execution evidence |
| Part 06 | 110-120 | 10 | SOP, reporting, evidence hygiene, close |

## Slide-by-slide script

### Slide 01 · 0:00-0:01 · Evaluating AI Agents: From Test Design to Release Decisions

*OPENING | COVER | ISA104  /  TESTING AND EVALUATION OF AI AGENTS*

Good morning. For the next two hours I want to do one thing properly: connect the craft of software testing to the craft of evaluating AI agents.

Most courses treat these as separate subjects. One subject says: here is how you design a test case, here is a decision table, here is a test oracle. The other subject says: here is a benchmark, here is an LLM-as-a-judge, here is a score. In practice, on a real product, they are the same job. If the test condition is vague, no judge will save you. If the trace is truncated, no metric will save you.

So the question I keep returning to today is very simple. When an agent gives a wrong answer, can you say which layer failed, and can you prove it? Not guess. Prove it, with evidence that somebody else can re-run.

**Evidence:** Course framing; first-hand transcripts 01 and 02; book ch.3-4

---

### Slide 02 · 0:01-0:03 · One failure, five possible causes

*OPENING | SPLIT | OPENING  /  THE PROBLEM*

Let me start with a failure. A user asks a personal assistant to find a thirty-minute slot with their manager next Wednesday morning, book a meeting room, and remind them the day before. The assistant creates the calendar event and reports success. It never books the room. It never creates the reminder.

Now look at the two columns. An answer-level metric sees a fluent, plausible, well-formatted confirmation. A pointwise judge might well give that four or five out of five, because the language is good and nothing looks wrong. The user sees a broken task.

The real cause could be in at least five places. Maybe the intent decomposition dropped a sub-task. Maybe the time slot was parsed incorrectly. Maybe the wrong tool was selected. Maybe the tool parameters were wrong. Maybe an API call timed out and nothing retried. Maybe the reminder service fired but silently failed.

That is the whole motivation for this session. One score tells you that something is wrong. It does not tell you what to fix. And if you cannot say what to fix, you cannot write the regression case that proves it stayed fixed.

**Evidence:** Second-lecture first-hand transcript 00:06:53-00:12:37; MCP code audit findings

---

### Slide 03 · 0:03-0:04 · The same failure, seen from three distances

*OPENING | SPLIT | OPENING  /  THREE OBSERVATION DISTANCES*

Before we go further, look at the same failure from three distances. At the answer level you have a confident, wrong sentence, and you can score it without knowing anything else about the run. At the trace level you can see that the agent called two tools, skipped retrieval and never saw the refund record, so the failure now has a location.

There is a third distance that most evaluation courses skip. Suppose a workflow had already written a record into a customer system before it died. The sentence can be generated again. That write cannot. Keep this distinction in the back of your mind, because in Part Five we will enlarge the unit of test from an answer to an execution, and the same question comes back: what evidence do I actually have?

The habit I want you to build today is simple. Ask what a claim rests on before you ask how to score it. We will repeat that move in every part of the session.

**Evidence:** Session framing; first-hand lecture transcripts on answer-level vs trace-level observation

---

### Slide 04 · 0:04-0:05 · By the end of two hours you should be able to

*OPENING | CARDS | OPENING  /  LEARNING OUTCOMES*

Six outcomes, and I will come back to each of them at the end.

First, distinguish. You should be able to say whether a method is about using AI to test software, or about testing an AI system, and place a standard, a framework and a teaching taxonomy at the correct layer. That sounds pedantic until you see a team claim compliance with something that was never a standard.

Second, design. Given one vague sentence of a requirement, you should be able to write a verifiable test condition, name the case-design method you used, and state what the oracle is.

Third, build. You should be able to construct a three-layer dataset where every record is executable, the queries look like real users, and the quality control is written down.

Fourth, measure. You should be able to decide what to score with a rule, what with a semantic metric, and what needs a judge, then calibrate that judge and freeze its version.

Fifth, localise. For RAG and for agents, you should be able to say which layer failed and write a Bad Case record that a developer can act on.

And sixth, decide. You should be able to apply a release gate and say honestly what counts as evidence and what does not.

**Evidence:** Course-level outcomes written for this session

---

### Slide 05 · 0:05-0:07 · Learning outcomes, restated as defensible claims

*OPENING | CARDS | OPENING  /  WHAT YOU MUST BE ABLE TO DEFEND*

The six outcomes on the previous slide are written as abilities, but I want to restate them as things you could defend in a review. Understanding is not observable. An artefact is.

By the end you should be able to put three things on a table. First, a test condition, a case record and a named oracle that came out of a vague requirement. Second, a calibrated judge with a frozen prompt, a frozen rubric and a recorded model snapshot, so somebody else can reproduce your score. Third, a short release report that separates first-hand evidence from generated commentary.

Notice that none of these is a score. A score is an output of the system; an artefact is something a reviewer can audit. That is why the lab asks you to hand in cases and reports rather than a single number.

**Evidence:** Learning outcomes for this session; ISA104 Lab 5 deliverables

---

### Slide 06 · 0:07-0:08 · How the 120 minutes are spent

*OPENING | FLOW | OPENING  /  RUN OF SHOW*

Here is the shape of the two hours. We spend eight minutes on the failure case, seventeen on the map of the subject, twenty on designing evidence, then an activity and a short break. The second hour is measurement, data engineering, systems, and the release decision.

There are two short activities where you will actually write something, and a five-minute break. Questions are folded into the close rather than held to the end, so please interrupt me if a distinction is unclear.

**Evidence:** Session plan for this delivery

---

### Slide 07 · 0:08-0:08 · One discipline, two directions

*PART 01 | SECTION | PART 01  /  8-25 MIN*

Part one. I want to give you the map before any of the technique, because most of the confusion I see in project reports comes from mixing up two different jobs.

**Evidence:** Section divider

---

### Slide 08 · 0:08-0:10 · Same discipline, opposite directions of use

*PART 01 | SPLIT | PART 01  /  THE CENTRAL MAP*

Here is the map. On the left, testing WITH AI: the model is the tool. It reads a requirement, proposes test conditions, drafts cases, generates automation scripts, parses a performance log, triages a defect, drafts a report. The thing being tested is ordinary software. That is the subject of the textbook on your reading list.

On the right, testing OF AI: the model or the agent is the thing being tested. We build evaluation datasets, define expected behaviour, score outputs and traces, calibrate judges, monitor drift. Our tool is the evaluation harness. That is the subject of the two industry lectures I asked you to look at.

They share a great deal. Test conditions, oracles, coverage arguments, traceability, versioning, defect records, regression sets. Those are software testing ideas. They predate large language models by decades, and this is precisely why a testing textbook is useful in an AI evaluation course.

They do not share a failure model. Conventional software fails deterministically: the same input gives the same wrong output. An AI system fails stochastically, can be right for the wrong reason, and quite often has no single correct answer at all. That last point will come back when we score ambiguous queries.

**Evidence:** Book ch.1, ch.3-8; first-hand transcripts 01 and 02; ISTQB syllabus split

---

### Slide 09 · 0:10-0:11 · Eight chapters, eight test-engineering deliverables

*PART 01 | FLOW | PART 01  /  TESTING WITH AI, ONE CHAPTER AT A TIME*

The book's eight chapters are easy to remember as a chain of deliverables. Requirements give you a test condition you can point at. Design gives you cases that carry a method name, such as equivalence partitioning or a decision table. Implementation turns them into executable scripts and generated data, with a review gate before anything is admitted. Non-functional work produces performance and security evidence tied to an explicit environment. Management keeps a traceable link from every case back to a condition. Knowledge engineering leaves behind a defect taxonomy the next project can reuse. Regression gives you a stable set, and reporting ends in a decision document rather than a dashboard screenshot.

I use this list because it stops the conversation drifting into tools. Whatever the model does, these eight artefacts still have to exist, and each one is checkable.

**Evidence:** Book chapters 1-8, table of contents and chapter cards (primary reading notes)

---

### Slide 10 · 0:11-0:12 · In 2026 the profession formalised the split

*PART 01 | CARDS | PART 01  /  AN OFFICIAL ANCHOR*

This distinction is not just a teaching device. In 2026 the certification bodies formally separated the two.

ISTQB CT-AI version 2.0 took effect on the twenty-first of April 2026, and its scope is exclusively testing AI-based systems. All the material about using AI for testing was removed from it, and material on generative AI testing and red teaming was added. CT-GenAI, approved in July 2025, is the separate certificate about testing with generative AI.

I use this as an anchor because students often assume the two-direction map is something I invented to make a lecture tidier. It is not. It is how the profession now organises the subject.

One caution, and this is a habit I want you to build today: a syllabus is not a standard, and holding a certificate is not evidence of compliance. This is professional context. It is not a normative requirement, and it must not appear in a compliance matrix.

**Evidence:** Earlier standards survey in this course; ISTQB CT-AI v2.0 / CT-GenAI

---

### Slide 11 · 0:12-0:14 · What each recorded session actually contributed

*PART 01 | SPLIT | PART 01  /  TESTING OF AI, TWO SESSIONS*

Let me be precise about what the two recorded sessions give us. The first one is mostly about the evaluation loop, benchmark pathologies, rubric design, judge failure modes and calibration. The second one is much more operational: executable case fields, a challenge layer, the anatomy of a judge prompt, retrieval metrics, agent levels, trace integrity and a seven-step procedure for standing an evaluation system up from zero.

Neither session is a standard, a regulation or an academic source. They are anonymous industry training, and every number spoken in them is an illustrative demo setting. We quote the raw transcripts as first-hand evidence of practice, and we take our formal vocabulary from the textbook and from the standards catalogues. AI-generated summaries are navigation only. The two AI-generated deep-research reports are excluded outright, and I will show you why in Part Six.

**Evidence:** TicNote first-hand transcripts, sessions 1 and 2; course evidence policy

---

### Slide 12 · 0:14-0:15 · Eight chapters, one test-engineering chain

*PART 01 | FLOW | PART 01  /  THE TEXTBOOK*

Now the textbook. Eight chapters, and I want you to see them as one chain rather than eight topics.

Chapters one and two set the context: what the authors call software engineering 3.0, the idea of a test LLM, and the model foundations. Chapter three turns a vague requirement into atomic, verifiable test conditions, using tools like MoSCoW, a risk-value matrix, dependency parsing and causal chain reasoning. Chapter four generates cases: scenarios, personas, end-to-end paths, equivalence classes, decision tables, orthogonal arrays, SCAMPER and adversarial thinking, and then reviews them. Chapter five generates scripts. Chapter six covers non-functional testing. Chapter seven is test knowledge engineering and management. Chapter eight is about the person doing the work.

Notice what chapter four already contains: classical case design, review, and adversarial thinking. We did not invent challenge layers in 2025. We renamed a practice that software testing has had for a long time.

One bibliographic note, because this tripped us up in an earlier draft. The book is by Zhu Shaomin and Xing Ying, published by China Machine Press in 2026. The English title I am using is a translation for this English-language session; there is no official English edition. Cite the Chinese original in a reference list.

**Evidence:** Book table of contents (OCR pages 2-6); bibliographic details verified in earlier course survey

---

### Slide 13 · 0:15-0:16 · Two lectures, two halves of one loop

*PART 01 | SPLIT | PART 01  /  THE TWO LECTURES*

And now the two recorded lectures. They are from the same industry training series, and they divide neatly.

The first one is about why and what. Its central claim is that the purpose of evaluation is to feed iteration, not to hand somebody a score. It explains why static benchmarks fail: contamination of public test sets, score saturation at the top, and optimisation against the leaderboard. It moves the discussion from benchmark evaluation to system-level evaluation, and it gives us the loop of assess, attribute, iterate.

The second lecture is almost entirely about how to fill in the forms. There are very few new concepts. The value is in engineering constraints: a three-layer dataset with actual field schemas, scoring bands for ambiguous queries, a five-step judge calibration procedure, retrieval metrics you can compute by hand, four levels of agent evaluation, a seven-step standard operating procedure and a release gate.

Together they give us the thesis for today: executable verification, layered localisation, quantified attribution. And I want you to hold one sentence in your head. A score is a float; an actionable attribution is the product.

We treat both lectures as anonymous industry training cases. They are not standards, not academic literature, and not a consensus. Every number in them is a demo setting. I will say that every time one appears.

**Evidence:** First-hand transcripts 01 and 02 and their close-reading notes

---

### Slide 14 · 0:16-0:17 · Five ideas that cross the boundary unchanged

*PART 01 | CARDS | PART 01  /  WHERE THEY MEET*

Five ideas cross from the textbook into AI evaluation without changing meaning.

A test condition is a verifiable statement of what must hold. The book derives it from a requirement. In our evaluation dataset it is the field called expected behaviour.

An oracle is the rule that decides pass or fail. In AI evaluation the oracle is frequently missing, and we will spend a whole slide on that. Missing is not the same as unnecessary.

Coverage. Both sources reject the idea that more cases means better coverage. Coverage means which equivalence classes and which risk classes you have touched.

Traceability. Every case points to a source passage or a business rule. Every defect points back to a case. Every fix is verified by replaying that case.

And regression. A system is not repaired when a developer says it is repaired. It is repaired when the recorded Bad Case passes again. The loop closes on evidence, not on intention.

**Evidence:** Book ch.3-4 and ch.7; first-hand transcripts 01 and 02

---

### Slide 15 · 0:17-0:19 · What a standard can and cannot tell you

*PART 01 | CARDS | PART 01  /  WHERE THE STANDARDS STOP*

A standard can tell you what to document, which quality characteristics to consider, how to structure a process and what evidence a conformity claim needs. It does not tell you that Spearman's rho must clear a particular threshold, that a calibration set has three hundred rows, or that point eight is a passing line.

The confusion is easy to understand. A heuristic is genuinely useful, it gets repeated in training courses and engineering blogs, and after a while somebody describes it as a clause. That is the authority-inflation failure mode, and it is one of the things our survey set out to document. So here is the rule for this room: name the clause number when you cite a standard, name the chapter when you cite the book, and label everything else explicitly as practice or as a teaching convention.

**Evidence:** ISA104 standards verification sheet; survey Section 9 on authority inflation

---

### Slide 16 · 0:19-0:20 · Three layers of object, three layers of authority

*PART 01 | CARDS | PART 01  /  STANDARDS MAP*

A short standards map, because I will refer to it later and I do not want anyone to confuse a standard with a teaching category.

At the model capability layer, the GB/T 45288 series from 2025 covers general requirements, metrics and methods, and service maturity. Two clauses matter to us: 6.2 on dataset requirements, and 6.5 on evaluation methods, which notably requires cross-model verification and human review when a model acts as a judge.

At the AI system testing layer, ISO/IEC TS 42119-2, published in late 2025, applies the long-standing 29119 software testing series to AI systems with a risk-driven selection of practices. Alongside it sit the 25059 quality model and the 42001, 42005 and 23894 management standards.

At the agent and tool layer, the 2026 GB/Z series covers agent interaction, tool calling and agent technical requirements, and two further GB/Z documents address RAG.

And then frameworks and law: NIST AI RMF, the EU AI Act, the domestic generative-AI security baseline, the personal information protection law. These are not test methods. They create obligations and evidence expectations. Keep the layers separate, and never claim that a teaching taxonomy is a standard.

**Evidence:** Earlier standards verification sheet and content audit in this course

---

### Slide 17 · 0:20-0:21 · Three things that are not standards

*PART 01 | SPLIT | PART 01  /  A COMMON ERROR*

Three things that regularly get promoted to standards by accident.

MCP is an industry protocol with a public changelog. It is not a standard, and official domestic commentary says plainly that protocols in this space have not converged. The five dimensions of our own platform are a teaching taxonomy we defined for this course; they are neither the nine characteristics of 25059 nor a GB/T classification. And the seven capability areas from the first training lecture are one team's working taxonomy.

All three are useful. None of them is normative. The practical rule I want you to use: state the layer, name the authority, give the status date. If you cannot do those three things, call it team practice.

**Evidence:** Standards content audit; GB/Z 185 official commentary; platform README

---

### Slide 18 · 0:21-0:22 · Five words we will use all day

*PART 01 | CARDS | PART 01  /  CHECKPOINT Q1*

Quick checkpoint before we design anything. A test condition is a checkable property of a requirement, not a case and not a user story. An oracle is the mechanism that decides pass or fail when there is no single correct answer. A case is one input together with its oracle, a source citation and a named design method. A judge is a model, a prompt and a rubric frozen together, and it is itself a system under test. A trace is the ordered record of what the system did, and if it is missing, that is a finding rather than a gap for you to fill in with a plausible story.

Take twenty seconds to say those five definitions to the person next to you. If you cannot say one of them without using the word 'quality', that is the one to come back to during the break.

**Evidence:** ISTQB CT-AI v2.0 terminology; first-hand lecture transcripts; Lab 5 task brief

---

### Slide 19 · 0:22-0:25 · Turn to the person next to you

*PART 01 | ACTIVITY | CHECKPOINT  /  90 SECONDS*

Ninety seconds with the person next to you. A colleague writes: our MCP server passed the ISO/IEC 25059 evaluation, so it is compliant with the EU AI Act. Name three separate problems with that sentence.

I will take two suggestions aloud. Listen for the three I have in mind: the layer of the object is wrong, the type of authority is wrong, and a quality model is not a conformity assessment for a piece of legislation that addresses a different entity altogether.

**Evidence:** In-class checkpoint written for this session

---

### Slide 20 · 0:25-0:25 · Designing the evidence

*PART 02 | SECTION | PART 02  /  25-45 MIN*

Part two. This is where the textbook earns its place. We are going to design the evidence before we choose a single metric.

**Evidence:** Section divider

---

### Slide 21 · 0:25-0:27 · A vague need is not yet a test condition

*PART 02 | CARDS | PART 02  /  FROM REQUIREMENT TO CONDITION*

Start with a sentence: move my weekly meeting to Friday afternoon. That is a need, not a test condition. It is context-dependent, and it hides at least four assumptions. Which meeting? Which Friday? What counts as afternoon? And what happens to the linked reminder?

The book's chapter three gives us a route. Dependency parsing reduces the sentence to a functional subject, an object, an action verb and constraints. Causal chain reasoning then exposes conflicts with other business rules; for example, if priority is computed from the deadline, moving the deadline may change priority and cause an ordering oscillation.

Then we prioritise. MoSCoW combined with a risk-value matrix: high business value and high failure risk is a must-have, low and low is a could-have.

And finally we write the condition in a form that can fail: given an existing calendar event referenced by the previous turn, the system issues an Update, not a Create, with the new time inside the stated afternoon interval. That is verifiable. Notice it says nothing about the wording of the reply. We are testing behaviour, not prose.

**Evidence:** Book ch.3 (scan p70-110); second-lecture transcript 00:38:45-00:40:09

---

### Slide 22 · 0:27-0:28 · One condition, three cases, three methods

*PART 02 | CARDS | PART 02  /  WORKED EXAMPLE*

Let us turn one condition into three cases. The condition is: for a question outside the knowledge base, the system must not invent an answer. It is checkable, bounded and says nothing about implementation.

An equivalence-class case uses a name that simply is not in the knowledge base, and the expected behaviour is an explicit refusal with no fabricated detail. A boundary case uses a name one character away from a known entity; here a clarification or a refusal is acceptable, but confidently merging the two is not. A counterfactual case deliberately alters a fact in the knowledge base and asks whether the system follows the provided evidence rather than its parametric memory.

Three cases, three named methods, one condition. If you cannot name the method that produced a case, you have written an example rather than a case, and it will not survive a review.

**Evidence:** Classical test-design methods; Lab 5 dataset categories in_kb_factual, out_of_kb, counterfactual_conflict

---

### Slide 23 · 0:28-0:30 · The old methods are still the backbone

*PART 02 | CARDS | PART 02  /  CLASSICAL CASE DESIGN*

This is the slide I most want you to photograph, because it is the one that gets skipped.

Equivalence partitioning and boundary value analysis: intent types give natural classes, and dates, time zones, token limits and empty results give boundaries. A date on the thirty-first of December referring to '5 January' is a boundary case, not trivia.

When conditions interact, use a decision table to state the rule, and an orthogonal array to sample combinations without enumerating every one. The book uses an L18 array for a multi-factor allocation rule.

End-to-end paths cover the basic flow, the alternative flow and the exception flow. A state tree identifies which nodes are worth testing.

Then systematic variation. SCAMPER gives you seven ways to mutate an existing scenario, and adversarial thinking asks you to assume the component is broken or the user is hostile.

And the last item is the one that matters most for AI: the book has a dedicated review step for generated cases. If an LLM drafts your evaluation items, a human reviews them before they enter the dataset. Every time.

**Evidence:** Book ch.4; lecture-2 challenge layer; Lab 5 case-design methods note

---

### Slide 24 · 0:30-0:31 · The test oracle problem

*PART 02 | SPLIT | PART 02  /  THE HARD PART*

Now the hard part, and the reason this course is not just a list of metrics.

An oracle is the mechanism that decides whether an observed behaviour is correct. For a calculator it is trivial: two plus two is four. For 'write me a polite refusal' or 'summarise this meeting', there may be no single correct string at all.

If you cannot define correctness, a judge model will quietly substitute plausibility. You get high scores that measure fluency, and the evaluation becomes circular: a language model is grading a language model for sounding like a language model.

There are three practical escapes. First, define expected behaviour as an executable action rather than a string: the system issues an Update, not a Create. Second, allow the reference answer to be empty, and let the rubric carry the decision. Third, when the input is genuinely ambiguous, score how the system handles uncertainty instead of scoring the answer.

This is not just an opinion. Work on the test oracle problem reports that a large share of failures in generated tests come from wrong assertions rather than from product defects, and confirmation bias in LLM judging is documented. If you remember one slide from part two, make it this one.

**Evidence:** Course survey on the test oracle problem and judge reliability; second-lecture transcript 00:39:47

---

### Slide 25 · 0:31-0:32 · When there is no reference answer, build one

*PART 02 | CARDS | PART 02  /  FOUR ORACLES*

The oracle problem sounds fatal until you notice that a reference answer is only one of four options. Expected behaviour states what the system must do rather than what it must say: 'refuses without fabricated detail' is checkable, while a golden sentence is brittle. A tool-call assertion says a named tool must or must not be called with arguments inside a declared range; that is cheap, deterministic and independent of phrasing. An invariant is a property that must hold for every output, such as no invented citation, no leaked credential, or conformance to a declared JSON schema. And for genuinely ambiguous queries we use a two-one-zero rubric with an anchor example written before we see any output.

The timing matters. Choose the oracle before you generate the outputs. Choosing it afterwards is fitting the answer to the data, and that is exactly the mistake a benchmark is supposed to prevent.

**Evidence:** First-hand lecture 2 on expected_behaviour fields; Lab 5 answer key on the 2/1/0 rubric

---

### Slide 26 · 0:32-0:34 · A three-layer test set answers three questions

*PART 02 | CARDS | PART 02  /  DATASET ARCHITECTURE*

Three layers, three questions, and the shape is not an accident.

The general capability layer asks whether the foundation has regressed. It must be a fixed subset, run through a fixed harness with fixed prompt templates, otherwise you are measuring your own configuration changes. It is a baseline reference only.

The scenario layer asks whether the product works for real users. Cover every functional module and every task. If you have production logs, sample according to the real traffic distribution; if you do not, weight by business priority and risk.

The challenge layer asks whether the evaluation itself can be trusted: edge cases, adversarial cases, ambiguous cases. Notice that this layer tests your measurement, not only your product.

And there are two diagnostic rules worth memorising. Business passes but the benchmark drops: suspect the foundation. Both normal but business is poor: suspect the business chain, especially intent recognition and tool calling. Those two rules turn one number into a location.

**Evidence:** First-lecture transcript 01:04:02; second-lecture transcript 00:25:36-00:31:20

---

### Slide 27 · 0:34-0:35 · A benchmark is not a release decision

*PART 02 | SPLIT | PART 02  /  THE RELEASE GATE*

A benchmark is not a release decision. The gate is: business metrics meet their target and no safety red line is touched. The benchmark only tells you whether the base model degraded.

Three lines keep this honest. Red line for safety, privacy and irreversible financial operations, non-negotiable. Target line for the service level agreed in the SLA. Watch line for post-launch user experience.

And three comparability constraints: fixed subset, fixed framework, fixed prompt template. If any one of those moves, a difference in scores is uninterpretable, no matter how many decimal places you print.

Let me add a warning from our own platform audit, because it is a real defect we measured, not a hypothetical. In one scoring implementation, when every performance probe failed, the code substituted a neutral fifty points. A server that failed everything scored higher than a genuinely slow but working server. A gate built on a broken score is worse than no gate at all, because it gives you confidence you have not earned.

**Evidence:** Second-lecture transcript 00:30:43-00:31:20 and 02:14:20; MCP code audit issue ledger

---

### Slide 28 · 0:35-0:37 · A case is executable only if its fields are

*PART 02 | CARDS | PART 02  /  THE SAMPLE RECORD*

Here is what an executable case looks like. Identity and context first: an id, a scene, an intent, capability tags, difficulty, source, the query and the conversation history. Source matters, because it distinguishes real logs, external benchmarks and cases you built yourself.

Then expected behaviour. This is the field that carries the oracle, and I want it to be an action wherever possible: calendar Update, not Create. That is far stronger than a reference string, because we can assert on it after the tool call.

Parameters to check: event id, time interval, attendee list.

Then a field the lecture called para_note, which is really a set of human verification points: must update the referenced event, must not create a new one, the time must fall in the afternoon, and the response must use the word change.

And finally a reference answer which is allowed to be empty. When it is empty, the judge decides against the rubric rather than by string similarity.

One administrative note: the CSV you upload in Lab 5 still has three columns. This schema is the design sheet behind each row, not a new upload format.

**Evidence:** Second-lecture transcript 00:37:47-00:41:45; Lab 5 task brief sample-record table

---

### Slide 29 · 0:37-0:38 · Read one row as a contract

*PART 02 | SPLIT | PART 02  /  A CASE RECORD, FIELD BY FIELD*

Here is how to read one row of the dataset as a contract. The identifier, category and query give you a stable identity, a declared failure family and the raw user wording; we never polish the query into a benchmark-sounding sentence, because polished queries produce flattering scores. Expected behaviour is the oracle, written as behaviour and carrying a source citation a second person can actually open. Design method and challenge layer say why the case exists and whether it belongs to the harder distribution. Source reference and notes point at the exact knowledge-base passage or transcript line, and record anything a grader needs to know to avoid a false failure.

The test I apply is simple. If a stranger cannot run this row and reach the same verdict as me, the row is not executable yet.

**Evidence:** ISA104 Lab 5 evaluation dataset schema; first-hand lecture 2 on case JSON fields

---

### Slide 30 · 0:38-0:39 · Polished queries produce flattering scores

*PART 02 | CARDS | PART 02  /  QUERY REALISM*

A dataset full of polished queries produces flattering scores, and I have seen teams celebrate that as an improvement.

Real users write fragments: actually, make it afternoon instead. They make typing errors, produce homophones, and paste in speech-recognition artefacts. They mix full-width and half-width characters. And they use unresolved references: put it there instead.

If every query in your evaluation set is self-contained and grammatically complete, you have not tested the product you shipped. You have tested a product that does not exist.

The characteristic symptom is a private dataset scoring artificially high while the public benchmark looks low. That gap is a measurement artefact. Before you interpret any score difference, go and read twenty queries at random.

**Evidence:** Second-lecture transcript 00:33:17-00:37:46; book ch.4 scenario realism

---

### Slide 31 · 0:39-0:41 · Three families of hard cases

*PART 02 | CARDS | PART 02  /  THE CHALLENGE LAYER*

Three families of hard cases.

Edge cases: a date on the thirty-first of December referring to January, a traveller in Dubai saying wake me at eight tomorrow, lunar leap days, reference resolution after a long conversation, two events in the same slot.

Adversarial cases of the safety kind: prompt injection, an instruction to invent a meeting that never existed, an attempt to extract the whole contact list, an order to delete somebody else's calendar.

Adversarial cases of the robustness kind: near-form characters, typos, encoding interference. Same intent, different surface form.

And ambiguous cases. Lexical, syntactic, referential. For these there is no single correct answer, which means that scoring answer correctness is itself a test design error. We need a different rubric, and that is the next slide.

**Evidence:** Second-lecture transcript 00:42:16-00:47:55

---

### Slide 32 · 0:41-0:42 · Three cases that break otherwise good systems

*PART 02 | CARDS | PART 02  /  DESIGNING THE CHALLENGE LAYER*

The challenge layer is where a system that scores well on the base distribution starts to fail. A multi-hop case gives you two documents that are individually harmless but jointly imply the answer; retrieval finds one and the system answers confidently from a half-evidence base. A conflict case puts a retrieved passage that contradicts parametric memory, and you watch whether the system cites the passage or quietly reverts to what it thinks it knows. An injection case puts instructions inside retrieved content instead of the user turn, and the oracle is an invariant: that instruction is data, not a command.

Keep this layer separate in your report. If you fold it into aggregate accuracy, the easy ninety percent will hide all three failures, and you will ship a system that looks strong in the slide deck.

**Evidence:** Lab 5 dataset: multi_hop, counterfactual_conflict, prompt_injection, safety categories

---

### Slide 33 · 0:42-0:44 · A 2 / 1 / 0 rubric for ambiguous queries

*PART 02 | CARDS | PART 02  /  SCORING UNCERTAINTY*

Here is the most transferable single idea from the second lecture.

For an ambiguous query, give two points if the system recognises the ambiguity, lists the plausible readings, or asks a clarifying question. Give one point if it chooses one reasonable reading and states the assumption it made. Give zero if it answers in a confident, definite tone with no acknowledgement that another reading was possible.

Look at what is being measured. Not whether the answer is correct. We are measuring whether the system handles uncertainty honestly. That is a behaviour with an oracle we can actually write down.

I will keep saying this: the two, one, zero bands are a teaching convention from one training case. They are not a standard, not a benchmark, and not an industry consensus. They are a good rubric, and they are now a required rubric in Lab 5 if you choose to add an ambiguous case.

**Evidence:** Second-lecture transcript 00:45:41-00:47:55; Lab 5 task brief ambiguity rubric

---

### Slide 34 · 0:44-0:45 · Grade this query: 2, 1 or 0?

*PART 02 | CARDS | PART 02  /  CHECKPOINT Q2*

Grade this one before I show you the bands. The query is: what did the professor say about the deadline? Two sections mention a deadline, the recording is ambiguous, and the system did not ask a clarifying question.

A two states the ambiguity, gives both plausible readings and asks which is meant; full credit, even though no single answer is supplied. A one picks one reading but signals uncertainty and cites the passage it used; defensible, but the ambiguity was never surfaced. A zero is a confident single date with a fabricated timestamp, and it stays a zero regardless of fluency, length or formatting.

Notice what we just did. The bands were fixed before we saw any output. That is the whole difference between a rubric and a rationalisation.

**Evidence:** First-hand lecture 2 on the 2/1/0 ambiguity rubric; Lab 5 answer key

---

### Slide 35 · 0:45-0:48 · Write one case that can actually fail

*ACTIVITY | ACTIVITY | ACTIVITY 1  /  6 MINUTES*

Six minutes, in pairs. A user says: actually, move it to the afternoon instead. The previous turn created a thirty-minute one-to-one on Wednesday morning.

Write one evaluation record using the schema from slide twenty. Include expected behaviour, two parameters to check, and two human verification points. State which case-design method you used.

Then add one ambiguous variant of the same query and write the two, one, zero anchors for it. One sentence on why a single reference answer would be the wrong oracle here.

Half a page. I will collect four and put two on the board. I am going to walk around, so stop me if the oracle is giving you trouble.

**Evidence:** In-class activity written for this session; adapts the Lab 5 case-design requirement

---

### Slide 36 · 0:48-0:50 · Six minutes, one case, five fields

*ACTIVITY | ACTIVITY | ACTIVITY 1  /  WHAT GOES ON THE CARD*

Here is exactly what goes on the card, so there is no ambiguity about the task. Write one checkable condition, then the raw user wording without tidying it. Choose an oracle: expected behaviour, a tool-call assertion or an invariant, and add a two-one-zero band if the query is genuinely ambiguous. Name the design method that produced the case and give a citation somebody else can open. Finally, write down the failure you expect from a good system.

That last field is the one people skip. If nothing can fail, the case is too easy, and it will not tell you anything in the lab. Work in pairs, one card per pair, six minutes. I will collect three and debrief them in front of the room.

**Evidence:** Activity 1 instruction sheet; Lab 5 six-point review checklist

---

### Slide 37 · 0:50-0:52 · What a good answer contained

*ACTIVITY | CARDS | ACTIVITY 1  /  DEBRIEF*

Let me summarise what the strong answers had in common.

Expected behaviour was an action, not prose. 'Update the referenced event, not Create' is an oracle. 'A polite confirmation sentence' is not.

The case-design method was named. Equivalence class for the intent, boundary value for the time interval, a decision table if you built the conflict case. Naming the method is part of the deliverable, because it is the only way I can see your coverage argument.

Traceability: a pointer to the business rule or conversation turn that makes the assertion true.

And an honest ambiguity band. Two points required an explicit reading or a clarifying question. 'Give a shorter answer' is a style preference, not a scoring anchor.

**Evidence:** In-class debrief notes

---

### Slide 38 · 0:52-0:53 · Three cards, three different problems

*ACTIVITY | CARDS | ACTIVITY 1  /  DEBRIEF*

Let me debrief three representative cards. Card A has a beautifully written query and no decision rule at all. It is an example, not a case; add expected behaviour before you run anything. Card B hides its oracle inside the answer, because the expected behaviour names an exact output string. That will break on the first paraphrase, so restate it as a property and keep the literal string as an anchor example instead. Card C cannot fail: the answer sits in a single obvious passage. Keep it as a smoke test, but move it out of the challenge layer.

The common thread is that all three fail at review time, not at run time. That is why the lab asks you to apply the six-point checklist before a single token is spent.

**Evidence:** Lab 5 answer key and six-point review checklist; activity debrief conventions

---

### Slide 39 · 0:53-0:58 · Back at minute 58

*BREAK | BREAK | BREAK  /  5 MINUTES*

Five minutes. When we come back, the question is: if the oracle is this hard, what exactly is a judge allowed to decide?

**Evidence:** Break slide

---

### Slide 40 · 0:58-0:58 · Rules, judges, and calibration

*PART 03 | SECTION | PART 03  /  58-78 MIN*

Part three. Measurement. We start by deciding what should not be measured by a model at all.

**Evidence:** Section divider

---

### Slide 41 · 0:58-1:00 · Rules were never obsolete

*PART 03 | CARDS | PART 03  /  DISPATCH BY DETERMINACY*

A correction to something students often take away from a first lecture on LLM evaluation. Rule-based metrics are not obsolete.

If a parsed timestamp must be in a specific format before it reaches a function, check the format with a rule. Zero cost, zero latency, no ambiguity. If the agent either called read_file with the right argument or it did not, there is nothing for a semantic model to decide. If the output must be valid JSON with required keys, use a schema check. If a safety red line has fixed criteria, use a fixed check.

The real rule is dispatch by determinacy of the verdict. Rules, semantic metrics and judges are three tools in one toolbox, not three successive eras of technology. A team that sends everything to an LLM judge pays more, waits longer, and gets a less reproducible answer.

**Evidence:** Second-lecture transcript 00:13:39-00:15:39; Lecture 10 v6 notes

---

### Slide 42 · 1:00-1:01 · Similarity is not correctness

*PART 03 | SPLIT | PART 03  /  WHAT SEMANTICS CANNOT DO*

Before we get to LLM judges, one clarification. Similarity is not correctness.

An embedding or BERTScore-type metric tells you whether two texts resemble each other. It cannot tell you whether the date is right, whether the tool call actually happened, whether a claim is supported by the retrieved passage, or whether a refusal was appropriate. A fluent wrong answer can be very similar to a fluent right answer.

A trained BERT-style judge can decide correctness, but it needs labelled data and retraining for each domain. That is expensive and does not travel well.

So use similarity as a cheap supporting signal, never as the acceptance criterion. The acceptance criterion has to be tied back to expected behaviour.

A small note on source hygiene: the automatic transcript of the lecture mis-rendered these technical terms. I have restored standard terminology here, which is exactly why we go back to the raw transcript before quoting anything.

**Evidence:** Second-lecture transcript 00:16:03-00:17:27, checked against raw transcript

---

### Slide 43 · 1:01-1:03 · A similarity score can be exactly right and still useless

*PART 03 | SPLIT | PART 03  /  WORKED EXAMPLE*

Here is my favourite small example. The reference says the refund was approved on the twelfth of May. The candidate says the refund was not approved on the twelfth of May. The cosine similarity is very high, because one token of negation barely moves the vector and the sentence structure is identical. The correct verdict is a contradiction and zero credit, and a grader built on similarity alone will happily pass it.

Use similarity for retrieval and for clustering, where being in the right neighbourhood is the job. Never use it as the decision rule for a factual claim. The ordering in this course is always the same: deterministic checks first, model judgement second.

**Evidence:** Textbook chapters on test oracles; first-hand lecture 1 on rule-based vs model-based scoring

---

### Slide 44 · 1:03-1:04 · A rubric has four required elements

*PART 03 | CARDS | PART 03  /  THE RUBRIC*

A rubric is not a list of adjectives. It has four required elements.

One: the dimensions. Correctness, completeness, instruction following, expression — choose the ones the scenario actually needs.

Two: a verifiable definition for each. Correctness means the facts, the numbers and the logic hold. 'The answer feels accurate' is not a definition. If you cannot describe how a second person would check it, it is not a definition.

Three: an anchored scale. Describe every point on the zero-to-five scale in words. Zero is an empty or unusable reply, five fully satisfies, and the bands in between need their own descriptions. The more precise the anchors, the more stable the scores.

Four: attribution labels. Factual error, missing key information, logical contradiction. A low score without a label cannot drive a fix.

And emit structured JSON. Free text is pleasant to read and useless to aggregate across three hundred cases.

**Evidence:** First-lecture transcript 01:47:16-01:51:58

---

### Slide 45 · 1:04-1:05 · Four elements on one page

*PART 03 | CARDS | PART 03  /  A RUBRIC, WRITTEN ALL THE WAY THROUGH*

A rubric has four required elements, so let me write one all the way through. The criterion is grounding: every factual claim must be supported by the supplied passage and unsupported claims must be absent. The bands are two for all claims supported, one for a minor unsupported detail with the main claim intact, and zero for a material claim invented or contradicted. The anchors are one real output for each band, taken from a previous run and stored with the rubric version. And the procedure says show the passage first, then the output, then the band, and require a one-sentence justification, with the prompt, rubric and model snapshot frozen together.

Without anchors, a rubric is just a vocabulary. With anchors and a repeatable procedure it becomes an instrument, which is the only thing you can calibrate.

**Evidence:** First-hand lecture 1 on rubric elements; Lab 5 answer key on band anchors

---

### Slide 46 · 1:05-1:07 · Six elements of a judge prompt

*PART 03 | CARDS | PART 03  /  JUDGE PROMPT*

Six elements of a judge prompt, and notice they are not the same as the four rubric elements. They complement them.

Give the judge a role and a boundary: senior quality inspector for this product, decide only from the material provided, do not speculate about missing information. Inject the task context, who the user is, what the task is, because a research request and a casual chat do not share a standard. Break down the dimensions with an anchor for each.

Then the single most effective trick: require the judge to analyse before it scores. Make it output its reasoning first. That one instruction reduces arbitrary scoring and improves agreement with human raters.

Require structured output. And provide the full input: system prompt, user context, the current request, a reference answer if one exists, the model reply, and the actual tool-call trace. For an agent, a judge without the trace is judging a story, not an execution.

That last point is the bridge to part five, where we will see what happens when the trace is truncated.

**Evidence:** Second-lecture transcript 00:19:28-00:24:25 and 02:28:46

---

### Slide 47 · 1:07-1:08 · Six lines, each one preventing a known failure

*PART 03 | CARDS | PART 03  /  A JUDGE PROMPT, LINE BY LINE*

Here is the six-element judge prompt, explained by what each line prevents. The role line says you are grading grounding, not helpfulness, so a fluent off-task answer does not get rewarded. Evidence first puts the passage before the output, so the judge cannot reconstruct the answer from its own memory. The rubric and its bands go inline with anchors, which limits drift between runs. Reason before score forces analysis first and a single band afterwards, which blunts length bias. A strict output shape makes post-processing deterministic. And an abstention line says return ungradable when the passage is insufficient, rather than fabricating a verdict on a broken case.

Freeze that prompt string with a version tag. A silent edit to one line invalidates every score you collected before it, and you will not notice until somebody tries to reproduce your table.

**Evidence:** First-hand lecture 2 on judge prompt structure; survey on judge failure modes

---

### Slide 48 · 1:08-1:10 · Pointwise, pairwise, listwise

*PART 03 | CARDS | PART 03  /  THREE FORMS*

Three forms, three decisions.

Pointwise scores one response against a rubric. Use it for daily regression and dashboards. It gives an absolute score, which is convenient and dangerous in equal measure, because people start comparing absolute scores across months without checking whether anything changed.

Pairwise compares two responses, as in an arena. Use it for version decisions and preference alignment. Run both A-B and B-A orders, and keep only the verdicts that agree. A flip is not noise to be averaged away; it is evidence of position bias.

Listwise ranks a set. Use it when the decision is selection and only the ordering matters.

And whatever the form, post-processing is mandatory: fill missing dimensions, clamp out-of-range scores, clean attribution labels, drop labels on perfect scores, and normalise invented labels back to the agreed vocabulary. A judge is a model, not a database.

**Evidence:** First-lecture transcript 01:46:24 and 02:14:37; second-lecture transcript 00:17:00

---

### Slide 49 · 1:10-1:11 · A judge is also a model under test

*PART 03 | CARDS | PART 03  /  FIVE FAILURE MODES*

A judge is also a model under test. Five failure modes, and I want you to be able to name all five.

Position bias: swapping A and B changes the verdict. Run both orders, keep only consistent verdicts, report the flip rate as a quality metric of your evaluation process.

Length or verbosity bias: a longer answer is read as more careful. State in the prompt that length earns no reward, and control length in comparisons.

Self-preference: a judge favours output from its own family or its own style. Use cross-family judges and never let the same series grade itself.

Score drift: same input, same rubric, different score on a different day. Average three runs, keep a frozen calibration set, and version everything.

And generic judge bias: the judge's own capability and disposition introduce systematic error. Use multiple judges and human spot checks.

Three of these were already in the course deck. The two lectures added verbosity bias and drift, and that is a good example of industry practice filling a gap in a textbook treatment.

**Evidence:** First-lecture transcript 02:01:10-02:13:10; survey reading on judge reliability

---

### Slide 50 · 1:11-1:12 · Swap the order and watch the score move

*PART 03 | CARDS | PART 03  /  POSITION BIAS, MEASURED*

Position bias is not a vibe, it is a measurement. Take a set of pairwise comparisons, present A then B for half of them and B then A for the other half, and change nothing else. Compute how often the first-presented answer wins, how often the two orders agree, and Cohen's kappa against a human calibration set. What you usually see is a preference for the first position, with longer answers benefiting disproportionately when they appear first. The control is to randomise order, report both orders and average over repeated runs. Never report a single-pass pairwise win rate.

One caveat, because this is where authority inflation creeps in: every threshold you might attach to kappa or MAE here is a teaching convention. The standards do not specify one.

**Evidence:** Survey Sections on position, length and self-preference bias; kappa and Spearman monitoring as engineering practice

---

### Slide 51 · 1:12-1:14 · Four reasons a score moves when nothing changed

*PART 03 | SPLIT | PART 03  /  DRIFT*

Why does a score move when the product has not changed? Four reasons.

A hosted judge endpoint is silently upgraded behind a stable model name. Temperature above zero makes scoring non-deterministic. Someone changes 'must' to 'should' in the rubric, and a whole distribution shifts. Or the entire scale becomes stricter or more lenient.

The last one is subtle and important. If everything shifts up by one point, the ranking is unchanged, so a rank correlation will tell you nothing is wrong. That is why we need more than one agreement statistic.

The operational rule: treat the model snapshot, the prompt and the rubric as a single versioned dependency. Freeze it, record it on every report, and never compare scores across versions without saying so.

**Evidence:** First-lecture transcript 02:05:24-02:13:10

---

### Slide 52 · 1:14-1:15 · Three runs, nothing changed, three different means

*PART 03 | SPLIT | PART 03  /  DRIFT IS A MEASUREMENT*

Drift is a measurement, not a feeling. Imagine three runs on a frozen set with the prompt, model snapshot, temperature and rubric all held constant. The first gives a mean of nought point eight one. A week later the second gives nought point seven eight; a silent model update is the first suspect, not your data. The third gives nought point eight four, which means sampling variance is already large enough to hide a real regression.

So record the model snapshot, a prompt hash, the rubric version, the seed, the date and the per-case scores, not just the mean. Monitor joint agreement and error rather than a single aggregate. A moving mean without a frozen reference is not evidence of anything. And to repeat the standing rule: these three numbers are illustrative demo settings, not measurements from a published study.

**Evidence:** First-hand lecture 1 on score drift; survey on calibration and model-snapshot freezing

---

### Slide 53 · 1:15-1:17 · Calibrate the judge before you trust it

*PART 03 | CARDS | PART 03  /  CALIBRATION*

Calibrate before you trust. The five-step admission from the second lecture: sample across every business scenario, have humans score to the written standard, have the candidate judge score the same batch, compute agreement, then set a threshold and tune the judge prompt until it passes.

Now the statistics, and this is where many teams make a category error. Kappa measures agreement on discrete grades or categories. Spearman measures rank order. They answer different questions and cannot replace each other. Add mean absolute error to catch a uniform shift of the whole scale, because Spearman is blind to it.

Keep a frozen, human-labelled calibration set and re-run it before every release and every judge version change. It is the control chart of your evaluation system.

And be honest about cost: three runs per case roughly triples cost and latency. That is a budget trade-off, not a standard requirement.

**Evidence:** First-lecture transcript 02:09:11-02:13:10; second-lecture transcript 00:17:40-00:19:25

---

### Slide 54 · 1:17-1:18 · Five steps before you trust a judge

*PART 03 | FLOW | PART 03  /  A CALIBRATION SET IN ONE AFTERNOON*

You can build a calibration set in an afternoon. Sample a stratified slice from every category, including the challenge layer; small is fine, unrepresentative is not. Have two humans grade independently with the rubric and anchors visible, and record their disagreements instead of averaging them away. Freeze the labelled rows together with a prompt hash, a rubric version and a model snapshot as one immutable bundle. Run the judge, compute agreement and error, and read every disagreement by hand. Then admit the judge only for the categories where it agrees with the humans, and route the rest to deterministic rules or back to people.

Calibration is admission control for a measuring instrument. It is not a one-off accuracy check you perform once and then forget.

**Evidence:** First-hand lecture 1 on the five-step admission and calibration procedure; survey RQ-I

---

### Slide 55 · 1:18-1:18 · Data engineering and quality

*PART 04 | SECTION | PART 04  /  78-90 MIN*

Part four. We have a dataset design. Now: how do you grow it without quietly destroying it?

**Evidence:** Section divider

---

### Slide 56 · 1:18-1:20 · Augmentation and synthesis are not the same operation

*PART 04 | SPLIT | PART 04  /  GROWING THE SET*

Two operations, often confused.

Augmentation has a seed. You paraphrase while keeping the intent and the slots unchanged, you perturb parameters like time, place and person, or you escalate difficulty with noise and distractors. The augmented case keeps its seed ID, so you can trace it back.

Synthesis may have no seed. Strategy comes first: generate an assessment-point profile or a catalogue of error-prone logic, including unseen topics and extreme boundary traps. Sample two or three directions at random, then generate per direction. Assign a completely new ID.

Why strategy first? Because unconstrained generation produces hundreds of near-identical reformulations. Variety has to be designed, not hoped for.

And why does ID lineage matter? Because when a case fails, you need to know whether it came from a real log, a paraphrase of a log, or an invented scenario. Those are three different evidence strengths, and a report that mixes them silently is misleading.

**Evidence:** Second-lecture transcript 00:48:36-00:52:36; book ch.7 synthetic data

---

### Slide 57 · 1:20-1:21 · One admission rule applied to four generated cases

*PART 04 | CARDS | PART 04  /  WORKED EXAMPLE*

Augmentation and synthesis are not the same operation, so let us apply one admission rule to four generated cases. The rule is: admit only if the oracle is checkable, the source is openable and no near-duplicate already exists. Case one is a counterfactual with an exact knowledge-base line and a behaviour oracle; admit it. Case two is a fluent query whose oracle is 'the answer should be good'; reject it, there is no decision rule. Case three is valid but has ninety-four percent token overlap with an existing row; reject it as a near-duplicate, because it inflates the score without adding coverage. Case four is a safety case citing a page that no longer resolves; hold it for repair rather than grading around it.

Generate freely and admit sparingly. Keep the admission log, because it is part of the evidence that your set was built rather than merely collected.

**Evidence:** First-hand lecture 2 on data quality gates; Lab 5 six-point review checklist

---

### Slide 58 · 1:21-1:22 · Generate freely, admit sparingly

*PART 04 | CARDS | PART 04  /  QUALITY GATE*

Generate freely, admit sparingly.

A separate LLM acts as a quality inspector across several dimensions. The training demo suggested an acceptance line of zero point eight. Two veto rules override any score: a hallucinated fact, or an invalid item — unsolvable, multiple valid answers, missing options — is discarded.

For a thousand-plus items, full human review is not feasible. Inspect all low-scoring cases and sample the high-scoring ones.

And the principle, which I would like you to write down: not more data, but broader coverage and higher quality. 'More complete' beats 'more numerous'.

Two honesty notes. The zero point eight threshold and the three-to-five-hundred-case regression set in that demo are one team's settings, not norms, and not statistical conclusions. And this quality gate is the same control as the book's case-review step, described in a different vocabulary. That is the two-direction map showing up again.

**Evidence:** Second-lecture transcript 00:53:00-00:56:55 and 01:12:04; book ch.4.3.4

---

### Slide 59 · 1:22-1:24 · Scaling from 10 to 1000 changes the distribution

*PART 04 | SPLIT | PART 04  /  DISTRIBUTION COLLAPSE*

Here is a failure mode that only appears at scale. Ten to a hundred generated cases look diverse. At a thousand, tone and sentence structure converge. The set is large and narrow.

The control is a three-dimensional quota over scene, intent and expression style. Stop generating a cell once its quota is filled.

Then three levels of deduplication: lexical, semantic, and finally an LLM check for cases that differ in wording but test the same assessment point.

Why does this matter statistically? Because a thousand near-identical cases inflate apparent confidence. Your effective sample size is far smaller than your row count, and any confidence interval you compute on the row count is fiction.

**Evidence:** Second-lecture transcript 00:54:07-00:56:55

---

### Slide 60 · 1:24-1:25 · What scaling from 10 to 1000 quietly does

*PART 04 | SPLIT | PART 04  /  DISTRIBUTION COLLAPSE*

Here is what scaling does when nobody watches the distribution. A human-written seed set of ten rows has six factual cases, two out-of-knowledge-base, one multi-hop and one safety case, each with a reason. Generate a thousand rows from that seed and you get nine hundred and ten factual cases and a thin tail everywhere else, because the generator reproduces the easy majority and smooths off the hard edges. Reported accuracy then rises from nought point seven two to nought point eight nine without a single change to the system. The score moved because the set moved.

The control is to hold category proportions fixed, report per-category scores, and keep a frozen holdout that no generator has ever seen. Again, these are illustrative demo settings, not a measured result.

**Evidence:** First-hand lecture 2 on data distribution and quality inspection; survey on benchmark pathologies

---

### Slide 61 · 1:25-1:26 · A score is only actionable at the right granularity

*PART 04 | CARDS | PART 04  /  TAXONOMY*

A score is only actionable at the right granularity.

Overall satisfaction of eighty-six percent tells you nothing. Calendar modification at sixty-two percent tells you which team to send. Both numbers come from the same training demo, and both are illustrative.

Three axes. Capability: instruction following, factual accuracy, context understanding, reasoning, safety, tool use. Scene: a top-level scene like scheduling, then second-level tasks like create, modify, query and conflict detection; a third level only when the fix needs it. And intent: question, command, creation, role advice, chat, compound.

The intent axis is the one teams forget, because it is not visible in a product screenshot.

And the rule is not 'as fine as possible'. It is 'as fine as the fix requires'. Every extra level costs labelling effort and invites inconsistency between annotators.

**Evidence:** First-lecture transcript 01:04:02; second-lecture transcript 00:57:19-01:00:02

---

### Slide 62 · 1:26-1:27 · The same 0.86, three different decisions

*PART 04 | CARDS | PART 04  /  GRANULARITY*

A score is only actionable at the granularity of the decision it supports. One aggregate number, nought point eight six, says ship it, and hides the fact that every safety case failed while every factual case passed. Break it down by category and you get nought point nine seven factual, nought point six two out-of-knowledge-base, nought point four one multi-hop and nought point three zero safety; now a release decision is possible, and it is clearly no. Go down to the case level and you find the two failing safety rows share one root cause, a missing retrieval guard, which is a fixable defect rather than a model problem.

Aggregate for the headline, category for the gate, case for the engineer. Never let the headline make the decision.

**Evidence:** First-hand lecture 2 on metric granularity; Lab 5 report template

---

### Slide 63 · 1:27-1:29 · Instrumentation is part of the test design

*PART 04 | CARDS | PART 04  /  SIGNALS*

Explicit feedback — likes, dislikes, star ratings — is noisy and sparse. The lecturer described it as not confident. Implicit feedback localises dissatisfaction much better: follow-up rate, rewrite rate, task completion rate measured by backend tool success, mid-session abandonment, retention.

But here is the trap, and it is the most important sentence in part four. RAG and agent evaluation require intermediate data. If the trace is truncated, no trace-level metric is computable, no matter how good your rubric is.

The team admitted in the recording that their business had run for a long time with data problems and that many agent traces were cut off. I respect that honesty. It is also a direct warning to us, because we found exactly this in our own platform audit, and we will look at the measured behaviour in part five.

The lesson: instrumentation is not plumbing you add later. It is part of the test design.

**Evidence:** Second-lecture transcript 01:31:19-01:35:33; MCP code audit

---

### Slide 64 · 1:29-1:30 · What would you log?

*PART 04 | CARDS | PART 04  /  CHECKPOINT Q3*

Last checkpoint before the systems part. A user tells you the assistant made something up last Tuesday, and all you have is the final answer. What would you need to have logged? At minimum: a case identifier, the model snapshot, a prompt hash, the identifiers of the retrieved passages, tool calls with their arguments, timestamps, and the grader version. Without passage identifiers you cannot test faithfulness; without a snapshot you cannot reproduce; without a grader version you cannot compare scores.

And if those fields are absent, 'insufficient trace, ungradable' is a legitimate, useful verdict. Writing a plausible story into the gap is precisely the failure our evidence policy exists to prevent. Instrumentation belongs in test design, not in an operations ticket afterwards.

**Evidence:** First-hand lecture 2 on signals and trace fields; Lab 5 answer key on ungradable cases

---

### Slide 65 · 1:30-1:30 · Systems under test: RAG and agents

*PART 05 | SECTION | PART 05  /  90-110 MIN*

Part five. Now the object under test is a system with parts, and the whole point is to attribute failure to a part.

**Evidence:** Section divider

---

### Slide 66 · 1:30-1:32 · From one answer to one execution

*PART 05 | SPLIT | PART 05  /  THE UNIT OF TEST GETS BIGGER*

Everything so far had a fairly small unit of test: the system produced an answer, maybe with a tool call or two, and the trace lived inside one request. Now enlarge the boundary. The system is a workflow with triggers, nodes, model calls, writes to external systems, a human approval step, and a run that can last hours or days.

What changes is that side effects become real. A write to a customer system cannot be undone by regenerating the sentence that came before it, and a refund is not the same event as a refund followed by a correction. What does not change is the discipline. Condition, oracle, coverage, traceability and regression still apply; they just operate on a larger boundary. That is the whole argument of this part.

**Evidence:** Session framing; Diagrid engineering blog on long-running AI workflows (vendor primary, 2026-10-06)

---

### Slide 67 · 1:32-1:33 · Never score only the final answer

*PART 05 | CARDS | PART 05  /  RAG*

Never score only the final answer. The answer may be right because the model guessed from parametric memory, not because retrieval worked. Next week, with a different question, it fails. A correct answer is not evidence of a correct pipeline.

The chain matters. Chunk the corpus, and down-weight superseded versions and old itineraries during re-ranking so they cannot outrank the current document. Rewrite the query: resolve 'the last meeting' into a concrete date and name, otherwise you are testing retrieval on a query no real user would type. Use hybrid retrieval — keyword matching for exact identifiers like flight numbers and names, semantic search for intent — then re-rank and truncate.

You will recognise the hybrid retrieval idea from chapter seven of the textbook. Same concept, different direction of use: there it builds a test knowledge base, here it is the system we are evaluating.

**Evidence:** Second-lecture transcript 01:42:38-01:46:29; book ch.7.1 hybrid retrieval

---

### Slide 68 · 1:33-1:34 · A workflow is not a chain of answers

*PART 05 | CARDS | PART 05  /  ACTIONS ARE NOT ROLLBACKABLE*

A workflow is not a chain of answers, because its steps act on the real world. An email that has left cannot be recalled; a second message is a new action, not an undo. A payment that succeeded can be refunded, but a refund is compensation rather than erasure, and it creates its own record and its own failure modes. Stock that was decremented makes a blind re-run of the whole flow worse, not better.

The consequence for testing is direct. Your oracle has to describe actions and their state, not just the final text. 'The email was sent exactly once' is a checkable assertion. 'The answer was good' is not, and it will miss every one of these failures.

**Evidence:** Diagrid engineering blog on duplicate side effects (vendor primary, 2026-10-06); product-analysis essay as secondary discussion prompt

---

### Slide 69 · 1:34-1:35 · Four numbers you can compute by hand

*PART 05 | CARDS | PART 05  /  RETRIEVAL METRICS*

Four numbers you can compute by hand, from the worked example in the lecture. Two relevant documents exist; the top-three result contains one of them; the first relevant item is at rank three.

Recall at three is one over two, zero point five. Hit rate is one, because at least one relevant document appeared. Mean reciprocal rank is one third. And context utilisation asks whether the retrieved chunks were actually cited in the answer after re-ranking and truncation.

That last one is the interesting one. Retrieval can succeed while generation ignores the evidence entirely. And if you only score the answer, you will never see it.

These are worked examples from a training demo, not measurements from a real system. When graded relevance is available you can add NDCG.

**Evidence:** Second-lecture transcript 01:46:31-01:49:45

---

### Slide 70 · 1:35-1:36 · Faithfulness needs a defined evidence base

*PART 05 | CARDS | PART 05  /  GROUND TRUTH AND CLAIMS*

Faithfulness needs a defined evidence base.

Ground truth in three steps: write the relevance labelling specification first, then have humans label, then run a consistency check with a second round of adjudication where annotators disagree. Never start labelling without a written definition of what counts as relevant for this business.

Then decompose the answer into atomic claims. 'Your flight departs at two thirty from Terminal Three; arrive two hours early' becomes departure time, flight number, terminal, and the two-hour advice.

Generic advice is excluded from faithfulness checks. We only assess verifiable factual claims. If Terminal Three does not appear in the retrieved text, it is a hallucination.

And score abstention correctness explicitly. When the corpus has no answer, the correct behaviour is to say so. If you do not give that behaviour points, you are rewarding confident fabrication.

One open question the lecturer honestly left open: in a business RAG system, should faithfulness consider world knowledge or only retrieved text? They said their team did not consider it and acknowledged the problem. Do not present that as a settled answer.

**Evidence:** Second-lecture transcript 01:49:47-01:53:28 and 02:25:56

---

### Slide 71 · 1:36-1:37 · Generated artefacts versus facts that already happened

*PART 05 | SPLIT | PART 05  /  THE EVIDENCE-LINE ARGUMENT*

This is the point where the two halves of our course meet. Some artefacts are regenerable: connection code, the workflow definition on a canvas, condition configuration, even the model's answer. Ask again and you get another version. Some are not: whether a particular payment actually went out, which nodes had completed before the crash, and what the downstream system recorded at the time. You cannot prompt a model into producing those; you have to go and look.

If that sounds familiar, it should. It is exactly the distinction between a raw transcript and an AI-generated deep-research report. One is a record of an event, the other is a reconstruction of one. So when the execution record is missing, the honest verdict is ungradable. The runtime ledger is a primary source; a fluent narrative about the run is not.

**Evidence:** Course evidence policy; product-analysis essay (secondary, discussion prompt only); AI deep-research reports excluded

---

### Slide 72 · 1:37-1:38 · Two reports from the same run

*PART 05 | CARDS | PART 05  /  LAYERED VIEWING*

One run, two reports.

The end-to-end view goes to clients and managers: final accuracy and the release decision. One number, one verdict.

The layered view goes to engineering and evaluation: retrieval versus generation, which step, which dimension. That is where localisation happens.

Do not mix them. A manager report full of per-layer diagnostics obscures the decision; an engineering report reduced to one accuracy number makes the defect unfindable.

And red-line findings go at the top of both, regardless of how good the aggregate score looks.

**Evidence:** Second-lecture transcript 01:53:31-01:55:21 and 02:15:04

---

### Slide 73 · 1:38-1:40 · Four levels, not four points on one scale

*PART 05 | CARDS | PART 05  /  AGENT LEVELS*

Four levels, and they are not four points on one scale.

L1 is the task: end-to-end success and sub-task completion, judged by the final executed state, not by the reply text. L2 is the trace: step efficiency as actual steps over optimal steps, detours, loops, invalid call rate, and error recovery rate after a failure. L3 is the step: tool selection correctness and parameter-field parsing accuracy, validated per tool because every tool has different parameters.

Then there is an environment layer, which is not L4. It covers mock fidelity: conflicts, exceptions, boundary data, empty results.

And here is a detail I rather like. The lecturer corrected their own slide during the recording, saying they had mislabelled L3 while editing. A secondary AI-generated report on the same lecture then renumbered the environment layer as L4, inventing a level the lecturer never used. Two small errors, two good teaching examples: slides can be wrong, and AI-generated secondary material can quietly add structure that was never there.

**Evidence:** Second-lecture transcript 01:57:43-02:11:13 and the excluded AI deep-research report

---

### Slide 74 · 1:40-1:41 · When a flow dies halfway, what can it tell you?

*PART 05 | CARDS | PART 05  /  THREE QUESTIONS FOR A RUNTIME*

So here are three test conditions for the runtime itself. Where did the flow stop? A task-level error message is not enough; you need the last completed node and the state of the node in flight. Which results are uncertain? A step whose success receipt never came back is neither a success nor a failure, and it must be marked unknown and checked against the downstream system. What must never run twice? Payments, notifications and account creation need a stable execution identity, and ideally an idempotency key the downstream service also accepts.

Add a fourth question for the customer: can the record be exported, migrated and kept under a chosen data-residency policy? Auditability is a testable property here, not a marketing word. Each of these needs an oracle before you can grade anything.

**Evidence:** Diagrid release and engineering blog (vendor primary, 2026-10-06); n8n SAP investment blog on audit trails and data sovereignty (vendor primary, 2026-05-12)

---

### Slide 75 · 1:41-1:42 · Not every failure is partial credit

*PART 05 | SPLIT | PART 05  /  SCORING RULES*

Not every failure deserves partial credit. For an ordinary task with three sub-tasks, two completed gives two thirds. But anything involving money or an irreversible action scores zero when wrong — the training example was ordering the wrong coffee, which cannot be un-ordered.

And per-tool validation must be designed by a human from the actual business. The number of parameters and the validation standard differ from tool to tool. A framework supplies the plumbing; it does not supply the rules.

For online observation, watch safety as the compliance floor and experience as the gap between what users perceive and what the model can actually do.

These are rules from one training demo. The principle transfers; the specific red lines must come from your own domain.

**Evidence:** Second-lecture transcript 01:59:45-02:10:25

---

### Slide 76 · 1:42-1:43 · Two kinds of pause, only one is designed

*PART 05 | CARDS | PART 05  /  PLANNED WAITS, UNPLANNED CRASHES*

There are two kinds of pause and only one of them is designed. A human-approval step persists its progress and resumes when the approver comes back; the workflow expected to stop, so its state is deliberate. An unplanned crash is different: a worker dies or a container is evicted mid-run, and without checkpointing the flow starts again from node one, repeating every earlier side effect.

In October twenty twenty six, a Dapr Workflows integration for n8n began checkpointing each node, so completed nodes stay completed and recovery resumes at the failure point. That is vendor documentation, primary for product behaviour but not a standard and not independent evidence. And crucially it does not solve everything: a charge that succeeded just before the crash but was never recorded as completed may still be retried. Recovery and idempotency are different guarantees, and a good test separates them.

**Evidence:** Diagrid release 2026-10-06 and engineering blog; Diagrid's own stated limitation on unrecorded successful side effects

---

### Slide 77 · 1:43-1:44 · Check that you have a trace before you score one

*PART 05 | CARDS | PART 05  /  TRACE INTEGRITY*

This is the concrete counter-example I promised. We ran a read-only audit of the open MCP evaluation platform and measured three behaviours.

A malformed JSON request was accepted with HTTP 202 and then never answered. With keep-alive, the client can wait indefinitely. Any score computed with a timeout on that case is meaningless.

A path-traversal payload caused the server process to exit with code one after roughly three point two seconds; the event stream reset and the trace stopped mid-step.

And in one code path a timeout was recorded as a pass. A single false positive like that contaminates the entire A/B comparison built on that run.

So the rule: trace integrity is a precondition, not a metric. Give every probe an absolute deadline, verify the trace is complete, and only then compute error recovery or step efficiency.

No production system was modified in that audit. Everything was observed in a local, read-only run, and the findings are documented in the course issue ledger.

**Evidence:** MCP platform code audit: protocol probe results and issue ledger

---

### Slide 78 · 1:44-1:45 · When a retry is a second charge

*PART 05 | SPLIT | PART 05  /  IDEMPOTENCY*

Here is the sharpest version of the problem. Node seven charges a card, the charge succeeds, and the process dies before the runtime records node seven as complete. Naive recovery resumes from the last durable checkpoint, which is node seven, and the card is charged twice. The control is to bind each node execution to a stable identity, workflow execution plus node identifier, and to propagate that same identity downstream when the service accepts idempotency keys.

But keep the honest boundary in view. Durable execution guarantees recovery of the ledger; it does not guarantee correctness of the external world. You still query, reconcile, and label unresolved states as unknown. Reliable execution is not 'never repeat'. It is a mechanism for reducing repeats and handling uncertain outcomes, which is exactly the kind of claim a test should be able to falsify.

**Evidence:** Diagrid engineering blog on the idempotency ledger and its stated limitation (vendor primary, 2026-10-06)

---

### Slide 79 · 1:45-1:47 · Four layers, one Bad Case record

*PART 05 | CARDS | PART 05  /  ATTRIBUTION*

Four attribution layers. Intent: was the intent recognised and the slots extracted correctly? Retrieval: was the right evidence recalled and the stale version excluded? Generation: hallucination, or ignoring a stored preference. Execution: tool failure, workflow bug, missing fallback.

A reminder that never fires and gives no feedback is both a bug and a product design defect. That distinction matters because the fix belongs to two teams.

And the Bad Case record has eight fields: case ID, date, source version, the problem described from both the user's and the judge's view, the attribution layer and sub-item, severity, fix status, and the regression sample ID.

That last field is the one that closes the loop. Without it, a fix is an intention. Our own audit issue ledger has essentially the same structure, which is a nice moment of industry practice and our engineering method agreeing independently.

**Evidence:** Second-lecture transcript 01:35:36-01:42:33; MCP code audit issue ledger

---

### Slide 80 · 1:47-1:48 · Four fields that turn a run into evidence

*PART 05 | CARDS | PART 05  /  THE EXECUTION RECORD IS THE PRIMARY SOURCE*

What turns a run into evidence are four groups of fields. A node ledger gives you ordered identifiers with started, completed or unknown status and timestamps; that is the trace at workflow granularity. An execution identity gives you one stable run identifier plus a per-node identity, without which you cannot detect a duplicate side effect or compare two recoveries. Side-effect receipts tell you what the downstream system acknowledged versus what was merely attempted, and the gap between those two is where incidents live. An environment fingerprint records the workflow definition version, model snapshot, prompt hash, credential scope and deployment mode, because without it no regression claim is meaningful.

Export the raw execution record before you write any report. The report is a reading of that record, never a substitute for it.

**Evidence:** Course trace-integrity framework; Diagrid engineering blog; n8n vendor documentation on executions and audit trails

---

### Slide 81 · 1:48-1:49 · A ten-node workflow dies at node eight

*PART 05 | CARDS | PART 05  /  WORKED EXAMPLE*

Let us apply the four-layer attribution to a workflow. Ten nodes: webhook, fetch customer, AI agent, update CRM, generate document, send email, human approval, publish, notify and archive. The worker is evicted during node eight. Nodes one through five have durable receipts. Node six sent an email but its receipt is missing. Node seven was legitimately waiting on a human approval.

Now the four layers. At task level, did the business outcome complete at all? At trace level, which nodes are durably recorded? At step level, which node produced a duplicate or uncertain effect? At environment level, why was the worker evicted? The verdict is not 'partially failed'. It is: five confirmed, one unknown, one planned pause, one environment cause, two nodes never started. An answer-level metric sees one unsuccessful run. The ledger sees four distinct findings.

**Evidence:** Four-layer attribution from first-hand lecture 2; Diagrid engineering blog example (vendor primary)

---

### Slide 82 · 1:49-1:50 · Introducing Track C: workflow runtime evaluation

*PART 05 | FLOW | PART 05  /  TRACK C IN LAB 5*

This gives us a natural third lab track. Track A is the answer layer and RAG, where you evaluate what the system said and what it cited. Track B is the tool layer and the MCP server, where you evaluate the protocol surface. Track C is the execution layer, where you evaluate whether the run left behind a record you can trust.

The question is deliberately narrow: after an injected crash, can you prove which actions happened, which are unknown and which must not be repeated? You can do the core analysis from an exported execution record, so running n8n locally is an extension, not a prerequisite, and nobody needs a cloud account or a real payment provider. The deliverable is a defect report with an execution ledger, an oracle for each side effect and a two-one-zero band for ambiguous states. Track C is now the third alternative route inside Lab Five, bundled in the student kit as a zero-install folder. It is not a separate lab module, and it does not replace either of the other two routes.

**Evidence:** ISA104 Lab 5 Track C kit and design brief; Lab 5 Track A and Track B structure

---

### Slide 83 · 1:50-1:50 · From score to decision

*PART 06 | SECTION | PART 06  /  110-120 MIN*

Last part. We have measurements and attributions. Now: what do we actually tell somebody to do?

**Evidence:** Section divider

---

### Slide 84 · 1:50-1:52 · How to stand up an evaluation system from zero

*PART 06 | FLOW | PART 06  /  SEVEN-STEP SOP*

Seven steps, from the second lecture. Define what you are evaluating: model, product or agent. Derive the taxonomy from the feature list, not from a borrowed diagram. Build a minimal set and get the pipeline running end to end before you scale anything. Choose metrics by taxonomy and by determinacy. Establish a frozen baseline. Automate only after you understand the manual loop. And then iterate the mechanism itself, because data, taxonomy and standards all evolve with the product.

This is one team's standard operating procedure. It is not a standard and not a certification process.

But I do like their closing observation: every small product iteration is also an evaluation-system upgrade. Change the product form, and the dataset, taxonomy and rubric all have to move with it.

**Evidence:** Second-lecture transcript 02:11:47-02:13:45 and 02:30:53

---

### Slide 85 · 1:52-1:53 · A report is a decision document

*PART 06 | CARDS | PART 06  /  REPORTING*

A report is a decision document, not a score dump.

Conclusion first, red-line indicators above the aggregate score. Be explicit about offline-online calibration: an offline score rising while online metrics stay flat is normal, not an error. Map the two, and feed real traffic back into the regression set so its distribution follows reality.

Every Bad Case record needs an attribution and a fix recommendation. A list of low scores with no owners is not a report.

And state the versions on every page: model snapshot, judge prompt, rubric, dataset version, harness version. Without those, two reports are not comparable, however similar the charts look.

**Evidence:** Second-lecture transcript 02:15:04-02:16:37

---

### Slide 86 · 1:53-1:54 · One page that a reviewer can argue with

*PART 06 | SPLIT | PART 06  /  A GATE YOU CAN DEFEND*

A release gate is a documented decision rule applied to frozen evidence, so here is the one-page version. Freeze the dataset hash, prompt hash, rubric version, judge model snapshot, workflow definition version and execution identifiers. Report by layer: base distribution, challenge layer, safety category and runtime-evidence completeness, each separately, with no single aggregate hiding anything. State your conventions explicitly: point eight is our teaching threshold, not a standard clause and not an industry norm; say it on the slide and in the report. Then write the decision: ship, hold, or ungradable, with the failing case identifiers and an owner for each fix.

A report without a decision is a dashboard. The point of all this machinery is that somebody can disagree with you on the evidence rather than on the vibe.

**Evidence:** First-hand lecture 2 on the release gate and seven-step SOP; Lab 5 report template

---

### Slide 87 · 1:54-1:55 · What you are allowed to cite

*PART 06 | CARDS | PART 06  /  EVIDENCE HYGIENE*

Last technical slide, and it is a rule for everything you write in this course.

Cite first-hand sources: the raw transcripts, the textbook, the standards catalogues, and our own reproducible probe results. Quote them and date them.

Secondary AI-generated summaries are usable as navigation but not as authority. They contain terminology packaging and they repeat transcription errors. Verify every technical term against the raw transcript.

Never cite the AI-generated deep research reports from the recording platform. One invented an institution and repurposed an unrelated percentage as if it belonged to the lecture. The other cited the course's own summary link as a reference, attributed it to an unverifiable author, and quietly added a fourth agent level the lecturer never used.

And every number from the two lectures — zero point eight, the two-one-zero bands, eighty-six versus sixty-two percent, three to five hundred cases, Recall at three equals zero point five — is a spoken or demo setting. Label it illustrative. Never present it as a norm, and never write it into a standards matrix.

**Evidence:** Evidence-hygiene rules established across the course research package

---

### Slide 88 · 1:55-1:56 · Three labels, and one thing you never do

*PART 06 | CARDS | PART 06  /  EVIDENCE HYGIENE, ONE RULE*

Three labels and one prohibition. First-hand means raw transcripts, the execution ledger, official standards catalogues, and vendor documentation when the claim is about that vendor's own product behaviour; quote these with a date and a locator. Second-hand means AI-generated summaries and the product-analysis essay we used as a discussion prompt today; navigation only, and verify every term before it reaches a slide. Excluded means the AI-generated deep-research reports. One invented an institution and repurposed an unrelated percentage; another cited our own summary link back to us as a reference and invented a fourth agent level.

The prohibition is the one to take away. Never let a generated narrative stand in for a record of what happened. That rule governs the survey, the release report and Track C, and it is the reason a runtime ledger is worth testing at all.

**Evidence:** Course evidence policy; survey Sections 10.3 and 10.4 on failure morphologies and corrections on the record

---

### Slide 89 · 1:56-1:58 · Six sentences to take away

*PART 06 | CARDS | PART 06  /  TAKEAWAYS*

Six sentences, one per learning outcome.

The purpose of evaluation is to feed iteration. A score is a float; an actionable attribution is the product.

Testing with AI and testing of AI share conditions, oracles, coverage, traceability and regression.

Design the evidence before choosing the metric, and state the oracle or admit you do not have one.

Dispatch scoring by determinacy, and calibrate and version the judge like any other dependency.

For RAG and agents, score the layers, and verify trace integrity before computing a single trace metric.

Ship on business metrics plus red lines, and cite only what you can trace to a first-hand source.

**Evidence:** Session synthesis

---

### Slide 90 · 1:58-1:59 · Your lab starts where this session stops

*PART 06 | CLOSING | CLOSE  /  ASSIGNMENT AND QUESTIONS*

Your lab starts where this session stops. In Lab 5 you will add at least five cases of your own to the thirty-row dataset, at least one from the challenge layer, each with a source citation and a named case-design method, and you will apply the six-point review checklist before uploading.

There is one discussion I want you to write up. Inject a timeout with no retry into an agent trace, then state what the task level, the trace level and the step level would each observe, and explain why an answer-level metric would miss it entirely.

Reading: chapters three, four and seven of the textbook, the standards map, and the survey reading list on judge reliability.

Questions now, or bring me a real failing case in the lab. A real failing case is a much better starting point than any slide I have shown you today. Thank you.

**Evidence:** ISA104 Lab 5 task brief; session close

---

### Slide 91 · 1:59-2:00 · Four lectures said "evaluation". They meant four objects.

*PART 06 | CARDS | REFERENCE CARD  /  PRIOR ISA104 VOCABULARY*

One last card, and it is a reference card rather than new content. Four earlier ISA104 lectures used the words evaluation and five dimensions, and they were not talking about the same object. Lecture 4 evaluated governance: the Five Pillars of Responsible AI, the EU AI Act risk tiers, NIST AI RMF, red teaming and model cards. Lecture 5 evaluated RAG systems: noise robustness, negative rejection, information integration and counterfactual robustness, with four failure sites. Lecture 6 evaluated agent components: planning, tool use, end-to-end success, safety and efficiency, and introduced MCP. Week 9 evaluated the human-system interaction: formative and summative studies, utility and usability, SUS, ISO 9241-11, and confound controls such as within versus between subjects.

This session evaluates the AI system and the evidence it leaves behind. So keep three things straight. First, Week 9's evaluation and our evaluation have different objects, and a metric does not travel between them. Second, four different lists of five exist in this module, and none of them is the ISO/IEC 25059 quality model or the NIST AI RMF characteristics. Third, two numbered outcomes sets exist: Session LO1 to Session LO6 belong to this session, Lab LO1 to Lab LO6 belong to Lab 5, and the official module outcomes remain A to E. Also, the two agent-evaluation surveys are different papers: arXiv:2503.16416 is Yehudai et al., cited in Lecture 6, and arXiv:2507.21504 is the other survey on the Lecture 10 references slide.

Use this card at the start of a revision session, or print it for your group project. It is deliberately the final slide so that every slide-number pointer in the Lab 5 brief and the Track B and Track C kits still points to the right page.

**Evidence:** ISA104 L1 / L4 / L5 / L6 / Week 9 course packs; ISA104_w1w9_conflict_audit.md (instructor copy)

---
