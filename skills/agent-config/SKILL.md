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
claims as **unknown**; never promote unknown to available. An executable
current model is distinct from selectable models: absence of a model selector
or per-agent model selection does not imply absence of a usable current model.
Honor a concurrency cap exactly; when no cap is evidenced, schedule one worker
at a time or return `BOUNDARY`. A capability supports only what its evidence
states: subagents do not prove parallelism, parallelism does not prove
isolated worktrees, and an executable current model does not prove selectable
models.

## Route selection

Choose the first applicable route and report why more capable routes were not
selected.

1. **Multi-model, multi-agent.** Requires at least two evidenced selectable
   models, subagents, per-agent model selection, parallelism, and independent
   session/threads. Assign roles by role; give each delegated role a named,
   evidenced model. The Reviewer must use a fresh, read-only session/thread
   distinct from the Implementer.
2. **Single-model / fixed-model, multi-agent.** Requires one evidenced current
   executable model (or selectable model), subagents, and independent
   session/threads, even if model selection or per-agent model selection is
   unavailable. All delegated roles use the current model; the Reviewer still
   runs fresh and read-only. Parallel work is limited to the evidenced cap and
   disjoint ownership units.
3. **Single-model / fixed-model, single-agent.** Use when subagents or
   independent session/threads are unavailable or unknown. The Controller
   executes serially using the current executable model, one ownership unit at
   a time. A self-check is recorded as a self-check, never as independent
   review; if the acceptance source requires an independent Reviewer, mark
   only the review gate `BLOCKED` and name the smallest capability needed to
   unblock it. Do not block the entire plan if safe implementation work can
   still proceed.

If no current executable model or selectable model is available, return
`BOUNDARY`.

## Plan

Return the bounded schema in
[`references/plan-schema.md`](references/plan-schema.md), including:

- evidence ledger (state, source, observation time; rejected claims visible);
- role assignment (Controller, Explorer, Implementer, Reviewer, Merger);
- ownership matrix and execution waves (one active unit per file, serial
  overlap, parallelism only within evidenced cap);
- review gate (fresh read-only Reviewer, self-check, or explicit `BLOCKED`);
- merge rule (one named Merger, serial without worktrees, worktree only when
  evidenced).

Keep the plan executable: do not assume a task board, background scheduler,
remote service, credential, external Skill, or fixed orchestration hierarchy.
Stop after returning the plan; the Controller decides whether to execute it.

## Outcomes

Return `NEED-INPUT` only when a missing choice changes outcome or risk; state
the one decision and its effect. Return `BOUNDARY` when required evidence is
absent, no executable or selectable model exists, or an explicit hard requirement
cannot be met. Do not return `BOUNDARY` solely because a model selector is
unavailable. A partial plan may mark safe work ready but must keep the blocked
gate visible.