# Neighboring Skill Group Review

Reviewed the four mandated groups together; no forced shared architecture.

## Clarification family: `socratic`, `clarify`, `project-clarify`, `project-init`

- `socratic` is the reusable decision-state engine; it owns the conversational loop and fact-vs-decision rule.
- `clarify` is the standalone lightweight user entry: compose `socratic`, return state summary, stop.
- `project-clarify` is the project-scoped user entry: inspect project facts first, use `socratic` for decisions, produce a handoff for `project-spec`.
- `project-init` initializes structure; it does not clarify requirements. Boundary is explicit in both SKILL.md files.

## Planning/execution family: `project-spec`, `project-tickets`, `implement`, `code-review`

- `project-spec` consumes clarified material and publishes a SPEC.
- `project-tickets` slices the SPEC into vertical tickets.
- `implement` executes one ready ticket and hands to review.
- `code-review` is a specialist reviewer; it never owns the verdict. The chain is `project-spec → project-tickets → implement → review-loop → project-review`.

## Review family: `generic-review`, `review-loop`, `project-review`

- `generic-review` returns normalized findings for non-specialist artifacts.
- `review-loop` drives the convergence loop and owns no final verdict.
- `project-review` owns the final `PASS`/`FAIL`/`BLOCKED` and uses `review-loop` plus reviewers.
- The old monolithic review-loop references/profiles were moved/owned by `project-review`; `review-loop` is now the lightweight engine.

## Router: `ask-light` + final repository routing model

- `ask-light` is a read-only router over the final first-party map.
- It only names Skills/recipes; it does not reimplement the routed Skills or auto-invoke them.
- Repository-level workflow docs (not individual SKILL.md files) carry the routing/categorization detail.
