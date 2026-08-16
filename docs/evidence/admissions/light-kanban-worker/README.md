# `light-kanban-worker` admission evidence

[中文记录](README.zh-CN.md)

## Scope and status

- Package: `skills/light-kanban-worker/`
- Invocation type: model-invoked, with a supported manual entry point
- Profile: `review-loop` `agent-skill`
- Stable-release boundary: v0.1.3 contains seven packages and does not contain `light-kanban-worker`
- Admission status: `IN PROGRESS` — full admission path; the prompt-only fast track does not apply because the Skill accesses the network, reads workspace files, and mutates Light-Kanban task state

## Evidence plan (full path)

| Area | Required demonstration |
| --- | --- |
| Structure | Package tree, `SKILL.md` metadata, internal links and resources validate with the package contract and behavior suites. |
| Installation and discovery | A fresh environment installs the package form, then discovers the installed Skill without relying on the source checkout. |
| Behavioral | Scenarios A–F against a real Light-Kanban server: fresh task, Request Changes rework, two-worker atomic claim, workspace missing → block, empty queue → no mutation, offline → no mutation with clear failure. |
| Invocation | A scheduled-style prompt and a one-shot manual prompt both resolve to the worker; model-invoked metadata agrees with `SKILL.md`. |
| Review | `review-loop` with the `agent-skill` Profile evaluates the candidate using Producer evidence and a fresh Evaluator. |
| Attribution | Owner-authored first-party; no third-party content, so no `ATTRIBUTION.md` is required. |

## Results

The rows above are filled in with exact commands, environment facts, inputs,
outputs, and limitations as each gate completes. The final verdict is owned
by `review-loop agent-skill`; only a `PASS` admits the package into the
first-party collection.

- Contract and behavior suites:
  `skills/light-kanban-worker/tests/` (positive and negative fixtures,
  non-zero assertions).
- Behavioral evidence against a real Light-Kanban server: recorded in
  [behavioral-evidence.md](behavioral-evidence.md).
- Final acceptance: recorded under [review-loop/](review-loop/) once the
  `review-loop agent-skill` run completes.
