# SPEC: Light Skills Core Workflow & Socratic Repair

**Status:** ACTIVE  
**Repository:** `LightDevCoder/skills`  
**Primary references:** current `mattpocock/skills` implementations of `ask-matt` and `grilling`  
**Supersedes as execution authority:** `.scratch/light-skills-lean-refactor/spec.md`  
**Scope:** targeted repair of `ask-light` and the Socratic family, plus closure of previously identified integration/ownership gaps  
**Completion state:** local commit created, then STOP and wait for human review

---

## 1. Why This SPEC Exists

The Lean Architecture refactor succeeded at making `SKILL.md` smaller and establishing better package ownership, but two core user-facing capabilities are still materially below the intended design.

### Problem A — `ask-light` is too narrow

Current `ask-light` behaves mainly like:

```text
user wording
→ Skill-map / pattern matching
→ availability check
→ recommend a Skill
```

That is useful, but it is not the intended Light equivalent of Matt Pocock's `ask-matt`.

The desired behavior is a **workflow advisor and router**:

```text
inspect current situation
→ understand project/workflow stage
→ explain what is already done and what is missing
→ recommend the next Skill and why
→ wait for user agreement
→ execute the accepted Skill
```

It must understand workflows, not merely Skill names.

### Problem B — Socratic interaction was over-constrained

The current Socratic family was optimized around one frontier decision at a time.

That is not the desired interaction.

The intended behavior is closer to Matt Pocock's current `grilling`:

```text
compute the current frontier
→ ask the actionable frontier as a round
→ give each question multiple concrete options
→ give a recommended answer with reasoning
→ wait for the user's batch response
→ update the decision tree
→ compute the next frontier
```

The user should gain both:

- efficiency from answering several independent decisions in one turn;
- better thinking from seeing alternative choices and the agent's recommendation.

This SPEC repairs those two product-level gaps.

---


# 1.1 Priority Model

This SPEC contains three priority levels.

## P0 — Core product repairs

These are the primary reasons this SPEC exists and must receive the deepest implementation and interaction testing:

```text
ask-light
→ workflow advisor / navigator / router / approval-to-execution

socratic family
→ grilling-style frontier rounds
```

Do not declare this SPEC complete unless both are genuinely fixed.

## P1 — Known functional-closure gaps

These were discovered during the previous human review and must also be resolved before completion:

```text
ask-light root discovery
Light first-party provenance
project-clarify continuous-session parity
project-init declared-capability availability
reviewer-contract single ownership
```

These are smaller than P0 but are not optional follow-up debt.

## P2 — Final architecture / hygiene checks

Before the local commit, verify and repair where necessary:

```text
stale migration/runtime-reference ambiguity
remaining prose-coupled tests in touched areas
host compatibility claims
reference-ownership regressions
```

Do not turn P2 into another repository-wide cleanup project.


# 2. Planning Authority

Before implementation, retire the previous ACTIVE status of:

```text
.scratch/light-skills-lean-refactor/spec.md
```

Do not delete the previous SPEC or its records.

Mark it clearly as completed/superseded for execution purposes and point it to this SPEC.

Create the new active work area:

```text
.scratch/light-skills-core-flow-repair/
├── spec.md
├── issues/
└── results.md
```

This SPEC is the **only active planning authority** until this repair is implemented and locally committed.

Do not continue unfinished ideas from previous repair tickets unless this SPEC explicitly includes them.

---

# 3. Scope

## 3.1 Full modification allowed

The following Skills may be redesigned as necessary to satisfy this SPEC:

```text
ask-light
socratic
clarify
project-clarify
```

This includes their:

- `SKILL.md`
- local references
- scripts/helpers
- metadata
- tests

The implementation must still preserve the Lean Architecture principle:

> `SKILL.md` remains the minimal executable interface; supporting detail remains Skill-owned and progressively disclosed.

---

## 3.2 Integration-only

