# Code Review — logic reconstruction

**Real job:** Read-only specialist reviewer of a bounded git diff along Standards and Spec axes, returning findings without deciding final acceptance.

**Entry:** User invokes `$code-review`, or `review-loop`/`project-review` routes a software diff to it.

**Core loop:** Pin fixed point → locate originating Spec/standards → run Standards and Spec sub-agents in parallel → aggregate separately → return findings with citations.

**Produces:** Two-axis findings report.

**Completion/stop:** After the report is returned; no edits, no repair loop, no final verdict.

**Every-invocation knowledge:** Two-axis method, read-only boundary, citation requirement, reference pointers.

**Conditional knowledge:** Prompt briefs, finding shapes, smell baseline, examples live in `references/WORKFLOW.md`, `SMELL-BASELINE.md`, `EXAMPLES.md`.

**Duplicates:** Does not re-document `review-loop` or `project-review`; it supplies specialist evidence only.

**Negative constraints:** Read-only/no-verdict is a real contract and stays; tooling/style-smell nuances are delegated to references.
