---
name: agent-config
description: Map the current Agent Host's evidenced models and execution capabilities to a safe, role-clear execution plan. Use before complex multi-agent work when routing, reviewer independence, ownership, or host limits affect the result.
---

# Agent Config

`agent-config` is a model-invoked planning capability. It turns current,
inspectable Agent Host evidence into one executable execution plan. It does
not install agents, change host configuration, spawn work, or merge changes;
those actions remain with the Controller after the plan is accepted. It has no
required companion capability, no external Skill, and no external service.

## Inputs and evidence boundary

Require:

- a bounded task and its acceptance authority;
- change units with exact file ownership and declared dependencies;
- current host evidence per
  [`references/host-evidence-schema.md`](references/host-evidence-schema.md);
- any non-negotiable constraints (reviewer independence, worktree boundary).

A model or capability is **available** only when the current Host evidence
directly verifies it. Treat omitted, stale, contradictory, or unreadable
claims as **unknown**; never promote unknown to available. Honor a concurrency
cap exactly; when no cap is evidenced, schedule one worker at a time or return
`BOUNDARY`. A capability supports only what its evidence states: subagents do
not prove parallelism, and parallelism does not prove isolated worktrees.

## Route selection

Choose the first applicable route and report why more capable routes were not
selected.

1. **Multi-model, multi-agent.** Requires at least two evidenced selectable
   models, subagents, per-agent model selection, parallelism, and independent
   session/threads. Assign roles by role; give each delegated role a named,
   evidenced model. The Reviewer must use a fresh, read-only session/thread
   distinct from the Implementer.
2. **Single-model, multi-agent.** Requires one evidenced selectable model,
   subagents, and independent session/threads. All delegated roles use that
   model; the Reviewer still runs fresh and read-only. Parallel work is limited
   to the evidenced cap and disjoint ownership units.
3. **Single-model, single-agent.** Use when subagents or independent
   session/threads are unavailable or unknown. The Controller executes serially,
   one ownership unit at a time. A self-check is recorded as a self-check, never
   as independent review; if the acceptance source requires an independent
   Reviewer, mark the review gate `BLOCKED` and name the smallest capability
   needed to unblock it.

If no selectable model is available, return `BOUNDARY`.

## Plan

Return the bounded schema in
[`references/plan-schema.md`](references/plan-schema.md), including:

- evidence ledger (state, source, observation time; rejected claims visible);
- role assignment (Controller, Explorer, Implementer, Reviewer, Merger);
- ownership matrix and execution waves (one active unit per file, serial
  overlap, parallelism only within evidenced cap);
- review gate (fresh read-only Reviewer or explicit `BLOCKED`);
- merge rule (one named Merger, serial without worktrees, worktree only when
  evidenced).

Keep the plan executable: do not assume a task board, background scheduler,
remote service, credential, external Skill, or fixed orchestration hierarchy.
Stop after returning the plan; the Controller decides whether to execute it.

## Outcomes

Return `NEED-INPUT` only when a missing choice changes outcome or risk; state
the one decision and its effect. Return `BOUNDARY` when required evidence is
absent, no selectable model exists, or an independent review/parallelism/
worktree requirement cannot be met. A partial plan may mark safe work ready but
must keep the blocked gate visible.