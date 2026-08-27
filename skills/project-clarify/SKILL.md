---
name: project-clarify
description: Clarify a real project's unresolved decisions from inspected project facts and return a bounded handoff artifact. Use only when the user explicitly invokes $project-clarify after readiness or when a project needs formal clarification; it does not create a SPEC, tickets, or automatically start another user-invoked stage.
disable-model-invocation: true
---

# Project Clarify

`project-clarify` is an explicit, user-invoked project stage. Run it only
after an explicit `$project-clarify` request. It turns real project evidence
and user-owned decisions into a bounded handoff for `project-spec`.

## Required order

1. **Inspect project facts before asking.** If
   `docs/agents/light-project.md` exists, read its goal, outputs, domain-context
   locators, and tracker locator first. Then inspect the named material plus
   relevant `README`, instructions, source/tests/specs, and tracker state.
   Record each usable fact with a stable locator; mark missing or unreadable
   material as an evidence gap. Facts that inspection can settle are not user
   questions.
2. **Maintain user decisions with `socratic`.** Pass inspected facts, unknowns,
   existing decisions, and the goal to the `socratic` engine. Ask only the
   unblocked, user-owned frontier — one meaningful question at a time.
3. **Resolve fact and experiment gaps deliberately.** For a fact gap, state
   which decision it blocks and record the authorized capability call
   (`research`, `prototype`, `to-questionnaire`) in the ledger. Never mark a
   result as read without a result path actually read; leave unavailable or
   not-authorized gaps unresolved and keep their downstream decisions out of
   the frontier.
4. **Return the handoff and stop.**

## Handoff shape

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

Return the handoff in memory by default. Write it to a file only when the user
separately names a writable destination and confirms the write. Then stop; the
user chooses the next invocation.

## Composition and upgrade

```text
project-clarify → socratic
```

If the effort is large, multi-session, or has many dependent decisions,
recommend `$decision-map` and stop. The full contract is in
[project-clarification-contract.md](references/project-clarification-contract.md);
workflow and examples are in [WORKFLOW.md](references/WORKFLOW.md) and
[EXAMPLES.md](references/EXAMPLES.md).
