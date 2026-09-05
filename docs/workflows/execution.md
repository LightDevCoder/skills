# Execution — Composition

[中文](../zh-CN/workflows/execution.md)

This document explains the **Execution** composition: entry, routing, and handoff. Internal step-by-step workflows live in each Skill's `SKILL.md` and `references/`.

## Skills in this group

- [`implement`](../../skills/implement/SKILL.md) — user-invoked general-purpose bounded executor
- [`agent-config`](../../skills/agent-config/SKILL.md) — model-invoked profile-driven cross-harness execution configurator
- [`tdd`](../../skills/tdd/SKILL.md) — model-invoked test-driven loop
- [`diagnosing-bugs`](../../skills/diagnosing-bugs/SKILL.md) — model-invoked diagnosis loop
- [`resolving-merge-conflicts`](../../skills/resolving-merge-conflicts/SKILL.md) — model-invoked merge/rebase resolver

All are first-party and self-contained; no install of `mattpocock/skills` or `sol-advisor` is required.

## Entry → Handoff → Stop

| Situation | Entry | Typical path | Handoff / Stop |
| --- | --- | --- | --- |
| One clear ticket / SPEC slice | [`implement`](../../skills/implement/SKILL.md) — user-invoked | `implement` → inspect context → *optional* `agent-config` offer (when profile routing, review isolation, or topology materially helps) → execute → verify → hand to `review-loop` with the right reviewer | bounded diff + focused tests + verification evidence; stop at ticket scope |
| Need to configure model, effort, or execution topology | [`agent-config`](../../skills/agent-config/SKILL.md) — model-invoked | requires: bounded task or ticket graph + acceptance authority + current host evidence + confirmed profile; determines provider mode and task shape, right-sizes model tier & effort across four execution modes (Cases A, B, C, D) | profile-driven execution plan, not execution; executor performs work per plan |
| Code feature/fix should be test-first | [`tdd`](../../skills/tdd/SKILL.md) — model-invoked | `red → green → refactor` with real tests | tests + implementation slice |
| Hard bug / regression | [`diagnosing-bugs`](../../skills/diagnosing-bugs/SKILL.md) — model-invoked | build a tight `pass/fail` signal → reproduce → hypothesize → instrument → fix → cleanup | fix with feedback loop evidence |
| Merge/rebase conflict | [`resolving-merge-conflicts`](../../skills/resolving-merge-conflicts/SKILL.md) — model-invoked | resolve conflicted files per git guidance | clean working tree ready for verification |

## Two-Repository Architecture: Skill and Companion

The execution configuration system cleanly separates policy reasoning from host persistence and mutation:

- **Skill (`skills/agent-config`):** Installed from this repository ([LightDevCoder/skills](https://github.com/LightDevCoder/skills)). Performs task difficulty assessment, tier selection, and execution topology planning. Runs locally in the agent conversation.
- **Companion MCP Runtime:** Maintained in the independent repository [LightDevCoder/agent-config](https://github.com/LightDevCoder/agent-config). Provides 9 native host adapters (Codex, Claude Code, Antigravity / agy, DeepSeek Harness / DSH, OpenCode, ZCode, Cursor, Grok Build, Hermes) plus generic fallback.
- **Optional Companion:** Without the companion MCP server registered, `agent-config` remains fully operational in session-local, plan-only mode without mutating host configuration. With the companion installed and registered, it enables authentic host capability inspection, profile persistence, configuration preview before apply, and health validation.

## Composition with review

`implement` does not copy reviewer instructions. Coding work follows:

```text
implement → tdd (when appropriate) → code changes + tests → review-loop → code-review
```

Non-coding work:

```text
implement → artifact → review-loop → generic-review / domain reviewer
```

The reviewer is read-only; `review-loop` is the convergence engine; `project-review` (see [review-system](review-system.md)) owns final `PASS`/`FAIL`/`BLOCKED` when project acceptance is needed.

## When not to use this group

- Vague idea → [clarification-system](clarification-system.md) first.
- Approved SPEC → [`project-tickets`](../../skills/project-tickets/SKILL.md) before `implement`.
- Completed project → [`project-review`](../../skills/project-review/SKILL.md) / [review-system](review-system.md).
- Unknown entry → [`ask-light`](../../skills/ask-light/SKILL.md).