The following may receive **minimal compatibility changes only** if required by the repaired behavior:

```text
decision-map
project-init
project-spec
project-tickets
implement
project-review
review-loop
release-workflow
agent-config
```

Do not redesign them.

If they already expose the information `ask-light` needs, consume it rather than changing them.

Two specific integration-only repairs are explicitly allowed by this SPEC:

```text
project-init
→ verify declared relevant Light capabilities are discoverable / available

review-loop / repository docs
→ establish one canonical reviewer-contract owner and make other copies human-facing summaries or pointers
```

Keep those changes narrow.

---

## 3.3 Out of scope

Do not use this repair to modify unrelated Skills.

In particular, do not reopen the repository-wide Lean pass, reference-size cleanup, release workflow, or general metadata normalization.

Existing user-approved changes, including the previously approved `recap` exception, remain as-is unless the user gives new instructions.

---

# 4. Reference Behavior, Not Text

Use the current Matt Skills as behavioral references:

```text
ask-matt
grilling
```

Extract the useful interaction and workflow ideas.

Do not copy their wording or force Light into Matt's exact repository architecture.

For `ask-light`, the important reference idea is:

> know the flow and the current situation, not merely the catalog.

For `socratic`, the important reference idea is:

> ask the current frontier in rounds, with choices and recommendations.

Light remains its own system.

---

# 5. `ask-light`: Redefine the Product

`ask-light` is the user-facing **Light workflow advisor, navigator, and router**.

It must support three related modes without requiring three separate Skills.

---

## 5.1 Mode A — Situation / project advisor

When invoked in or around a project, `ask-light` should inspect enough local evidence to understand the current stage.

Relevant evidence may include, when present:

```text
Git repository state
docs/agents/light-project.md
docs/agents/issue-tracker.md
AGENTS.md / CLAUDE.md
current ACTIVE SPEC
.scratch/* effort state
current tickets and their completion state
existing implementation changes
review results / acceptance state
```

Do not read the entire repository blindly.

Inspect only the evidence needed to answer:

```text
What is this project trying to do?
What stage is it currently in?
What has already been completed?
What is blocking or logically next?
Which Light Skill best owns that next step?
```

The analysis must be based on project evidence, not lexical keyword ranking alone.

---

## 5.2 Recommend the next Skill with reasoning

The normal advisor response should tell the user, naturally and concisely:

- what the current situation appears to be;
- what has already been completed if relevant;
- the recommended next Skill;
- why that Skill fits **now**;
- why obvious neighboring alternatives are not the best next step, when that distinction matters.

Example behavior:

```text
The project already has a stable SPEC, but there are no implementation tickets yet.

I'd use `$project-tickets` next. It owns the SPEC → executable-work split and will preserve blockers/dependencies.

I would not jump to `$implement` yet because the implementation boundaries have not been created.
```

Do not force a rigid template when a shorter answer is sufficient.

The key requirement is **workflow reasoning**, not formatting.

---

## 5.3 User approval → execute the recommended Skill

This is required.

`ask-light` must not stop at:

```text
Recommended: $project-tickets
```

After the user accepts the recommendation with a normal reply such as:

```text
yes
可以
go ahead
do it
用这个
```

the current conversation should transition into the recommended Skill.

The user should **not** need to manually type the Skill invocation again.

Desired flow:

```text
$ask-light
→ inspect
→ recommend $project-tickets
→ user: 可以
→ begin project-tickets behavior
```

Do not auto-execute before user consent.

Preserve the recommendation across the next conversational turn.

---

## 5.4 Host execution compatibility

The primary acceptance target is Codex.

For Codex, prove with a real or repository-supported host test that:

```text
ask-light recommendation
→ user approval
→ target Skill begins
```

without requiring the user to repeat the target Skill command.

If a target Skill's invocation policy prevents direct model invocation, solve this using the host-supported composition/invocation mechanism rather than weakening the user experience silently.

Do not falsify compatibility.

