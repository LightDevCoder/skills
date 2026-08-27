---
name: review-loop
description: Run a lightweight review→findings→repair→re-review loop by resolving a reviewer, collecting normalized findings, and re-running until clean or bounded limit. Use for bounded review convergence; use project-review for final acceptance.
---

# Review Loop

`review-loop` is a model-invoked **Review Engine** (may also be manually
invoked). It drives exactly one loop — `review → findings → repair →
re-review` — and owns no project final acceptance.

## When to use

- A bounded review needs repair convergence (implementation handoff, package
  admission, routine review).
- The caller has a bounded packet and a concrete repair path.
- Do **not** use it to freeze an acceptance baseline or issue
  `PASS`/`FAIL`/`BLOCKED`; that is `project-review`'s job.

## Core behavior

1. **Resolve reviewer** — `generic-review` by default; `code-review` for a
   bounded software diff; an accepted domain reviewer when one exists. Never
   invent a specialist.
2. **Invoke reviewer** — send the four-field packet in
   [reviewer-contract.md](references/reviewer-contract.md).
3. **Receive findings** — collect the normalized report per
   [finding-schema.md](references/finding-schema.md). A missing or unreadable
   required input returns `REVIEW-ERROR` and stops.
4. **Return repair** — hand confirmed, in-scope findings to the Producer.
5. **Re-run reviewer** — recheck with the same reviewer until `Findings: []`
   or the configured limit (default **3 rounds**).

At the limit, hand the outstanding findings to the caller. Do not run another
round to obtain a favorable result. `review-loop` never writes `PASS`, `FAIL`,
or `BLOCKED`; those verdicts belong to `project-review`.

## Handoff and stop

- Clean: hand off `Findings: []`.
- Limited or blocked: hand off outstanding findings and the next smallest
  action.
- Caller needing final acceptance: recommend `project-review`, which composes
  reviewers through this engine.

## References

- [reviewer-contract.md](references/reviewer-contract.md) — reviewer input
  packet and read-only boundary.
- [finding-schema.md](references/finding-schema.md) — normalized finding shape
  and `REVIEW-ERROR` handling.
- [migration.md](references/migration.md) — historical provenance only; never
  required for current runtime execution.
- Composition targets (invoke by name, do not copy): `generic-review`,
  `code-review`, `project-review`.
