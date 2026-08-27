# Review System — Composition

[中文](../zh-CN/workflows/review-system.md)

This document explains the **Review** composition: reviewer vs engine vs acceptance owner. Do not put final project acceptance back into the engine.

## Separation of concerns

```text
                  review-loop  (lightweight engine)
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
 generic-review  code-review   domain reviewer
        └─────────────┼─────────────┘
                      ▼
                project-review  (acceptance owner)
                      │
               PASS / FAIL / BLOCKED
```

| Role | Skill | Invocation | What it guarantees |
| --- | --- | --- | --- |
| Reviewer | [`generic-review`](../../skills/generic-review/SKILL.md) | model-invoked, read-only | normalized `id`/`severity`/`location`/`problem`/`reason` findings for ordinary artifacts; never repairs or verdicts |
| Reviewer | [`code-review`](../../skills/code-review/SKILL.md) | model-invoked, read-only | Standards + Spec findings for a bounded `git diff`| 
| Engine | [`review-loop`](../../skills/review-loop/SKILL.md) | model-invoked (manual entry ok) | resolves reviewer → invokes → receives findings → returns repair to Producer → re-runs reviewer; stops when clean or at bounded limit |
| Acceptance | [`project-review`](../../skills/project-review/SKILL.md) | model-invoked (manual ok) | freezes Charter/baseline, composes reviewers, drives them through `review-loop`, validates dispositions, issues final `PASS`/`FAIL`/`BLOCKED` |

See the [runtime reviewer contract](../../skills/review-loop/references/reviewer-contract.md) (human summary: [Reviewer contract](../../docs/REVIEWER_CONTRACT.md)) for the normalized input packet (`Target` · `Requirements` · `Relevant context` · `Previous findings`) and result shape (`Findings: []`).

## Entry → Handoff → Stop

| Situation | Entry | Path | Stop |
| --- | --- | --- | --- |
| Generic artifact (no specialist) | `generic-review` via `review-loop` | `review-loop` → `generic-review` → findings → Producer repair → re-review | `Findings: []` or bounded `persists`; engine never issues final verdict |
| Bounded code diff | `code-review` via `review-loop` | `review-loop` → `code-review` (parallel Standards + Spec) → findings | findings only; verdict belongs elsewhere |
| Project needs final acceptance | [`project-review`](../../skills/project-review/SKILL.md) | `project-review init` (freeze Charter/Profile) → `review` (compose reviewers, drive through `review-loop`) → `resume` (continue unfinished action) → fresh Evaluator → `PASS`/`FAIL`/`BLOCKED` | durable verdict + evidence; stop |

## Relationship to `implement`

```text
implement → review-loop + (generic-review | code-review)
implement (+ project) → project-review → review-loop + reviewers
```

`implement` recommends the handoff to the appropriate review path and stops; the reviewer executes the check, the engine tracks convergence, the acceptance owner decides.

## Historical note

The `frozen baseline` / `final verdict` / `PASS`/`FAIL`/`BLOCKED` / `scope-change boundary` capabilities formerly embedded in `review-loop` were migrated to `project-review` (SPEC §25 Phase 7). `review-loop` is intentionally lightweight.