For Claude Code or other supported hosts:

- preserve correct invocation rendering;
- implement the same approval-to-transition behavior where the host supports it;
- otherwise clearly document the host limitation.

Codex behavior is mandatory for this repair.

---


# 5.5 `ask-light`: Own Root Discovery

`ask-light` must not require the caller to already know and inject the Light Skill installation root as the only way to function.

The current host integration may still pass explicit roots when available, but `ask-light` must have a reliable discovery strategy for the supported environment.

The goal is:

```text
current host / current repo
→ locate installed Light Skill roots
→ identify Light-owned Skills
→ evaluate availability
→ route
```

Do not make `--roots-json` the conceptual source of truth.

If explicit roots are supplied, validate them rather than blindly trusting them.

For Codex, implement and test the normal installed-path discovery behavior used by this repository's supported setup.

For other hosts, use the best supported discovery mechanism and document real limitations.

Do not claim automatic discovery where only manual injection exists.

---

# 5.6 `ask-light`: Prove Light First-Party Identity

A Skill being found under a scanned directory does **not** prove it belongs to Light.

`ask-light` must distinguish:

```text
known Light Skill
```

from:

```text
third-party Skill installed in the same host/root
```

Use Light-owned repository knowledge as the source of identity.

This may be the Skill map / registry or another stable Light-owned manifest.

Availability scanning answers:

> Is this known Light Skill currently installed and usable?

It must not answer:

> Anything I found here is Light.

Add a functional test with a fake third-party Skill placed beside Light Skills and verify it is not presented as Light first-party.


# 6. `ask-light`: Keep the Skill Map, But Demote Matching to a Tool

The existing Light-owned Skill map remains useful.

Do not remove it merely because lexical routing was overused.

Its role should become:

```text
repository taxonomy + capability knowledge
```

not:

```text
the entire reasoning engine
```

The map may describe:

```text
skill name
family/category
role
entry condition
workflow position
important neighbors
invocation mode
```

Add explicit semantic families if useful, such as:

```text
project
clarification
research
implementation
review
learning
knowledge-work
specialized
utility
internal/reusable
```

Do not over-schema it.

The map should help `ask-light` reason and browse, while project evidence determines the actual next step.

---

# 7. `ask-light`: Support Collection Navigation

`ask-light` must also answer questions about the Skill collection itself.

Examples:

```text
What project Skills do I have?
Show me the review Skills.
Which Skills are for learning?
What's the difference between clarify and project-clarify?
What can I use for bugs?
```

The answer should:

- list the relevant Skills;
- explain their roles briefly;
- distinguish neighboring Skills where useful;
- optionally recommend one based on the user's context.

This is navigation, not execution.

Do not return `NEED-INPUT` merely because the user asked to browse a category.

---

# 8. `ask-light`: Preserve Standalone Intent Routing

Not every request is a project-stage question.

Standalone inputs must still route correctly, including cases equivalent to:

```text
Explain this like I'm five.
Practice Japanese conversation.
Give me a one-line recap.
Investigate this bug.
Set up a manuscript workflow.
Teach me this concept.
```

Use the Skill map and current context.

Do not require project inspection when the request is clearly standalone.

---

# 9. `ask-light`: Ambiguity

When two Skills are genuinely plausible, do not choose arbitrarily.

Prefer:

```text
I see two plausible routes:

A. `clarify` — if this is a bounded idea we can resolve in conversation.
B. `decision-map` — if this will span sessions or depends on research/prototypes.

Given the current repo, I'd choose B because ...
```

If one route is clearly preferable, recommend it.

If the choice depends on a real user decision, ask that decision.

Do not use ambiguity as an excuse to avoid reasoning.

---


# 9.5 `project-init`: Verify Declared Capability Availability

The previous functional-closure pass made `project-init` the Light project bootstrap.

Do not redesign that bootstrap here.

This SPEC only closes one remaining gap:

