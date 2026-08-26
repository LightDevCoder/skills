# Agent Config — logic reconstruction

**Real job:** Turn current, inspectable Agent Host evidence into one safe execution plan for multi-role work.

**Entry:** A task needs several roles, independent review, parallelism, isolation, or host limits that affect safe execution structure.

**Core decision path:** Read host evidence → classify each model/capability as available/unknown/unavailable → select the most capable route that the evidence actually supports (multi-model/multi-agent, single-model/multi-agent, or single-model/single-agent) → assign roles → build ownership matrix/waves and review gate → return the bounded plan schema.

**Produces:** A plan object containing evidence ledger, role assignment, ownership matrix, review gate, merge rule; or `NEED-INPUT` / `BOUNDARY`.

**Completion/stop:** Stop after returning the plan to the Controller. No execution, installation, or merge happens in this Skill.

**Every-invocation knowledge:** Evidence boundary, route selection, role ownership rules, review-gate invariant, plan schema location.

**Conditional knowledge:** Detailed plan-schema and host-evidence-schema field shapes live in references; only loaded when building/validating a plan.

**Duplicates:** None materially; it intentionally does not re-document `review-loop`/`project-review` or subagent mechanics.

**Negative constraints:** The important ones (`do not promote unknown`, `do not invent concurrency caps`, `do not rename self-check as reviewer`) are high-risk host-evidence failure modes, so they remain as explicit guardrails after the positive route-selection behavior is stated.
