# Reviewer Contract — Human-Facing Summary

The runtime reviewer contract is owned by `review-loop` and lives at
[skills/review-loop/references/reviewer-contract.md](../skills/review-loop/references/reviewer-contract.md).

This page is a human-facing explanation and pointer only. It is **not** a
second independently maintained runtime contract.

## What the contract covers

A reviewer is a read-only capability that receives a bounded input packet and
returns a normalized finding report:

- **Input packet:** Target, Requirements, Relevant context, Previous findings.
- **Normalized result:** findings with `id`, `state`, `severity`, `location`,
  `problem`, `reason`, and optional `suggestion`; a clean report is
  `Findings: []`.
- **Boundary:** reviewers inspect but never write the target, evidence, or
  review state; they never issue a final `PASS`, `FAIL`, or `BLOCKED` verdict.

The canonical runtime details, including identity/cross-round state and the
severity guide, are maintained in the `review-loop` package reference linked
above. Any change to reviewer behavior belongs there, not in this summary.