> `project-init` may declare `Relevant Skills`, but the bootstrap must not silently assume those capabilities are actually available.

When writing or validating the project configuration:

1. inspect the declared relevant Light capabilities;
2. determine whether each is discoverable in the current host/environment;
3. distinguish at least:

```text
available
unavailable
unknown
```

4. do not silently promote `unknown` to `available`;
5. keep the project configuration usable even when an optional capability is unavailable.

The exact persistence format should stay minimal.

Do not turn `docs/agents/light-project.md` into a host inventory dump.

If availability is host-dependent, record only what downstream behavior genuinely needs and report the rest during setup.

Add tests using a temporary project and a controlled Skill installation set.


# 10. Socratic Family: Restore Frontier Rounds

Remove the one-question-at-a-time design as the default.

Any contract equivalent to:

```text
frontierDecisionLimit = 1
```

must be removed or redesigned.

The Socratic engine should identify the **current actionable frontier**:

> all meaningful user decisions whose prerequisites are already settled.

Ask that frontier as a round.

---

# 11. Frontier Round Presentation

Each round should normally contain multiple independent questions when multiple frontier decisions exist.

Use numbered questions:

```text
Q1
Q2
Q3
...
```

Each question should provide concrete choices when the decision can reasonably be discretized:

```text
A. ...
B. ...
C. ...
```

Add more or fewer options when the decision demands it.

Do not invent meaningless options just to satisfy A/B/C formatting.

Always allow the user to answer outside the listed choices.

---

# 12. Recommended Answer Per Question

For each meaningful question, provide the agent's recommended answer when enough context exists.

Example:

```text
Q2 — Storage for v1

A. JSON files
B. SQLite
C. PostgreSQL

Recommended: B. SQLite keeps deployment simple while avoiding the concurrency and migration problems of flat files.
```

The recommendation is advisory.

The user owns the decision.

Do not hide behind neutrality when the available evidence supports a recommendation.

---

# 13. Efficient Batch Replies

The user must be able to answer a round compactly:

```text
1B, 2A, 3C
```

or:

```text
1B
2B, but only locally
3A
```

or in normal prose.

The engine should:

1. map answers to the correct questions;
2. preserve nuance/qualifiers;
3. mark resolved decisions;
4. leave unanswered questions open;
5. recompute dependencies;
6. produce the next frontier round.

Do not require one reply per question.

---

# 14. Dependencies Still Matter

Do not ask questions whose answers depend on unresolved decisions from the same round.

If:

```text
Q4 depends on Q2
```

then Q4 belongs to a later frontier.

The efficiency gain comes from asking **independent currently-unblocked decisions together**, not from dumping the whole decision tree at once.

---

# 15. Facts Are Still the Agent's Job

Preserve the existing distinction:

```text
user-owned decision → ask the user
environment/project fact → inspect/research it
runnable uncertainty → prototype where appropriate
external person's knowledge → questionnaire where appropriate
```

Do not ask the user questions the agent can answer by inspecting the repository or tools.

Fact-finding may temporarily block only the dependent branches.

Other frontier decisions should continue.

---

# 16. Round Size

Default to the complete actionable frontier.

Do not artificially force one question per round.

If the frontier becomes genuinely too large to present usefully, split it into coherent batches.

This is an exception for usability, not a new hard small-number limit.

Do not introduce a fixed global maximum such as `3 questions` unless there is a demonstrated reason.

---

# 17. `clarify`: Lightweight Entry to the Socratic Engine

`clarify` remains the normal lightweight user entry.

Desired flow:

```text
$clarify <idea>
→ first frontier round
→ user answers several questions
→ next frontier round
→ ...
→ shared understanding
```

One explicit invocation starts the session.

Normal user replies continue it.

Do not require `$clarify` again after each round.

---

# 18. `project-clarify`: Same Interaction, Project-Aware Evidence

`project-clarify` should use the same frontier-round interaction, but seed and update the decision tree using project evidence.

