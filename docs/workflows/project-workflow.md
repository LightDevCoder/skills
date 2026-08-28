# Project Workflow — Composition

[中文](../zh-CN/workflows/project-workflow.md)

This document explains how the **Project Workflow** Skills compose. It shows entry, handoff artifact, and stop — not the internal workflow of any single Skill. For behavior, read the Skill's `SKILL.md`.

## The recommended flow

```text
project-init
      ↓  (stable Light project + tracker contracts)
project-clarify
      ↓  (bounded clarification handoff: understanding / resolved / unresolved / gaps)
project-spec
      ↓  (frozen SPEC + acceptance source)
project-tickets
      ↓  (tracer-bullet ticket graph with dependencies)
implement
      ↓  (bounded diff + focused tests + verification)
project-review
      ↓  (final PASS / FAIL / BLOCKED)
release-workflow
```

This is a *recommended* flow, not a required pipeline. Enter mid-stream when the task is already at that stage. No Skill auto-invokes the next user-invoked Skill.

## Entry → Handoff → Stop

| Step | Entry condition | Skill & invocation | Output / Handoff | Stop |
| --- | --- | --- | --- | --- |
| 1 | New project needs a stable, confirmed starting point | [`project-init`](../../skills/project-init/SKILL.md) — user-invoked | `docs/agents/light-project.md` + tracker contract + instruction pointer | stop; user chooses next |
| 2 | Real project has unresolved decisions; repo facts should not be re-asked | [`project-clarify`](../../skills/project-clarify/SKILL.md) — user-invoked → `socratic` engine | bounded handoff artifact for `project-spec` | stop at clarification summary; do not create SPEC |
| 3 | Decisions are clarified and a formal SPEC is needed | [`project-spec`](../../skills/project-spec/SKILL.md) — user-invoked | frozen SPEC with acceptance source | stop for approval; if blocked, return to `project-clarify` |
| 4 | SPEC is approved | [`project-tickets`](../../skills/project-tickets/SKILL.md) — user-invoked | dependency-ordered ticket graph (vertical/tracer-bullet slices) | stop; do not auto-start `implement` |
| 5 | One ticket is unblocked and unambiguous | [`implement`](../../skills/implement/SKILL.md) — user-invoked, may offer `agent-config` / call `tdd` internally | bounded diff + tests + local verification | stop at ticket scope; hand to review when appropriate |
| 6 | Artifact needs final acceptance | [`project-review`](../../skills/project-review/SKILL.md) — model-invoked (or manual) via `review-loop` | frozen Charter + reviewer findings + final verdict `PASS`/`FAIL`/`BLOCKED` | stop at verdict |
| 7 | Project passed acceptance | [`release-workflow`](../../skills/release-workflow/SKILL.md) — model-invoked | synchronized docs/catalog/tests, tag, release | stop |

**Optional / parallel:** `decision-map` may replace/augment `project-clarify` for large, foggy, multi-session work — see [clarification-system](clarification-system.md). `implement` may call `tdd`, `diagnosing-bugs`, `resolving-merge-conflicts` as needed — see [execution](execution.md). Review uses `generic-review`/`code-review`/domain reviewers via `review-loop` — see [review-system](review-system.md).

## Unknown or specialized entry

- Vague idea with no project context → [`clarify`](../../skills/clarify/SKILL.md) (standalone, via `socratic`, then stop).
- Don't know the entry → [`ask-light`](../../skills/ask-light/SKILL.md) `next` — one recommendation, wait for approval, then transition according to invocation policy.
- Manuscript / knowledge-base / kanban / learning → [specialized-workflows](specialized-workflows.md).

Composition is explicit. The advisor recommends; the user approves; the accepted
action follows that Skill's invocation policy and the Host's actual capability.
`SKILL.md` remains the contract.
