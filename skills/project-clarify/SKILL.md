---
name: project-clarify
description: Clarify a real project's unresolved decisions from inspected project facts and return a bounded handoff artifact. Use only when the user explicitly invokes $project-clarify after readiness or when a project needs formal clarification; it does not create a SPEC, tickets, or automatically start another user-invoked stage.
disable-model-invocation: true
---

# Project Clarify

`project-clarify` is an **explicit, user-invoked project stage**. Run it only
after an explicit `$project-clarify` request. It turns real project evidence
and user-owned decisions into a bounded handoff for `project-spec`.

Read [the project-clarification contract](references/project-clarification-contract.md)
before starting a run. Examples are in
[EXAMPLES.md](references/EXAMPLES.md).

## Required order

### 1 — Inspect project facts before asking

Inspect the applicable target root for readable material that could answer
questions without asking the user:

- `README`, `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md` / `CONTEXT-MAP.md`
- `docs/adr/`, `docs/`, `source`, `tests`, `specs`, task/tracker state

Record each usable fact with its path and stable location (heading, symbol,
file). Mark absent or unreadable material as an evidence gap. Details in the
contract.

Do not ask the user to decide a fact this inspection can settle. Do not claim
inspection ran unless it actually ran.

### 2 — Maintain user decisions with `socratic`

Pass inspected facts, unknowns, existing decisions, and the declared project
goal to the model-invoked `socratic` engine. Use its `current understanding /
open decisions / dependencies / frontier` to ask only the unblocked,
user-owned decisions — one meaningful frontier question at a time.

```text
project-clarify → socratic
```

This is an internal engine call, not an automatic user-invoked workflow.
Do not auto-invoke `$clarify`, `$project-init`, `project-spec`,
`project-tickets`, `implement`, or `review-loop`.

### 3 — Resolve fact and experiment gaps deliberately

When `socratic` reports a fact gap, first state which decision it blocks and
whether local inspection was sufficient.

- Use `research` only for a bounded external fact and only when the user has
  authorized the fact work in the current request.
- Use `prototype` only for a bounded disposable experiment that distinguishes
  alternatives with a safe non-production boundary.
- Use `to-questionnaire` when the information needed to unblock a decision is
  held by another person. Because it is a user-invoked Skill, do not auto-run
  it; record it in the ledger and, when appropriate, recommend it in the
  handoff.

For each attempted or recommended call, append a ledger entry defined in the
contract (`Capability call: socratic | research | prototype | to-questionnaire`,
`Blocked decision`, `Call status`, `Result read`, etc.). Never mark
`result-read` without a result path actually read. If the capability is
`unavailable` or `not-authorized`, retain the gap and keep its downstream
decision out of the frontier.

### 4 — Return the handoff and stop

Return one bounded `Project clarification handoff`:

```text
Project clarification handoff
- Target and inspected project facts:
- Evidence not found or not inspected:
- Current goal and constraints:
- Resolved user decisions:
- Open decisions and dependencies:
- Capability call records and results read:
- Current frontier or explicit blocker:
- Recommended next explicit invocation: project-spec | decision-map | none
- Status: ready-for-next-stage | waiting-for-user | blocked
```

This artifact is a returned record by default, not an implicit file write.
Write it only if the user separately names a writable destination and confirms
the write. Then stop. The user decides whether to invoke the recommended next
stage; do not auto-chain.

## Upgrade and boundaries

- If the effort is large, multi-session, or has many dependent decisions,
  recommend `$decision-map` and stop.
- Do not create or revise a formal SPEC, tickets, implementation code, or a
  release. Do not perform broad research, build a production prototype, or
  mutate project files as a side effect of clarification.

Large-task upgrade and handoff verification are detailed in
[EXAMPLES.md](references/EXAMPLES.md).