It should inspect the project's Light configuration and relevant local artifacts before asking.

The user-facing interaction should feel like `clarify`, not like a separate questionnaire product.

One explicit invocation starts the stage; normal replies continue it.

---

# 19. `socratic`: Reusable Engine, Not a Debug UI

`socratic` owns the reusable decision-resolution behavior.

Internal state may include:

```text
current understanding
resolved decisions
open decisions
dependencies
fact gaps
frontier
```

Do not dump this internal state by default.

The user-facing view should focus on:

- the current round of decisions;
- the choices;
- recommendations;
- short context necessary to answer well.

Detailed state is shown only when useful or requested.

---

# 20. Shared-Understanding Completion

When no meaningful frontier remains, synthesize the result.

Do not immediately act on the decisions.

Present a concise shared-understanding summary and ask for confirmation when appropriate.

After confirmation:

- `clarify` stops or recommends the next appropriate Skill;
- `project-clarify` stops or hands back into the project workflow;
- it does not auto-chain into unrelated work unless the user explicitly agrees.

---

# 21. Do Not Turn Socratic Into a Fixed Questionnaire

The round format is dynamic.

Questions must arise from:

```text
current goal
+ existing decisions
+ dependencies
+ project evidence
+ user's previous answers
```

Do not pre-generate a static questionnaire and merely walk through it.

Every round must be allowed to reshape the remaining decision tree.

---

# 22. References and Supporting Files

Do not create a generic template set for these Skills.

Supporting files should exist only where the repaired behavior benefits from them.

For example:

- `ask-light` may own a Skill/workflow map;
- `socratic` may own a small machine-readable conversation contract if it adds real testability;
- examples may exist if they materially improve behavior.

Do not add `WORKFLOW.md`, `EXAMPLES.md`, or contracts merely for symmetry.

Remove or update supporting material that contradicts the new behavior.

---


# 22.1 Reviewer Contract Ownership

The repository currently has the risk of maintaining the same reviewer concept in multiple locations, especially around:

```text
docs/REVIEWER_CONTRACT.md
skills/review-loop/references/reviewer-contract.md
```

Resolve this ownership explicitly.

Preferred direction:

```text
skills/review-loop/references/reviewer-contract.md
= canonical runtime contract owned by review-loop

docs/REVIEWER_CONTRACT.md
= human-facing explanation, summary, or pointer
```

Equivalent ownership is acceptable if there is a better repository-specific reason, but there must be one canonical runtime source.

Do not keep two independently maintained full runtime contracts for the same concept.

Do not rewrite `review-loop` behavior unless required to establish ownership.

Add a regression test or structural validation that makes accidental duplicate runtime ownership difficult to reintroduce.

---

# 22.2 Separate Migration History From Runtime Knowledge

Inspect touched Skills and their references for material that exists to explain:

```text
old Skill names
previous architectures
migration paths
superseded composition
historical compatibility
```

Historical material may remain useful.

It must not look like current runtime instructions.

For any such file, choose one:

```text
clearly mark as historical/migration documentation
move it to an explicitly historical location
replace it with a concise pointer
remove it if it no longer has value
```

Do not delete history merely to reduce file count.

Do not leave stale migration prose in the normal runtime disclosure path.

This check applies only to areas touched or directly depended on by this SPEC.


# 23. Tests: Functional, Not Prose-Locked

Add or update tests to protect the repaired behavior.

Do not test exact explanatory sentences unless they are a real public or machine-readable contract.

In all files touched by this SPEC, audit existing tests for prose coupling. If a test still requires a particular English sentence in `SKILL.md` or a reference file, determine whether the literal text is actually the contract.

Prefer testing:

```text
routing result
workflow state
composition edge
machine-readable contract
file ownership
availability state
host behavior
output shape
completion behavior
```

Do not preserve defensive prose solely because a test looks for it.

---

## 23.1 Required `ask-light` functional tests

Cover at least:

