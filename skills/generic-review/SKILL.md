---
name: generic-review
description: Review a bounded non-specialist artifact against supplied requirements and return normalized, read-only findings. Use when no accepted specialist reviewer is more appropriate.
---

# Generic Review

`generic-review` is a model-invoked, read-only reviewer for ordinary artifacts
that do not need a specialist review method. It returns candidate findings;
it does not edit the target, plan a repair, coordinate other agents, or issue
a final acceptance verdict.

## Required input

Read a bounded packet containing all four fields:

1. **Target:** immutable identity plus the artifact, diff, or view to inspect.
2. **Requirements:** approved criteria, request, and explicit exclusions.
3. **Relevant context:** material constraints, evidence, assumptions, and
   known limitations.
4. **Previous findings:** canonical prior finding records and their IDs. On a
   first review, set Previous findings to `none`.

If a required input is absent or unreadable, return `REVIEW-ERROR` with the
missing field and stop.

## Review method

1. Compare the target with the requirements and context. Check only for:
   missing required output, output contradicting a requirement, internal
   contradiction, a directly observable usability obstacle, or scope added
   without a stated requirement.
2. Tie every candidate to a target location and concrete requirement or
   evidence. Do not add a domain rulebook, speculate about hidden intent, or
   turn a preference into a finding.
3. Recheck each relevant previous finding. Reuse its ID when the same gap
   persists; record `fixed` only when the original gap is absent; mark a
   repeat of another canonical concern `duplicate` and name that canonical ID.
4. Return the normalized report in
   [`references/output-schema.md`](references/output-schema.md), preserving
   IDs across rounds.

## Read-only output

Return observations, not commands. An optional suggestion is a narrow possible
direction, not a repair plan or instruction to the Producer. Do not modify the
target, requirements, evidence, finding registry, or review state.

## Stop

- Return `Findings: []` when no candidate finding remains and no prior finding
  requires a recheck.
- Return `REVIEW-ERROR` for missing input, unreadable target, malformed report
  field, or a read-only violation; name the problem and stop.
- Return only the report. Hand it to the caller; do not continue into repair
  or final acceptance.