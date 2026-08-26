---
name: project-review
description: Determine whether a completed project satisfies its approved target by freezing an acceptance baseline, composing reviewers, and issuing a final PASS/FAIL/BLOCKED. Use when project delivery needs final acceptance.
---

# Project Review

`project-review` is the **project-level final acceptance** capability. It is
model-invoked and may also be manually invoked. It answers whether the
completed project actually satisfies the approved project target. It owns the
frozen acceptance baseline and issues the final `PASS`, `FAIL`, or `BLOCKED`.

## When to use

- The project has an approved target/SPEC/brief/ticket graph and a bounded
  implementation to check.
- Use it as the final gate after `implement` or after a batch of tickets,
  before `release-workflow`.
- Use it for Skill admission when the acceptance source is a package's
  `SKILL.md` and its supporting evidence.

## Core behavior

`project-review` composes read-only reviewers and drives them through
`review-loop` (resolve → invoke → receive → return repair → re-run). It does
not repair artifacts itself; the Producer performs authorized repairs.

- Freeze the acceptance baseline/Charter before reviewing.
- Select a Profile (`generic`, `software`, `manuscript`, `agent-skill`,
  `specification`).
- Invoke reviewers through `review-loop`: `generic-review` for ordinary
  artifacts, `code-review` for software diffs, domain reviewers when an
  accepted specialist exists.
- Validate candidate findings, direct only bounded in-scope repairs, and
  request a fresh, independent Evaluator.
- Issue `PASS`, `FAIL`, or `BLOCKED` when the stopping rules are met.

`review-loop` is only the convergence engine. `generic-review` and `code-review`
are read-only reviewers: they never self-repair, never run the loop, and never
issue the project verdict.

## Entry modes

Use one of three modes; details are in
[WORKFLOW.md](references/WORKFLOW.md):

- `init`: freeze the acceptance baseline and Profile before review.
- `review`: run one bounded evidence, critique, validation, repair, and
  evaluation round.
- `resume`: continue the next unfinished recorded action without rewriting
  prior evidence.

## Handoff and stop

- `PASS`: every frozen criterion has correctly labeled evidence and the fresh
  Evaluator accepts the baseline.
- `FAIL`: a frozen condition is unmet and cannot be resolved through a
  confirmed, in-scope, bounded repair.
- `BLOCKED`: required baseline, authority, environment, evidence, access, or
  independent context is unavailable; records conflict; or the repair limit
  stops safe convergence.

Default maximum is three rounds. Record durable state under
`.project-review/`; see [WORKFLOW.md](references/WORKFLOW.md) for the exact
state tree and resume rules.

## References

- [WORKFLOW.md](references/WORKFLOW.md) — full init/review/resume workflows,
  role packets, and durable state tree.
- [acceptance-charter.md](references/acceptance-charter.md) — frozen baseline
  and Profile fields.
- [evidence-protocol.md](references/evidence-protocol.md) — evidence labels
  and records.
- [finding-schema.md](references/finding-schema.md) — stable identities,
  dispositions, registry format.
- [reviewer-contract.md](references/reviewer-contract.md) — local read-only
  reviewer packet.
- [review-rubric.md](references/review-rubric.md) — generic Core checks and
  Profile-supplied dimensions.
- [subagent-protocol.md](references/subagent-protocol.md) — read-only
  Critic/Evaluator packets and independence declaration.
- [stopping-rules.md](references/stopping-rules.md) — verdict transitions,
  repair limit, scope-expansion stop.
- Profiles: [generic.md](references/profiles/generic.md),
  [software.md](references/profiles/software.md),
  [manuscript.md](references/profiles/manuscript.md),
  [agent-skill.md](references/profiles/agent-skill.md),
  [specification.md](references/profiles/specification.md).
- [migration.md](references/migration.md) — provenance of the migrated
  final-acceptance logic.
- Composition targets (invoke by name, do not copy): `review-loop`,
  `generic-review`, `code-review`.