### Project-state recommendation

Create realistic temporary project states and verify cases equivalent to:

```text
project initialized, no SPEC
→ recommend project-clarify or project-spec according to evidence

stable SPEC, no tickets
→ recommend project-tickets

tickets exist, work pending
→ recommend implement

implementation complete, acceptance not run
→ recommend project-review
```

Do not reduce these tests to keyword matching.

### Recommendation reasoning

Verify that the result contains a usable reason tied to project state.

Do not test a fixed English sentence.

### Approval-to-execution

Test:

```text
ask-light
→ recommendation
→ user accepts
→ recommended Skill begins
```

For Codex, include a real or project-supported host-level smoke test.

### Collection navigation

Test category/browse requests such as:

```text
show project Skills
show review Skills
```

### Standalone routing

Keep representative tests for standalone Skills.

### Provenance / availability

Preserve first-party and availability behavior.

---

## 23.2 Required Socratic functional tests

Cover at least:

### Multiple-question frontier

Given three independent decisions:

```text
→ first round contains all three
```

not one.

### Dependency gating

Given:

```text
Q3 depends on Q1
```

the first round must not ask Q3.

After Q1 is resolved, Q3 may enter the frontier.

### Choices + recommendations

When reasonable options exist:

```text
question
→ multiple options
→ recommended answer
```

Do not assert exact prose.

### Batch response parsing

Test:

```text
1B, 2A, 3C
```

and a mixed free-text response.

### Partial response

If the user answers only part of the frontier, preserve unresolved decisions correctly.

### Continuous session

One Skill invocation followed by ordinary replies must continue the same clarification session.

### Final confirmation

When the frontier is empty, return a shared-understanding synthesis before completion.

---

# 24. Real Interaction Smoke Tests

Unit tests alone are insufficient for these two Skills because the primary failure was interaction design.

Before completion, run at least:

## `ask-light`

A real Codex interaction equivalent to:

```text
$ask-light
```

inside a prepared project state.

Verify that it:

1. inspects the project;
2. explains the current stage;
3. recommends the correct Skill and why;
4. asks for/accepts approval;
5. begins the recommended Skill after a normal "yes/可以".

Capture a concise transcript or evidence in the work records.

## `clarify` / Socratic

Run a real multi-round interaction with at least three independent first-frontier decisions.

Verify that the first round visibly contains multiple questions with options and recommendations.

Then answer them in one batch and verify that the next round is recomputed correctly.

---


# 24.1 Host Compatibility Claims Must Be Evidence-Based

This repository currently renders or discusses multiple host invocation styles.

Before completion:

- identify which hosts this repaired behavior is actually tested on;
- distinguish tested support from best-effort rendering;
- do not describe untested behavior as verified compatibility.

Codex is mandatory and must receive real interaction smoke coverage for:

```text
ask-light inspection
recommendation
user approval
transition into target Skill
```

For Claude Code or other hosts:

- preserve compatible invocation output;
- run a real smoke test if the repository environment supports it;
- otherwise document the limitation precisely.

A host limitation is acceptable.

A false compatibility claim is not.


# 25. Preserve Lean Architecture

This repair must not regress the previous architecture.

After implementation:

```text
SKILL.md
```

must still be the minimal executable interface.

Do not solve missing functionality by putting hundreds of lines back into `SKILL.md`.

Put conditional workflow detail in Skill-owned supporting material where appropriate.

Functionality and progressive disclosure must coexist.

---

# 26. Work Records

Create focused tickets under:

```text
.scratch/light-skills-core-flow-repair/issues/
```

Keep the ticket set small and aligned to the actual work.

A reasonable breakdown is:

```text
01-ask-light-workflow-advisor
02-ask-light-execution-and-navigation
03-socratic-frontier-rounds
04-clarify-project-clarify-integration
05-functional-tests-and-host-smoke
06-final-validation
```

This is an example, not a mandatory ticket template.

