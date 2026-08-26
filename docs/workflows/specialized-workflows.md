# Specialized Workflows — Composition

[中文](../zh-CN/workflows/specialized-workflows.md)

This document explains the **Specialized Workflows**: their standalone nature and optional composition with the main workflow. They are not required members of `project-init → … → release-workflow`.

## Skills in this group

- [`manuscript-ops`](../../skills/manuscript-ops/SKILL.md) — manuscript engineering state machine
- [`kb-init`](../../skills/kb-init/SKILL.md) — knowledge-base design via interview + approval-gated implementation
- [`learn-anything`](../../skills/learn-anything/SKILL.md) — distill evidenced sources into reusable Skill methods
- [`language-learning`](../../skills/language-learning/SKILL.md) — six-mode language tutor
- [`kanban-worker`](../../skills/kanban-worker/SKILL.md) — one-task-per-wake Light-Kanban worker
- [`recap`](../../skills/recap/SKILL.md) — one-line session summary (`$recap` only)
- [`eli5`](../../skills/eli5/SKILL.md) — explain at a chosen audience level
- [`release-workflow`](../../skills/release-workflow/SKILL.md) — publish after acceptance (also closes the project workflow)

## Standalone vs composition

All eight were verified for:

1. **Standalone correctness** — the Skill fulfills its own `SKILL.md` contract without requiring the project workflow.
2. **Composition fit** — its output can be handed to another Skill without hidden rework.

Rule: if the output already hands off naturally (e.g., a deliverable, a Method Contract, a Kanban `complete`), **do not modify the Skill**. Only when a real integration gap exists is a minimal handoff sentence allowed:

```text
When this workflow reaches <state>, the caller may continue with <skill>.
```

or

```text
Return <artifact/result> to the calling workflow.
```

Adding a handoff line is not a redesign.

## Entry → Handoff → Stop

| Skill | Typical standalone entry | Natural handoff (optional) | Stop |
| --- | --- | --- | --- |
| [`manuscript-ops`](../../skills/manuscript-ops/SKILL.md) | manuscript scope/risk/batches/formats | May call `clarify`/`decision-map` via user choice; may hand its approved brief/Charter to `project-review` (`manuscript` Profile) | stop at routing decision, Charter freeze, or QA'd deliverable |
| [`kb-init`](../../skills/kb-init/SKILL.md) | ` $kb-init` | Interview → approved SPEC → implementation; may call `research` for external facts | stop at design or initialized KB |
| [`learn-anything`](../../skills/learn-anything/SKILL.md) | source with possible repeated method | Internal Method Contract → deterministic package builder → `project-review` (via `review-loop`) → catalog/doc sync | stop at `method_contract` / `not_promoted` / `BLOCKED` |
| [`language-learning`](../../skills/language-learning/SKILL.md) | language-learning request | Lessons/flashcards/conversation/grammar/quiz/translation each return their artifact | stop at lesson or quiz result |
| [`kanban-worker`](../../skills/kanban-worker/SKILL.md) | scheduled wake | `complete` or `block` with reason; next wake picks `reviewFeedback` before new claims | stop after one task |
| [`recap`](../../skills/recap/SKILL.md) | `$recap` | exactly one line of session summary; never continues work | stop |
| [`eli5`](../../skills/eli5/SKILL.md) | explain request | audience-tailored explanation | stop |
| [`release-workflow`](../../skills/release-workflow/SKILL.md) | ready to publish after `project-review PASS` | tag / GitHub Release / synchronized docs | stop at release record |

## How they meet the main workflow

- A project discovered via `project-clarify` may be routed to `manuscript-ops` or `kb-init` when domain specialization is more appropriate than generic `project-spec`.
- A reusable method from `learn-anything` may be admitted as a new Skill and then participate in future `implement` work.
- `kanban-worker` decomposes larger work already created by `project-tickets` and reports `complete`/`block`.
- `release-workflow` is both a specialized closer and the tail of the project workflow.
- When unsure, [`ask-light`](../../skills/ask-light/SKILL.md) routes to the appropriate specialized Skill.

No forced unification. Each package keeps its own shape (`references/`, `templates/`, `scripts/` as it actually needs).
