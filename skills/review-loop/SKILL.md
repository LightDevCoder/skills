---
name: review-loop
description: Run a lightweight review→findings→repair→re-review loop by resolving a reviewer, collecting normalized findings, and re-running until clean or bounded limit. Use for any bounded review convergence; for project final acceptance use project-review.
---

# Review Loop

## Purpose and boundary

`review-loop` is a lightweight **Review Engine**. It drives only the
`review → findings → repair → re-review` convergence loop and owns no project
final-acceptance verdict.

It is model-invoked and may also be manually invoked.

Use it when a bounded review with repair convergence is needed. Do not use it
to invent requirements, settle unresolved product decisions, weaken an
acceptance source, or make a reviewer repair the target.

Project-level final acceptance (frozen baseline, `PASS`/`FAIL`/`BLOCKED`,
scope-change gate) belongs to `project-review`, not this engine.

## Responsibilities

The engine does exactly five things, then stops:

1. **resolve reviewer** — pick the reviewer for this packet;
2. **invoke reviewer** — call it with the bounded packet;
3. **receive findings** — collect the normalized report;
4. **return repair** — hand confirmed, in-scope findings to the Producer;
5. **re-run reviewer** — recheck with the same reviewer until clean or limit.

At the bounded limit it stops and hands the outstanding findings to the caller.
It does not decide project `PASS`/`FAIL`/`BLOCKED`, freeze an acceptance
Charter, or own the final evidence — `project-review` does.

## Input packet

Every invocation uses the lightweight reviewer packet defined in
[REVIEWER_CONTRACT.md](../../docs/REVIEWER_CONTRACT.md):

1. **Target:** immutable identity + readable view of artifact or diff.
2. **Requirements:** approved criteria, request, and explicit exclusions.
3. **Relevant context:** constraints, evidence, assumptions, limitations.
4. **Previous findings:** canonical prior records and IDs; `none` on first review.

If a required input is absent or unreadable the reviewer returns
`REVIEW-ERROR` with the missing field and the engine stops without a repair.
Do not infer requirements from a Producer conclusion.

## Reviewer resolution

Resolve one reviewer per packet and only that reviewer:

- **default:** `generic-review` for ordinary artifacts (missing
  requirements, incorrect result, contradictions, usability, scope expansion
  — no large rule library).
- **software diff:** `code-review` when the target is a bounded `git diff`
  since a fixed point; it returns separate Standards/Spec candidate findings.
- **domain:** a domain reviewer when the task has an accepted specialist
  (e.g. manuscript). Never invent a specialist; use `generic-review` when
  none is more appropriate.

Record the resolved reviewer. A reviewer is always read-only — see
[REVIEWER_CONTRACT.md](../../docs/REVIEWER_CONTRACT.md).

## Normalized findings

The reviewer returns one normalized report. Each finding uses:

```yaml
id: F-001
severity: critical | high | medium | low
location: path, section, stable anchor, or "whole target"
problem: concise observable gap
reason: requirement or evidence that makes it a gap
suggestion: optional minimal direction; never an implementation order
state: new | persists | fixed | duplicate
```

`id`, `severity`, `location`, `problem`, `reason` are required; `suggestion`
is optional. Allocate the next unused `F-###` after the IDs in `Previous
findings`; never recycle an ID. Reuse the same ID when the same gap
`persists`; mark `fixed` only when the original gap is absent; mark
`duplicate` and link `duplicate_of: F-###` when it repeats another canonical
concern.

For a complete clean review with no candidates and no rechecks, the report
writes `Findings: []`. It never writes `PASS`, `FAIL`, or `BLOCKED` — those
are final-acceptance verdicts owned by `project-review`. A malformed or
mutating report is rejected as `REVIEW-ERROR`. See
[output-schema.md](../generic-review/references/output-schema.md) for the
concrete `generic-review` report shape; other reviewers follow the same
contract in [REVIEWER_CONTRACT.md](../../docs/REVIEWER_CONTRACT.md).

## Bounded convergence and handoff

Run the loop:

```text
resolve reviewer → invoke → receive findings → (if Findings: [] → hand off clean)
→ return confirmed in-scope findings to Producer → re-run same reviewer
→ stop when clean or at limit
```

Default maximum is **3 rounds**. Configure the maximum before the first
invoke. A new round starts only with a concrete, bounded, in-scope repair
path. At the limit or when no such repair remains, stop and hand the
outstanding normalized findings to the caller — do not run another round to
obtain a favorable result. Never overwrite prior findings or fabricate
reviewer output to make the state appear complete.

Durable state (`.review-loop/state.md`, `findings.md`, `rounds/`) is optional
for trivial loops and required only when the caller needs resumability. When
present, keep facts in their authoritative record and link rather than
duplicate them. Project-level durable state (Charter, `verdict.md`,
`PASS`/`FAIL`/`BLOCKED`) belongs to `project-review`.

## Composition

```text
implement → review-loop → generic-review / code-review / domain reviewer → findings → Producer repair → re-review
project-review → review-loop → relevant reviewers → convergence → project verdict
```

`code-review` is a specialist reviewer: read-only, never self-repairs, never
runs the loop, never decides the final project verdict. `review-loop` validates
its candidate findings through the same lifecycle and hands the bounded repair
to the Producer; `project-review` owns the final `PASS`/`FAIL`/`BLOCKED`.

## Legacy note

> **Deprecated final-acceptance behavior:** the former `review-loop` final-
> acceptance system (frozen acceptance baseline / Charter, evidence labels,
> finding registry with `confirmed`/`rejected`/`out-of-scope`/`resolved`,
> `PASS`/`FAIL`/`BLOCKED` final verdict, scope-change boundary, Profile
> selection, durable `.review-loop/charter.md|verdict.md|changes.md` lifecycle)
> has been **migrated to `project-review`** without rewrite. New project
> final-acceptance consumers must use `project-review`; this engine keeps
> only the convergence loop. See
> [migration.md](../project-review/references/migration.md) and
> `project-review/SKILL.md` for the mapping.

## References

- [REVIEWER_CONTRACT.md](../../docs/REVIEWER_CONTRACT.md): reviewer input packet and normalized result contract.
- [output-schema.md](../generic-review/references/output-schema.md): concrete `generic-review` report schema (all reviewers follow the same contract).
- [code-review](../code-review/SKILL.md): software specialist reviewer (read-only, no loop, no final verdict).
- [project-review](../project-review/SKILL.md): project final-acceptance owner (`PASS`/`FAIL`/`BLOCKED`, frozen baseline).

For contract validation, run:

```bash
python3 -m unittest discover -s skills/generic-review/tests -p 'test_*.py' -v
```