Do not create dozens of tiny tickets.

Update:

```text
.scratch/light-skills-core-flow-repair/results.md
```

with verified implementation results.

---

# 27. Validation

Run all existing canonical validation plus new functional tests.

At minimum:

```bash
python3 -m pytest -q
python3 -m unittest discover -s tests
python3 -m compileall -q skills tests
```

Run all Skill-local unittest suites used by the repository.

Verify:

- no unexpected unrelated tracked diffs;
- local references resolve;
- no new invalid cross-Skill deep links;
- ask-light root discovery works in the supported Codex setup;
- Light first-party provenance excludes colocated third-party Skills;
- ask-light routing and execution tests pass;
- project-init capability availability behavior is tested;
- reviewer runtime contract has one canonical owner;
- migration/history material is not accidentally in the active runtime path;
- Socratic frontier-round tests pass;
- touched-area tests are not unnecessarily prose-locked;
- real interaction smoke tests pass or any genuine host limitation is explicitly reported.

Do not claim a command passed unless it was actually run.

---

# 28. Local Commit Is Required

After implementation and validation:

1. review the complete diff;
2. ensure only this SPEC's intended changes are present;
3. update `results.md`;
4. create a **local Git commit** containing the completed repair.

Use a clear commit message such as:

```text
fix: close ask-light and socratic workflow gaps
```

Equivalent wording is acceptable.

Do not push the commit.

Do not publish a release.

Do not create or merge a PR unless the user explicitly asks.

---

# 29. Stop After the Local Commit

This is a hard workflow boundary.

After the local commit is created:

```text
STOP
```

Report to the user:

- local commit SHA;
- concise change summary;
- exact validation results;
- any known remaining limitations;
- that the repository is ready for **human review**.

Do not:

- perform another autonomous repair pass;
- invoke a release workflow;
- push;
- tag;
- bump a version;
- declare the repository finally accepted;
- continue modifying files after the commit.

The next authority is the user's manual review.

---

# Definition of Done

This SPEC is complete only when all of the following are true.

## `ask-light`

- understands current project/workflow state rather than relying primarily on lexical matching;
- explains what stage the work is in;
- recommends the correct next Skill with a reason;
- distinguishes meaningful neighboring alternatives;
- supports browsing Skill families/categories;
- preserves standalone routing;
- reliably discovers the Light installation/root in the supported Codex environment;
- uses Light-owned provenance instead of treating all colocated Skills as first-party;
- waits for user consent before execution;
- after consent, transitions into the recommended Skill without requiring the user to type the Skill command again in Codex;
- has verified host behavior, not only theoretical invocation rendering.

## Socratic family

- the one-question default is removed;
- each round asks the current independent frontier;
- questions provide useful multiple choices when appropriate;
- each question provides a recommendation when context supports one;
- users can answer several questions in one reply;
- dependencies prevent premature questions;
- answers reshape later rounds;
- `clarify` and `project-clarify` continue naturally after one initial invocation;
- internal state is not dumped as default UI;
- completion includes shared-understanding confirmation.


## Known closure gaps

- `project-init` verifies the availability state of declared relevant Light capabilities without redesigning the bootstrap;
- reviewer-contract runtime ownership is singular and explicit;
- historical/migration material in touched areas is clearly separated from current runtime instructions;
- remaining touched-area tests do not unnecessarily lock explanatory prose;
- host compatibility claims match actual evidence.


## Architecture

- Lean `SKILL.md` entrypoint design is preserved;
- supporting files remain need-driven;
- no unrelated repository-wide refactor occurs.

## Quality

- functional tests cover project-state routing, approval-to-execution, frontier rounds, dependency gating, batch replies, and completion;
- real interaction smoke tests are performed;
- all canonical tests pass.

## Delivery

- work records are updated;
- the completed repair is committed locally;
- nothing is pushed or released;
- implementation stops after the local commit;
- final status is **AWAITING HUMAN REVIEW**.
