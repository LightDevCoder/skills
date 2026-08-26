# Generic Review — logic reconstruction

**Real job:** Read-only reviewer for non-specialist artifacts against supplied requirements; return normalized findings.

**Entry:** Model-invoked by `review-loop`/`project-review` or another caller when no specialist reviewer is more appropriate.

**Core loop:** Read bounded packet (Target, Requirements, Context, Previous findings) → compare target to requirements → check only the five allowed finding classes → recheck previous findings → return normalized report.

**Produces:** `Findings: []`, a report of `F-###` findings, or `REVIEW-ERROR`.

**Completion/stop:** After returning the report; no edits, repairs, or verdicts.

**Every-invocation knowledge:** Four-field input packet, allowed finding classes, ID preservation, read-only boundary, output-schema pointer.

**Conditional knowledge:** Exact report schema in `references/output-schema.md`.

**Duplicates:** None; it is intentionally the generic fallback under `review-loop`/`project-review`.

**Negative constraints:** Read-only and no-invention are real contract; keep minimal explicit guardrails.
