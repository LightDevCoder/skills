---
name: agent-config
description: Map the current Agent Host's evidenced models and execution capabilities to a safe, role-clear execution plan. Use before complex multi-agent work when routing, reviewer independence, ownership, or host limits affect the result.
---

# Agent Config

`agent-config` is a model-invoked planning capability. It turns current,
inspectable Agent Host evidence into one executable execution plan. It does not
install agents, change host configuration, spawn work, select an unavailable
model, create a worktree, or merge changes. Those actions remain with the
Controller after the plan is accepted.

It has no required companion capability, no external Skill, and no external
service.

Use it when a task needs several roles, independent review, isolation, or
parallel work and the Host's model and agent capabilities affect the safe
structure. Do not use it for a bounded solo task whose execution structure is
already settled.

## Inputs and evidence boundary

Require these inputs:

- a bounded task and its acceptance authority;
- change units with exact file ownership and declared dependencies;
- current host evidence following
  [`references/host-evidence-schema.md`](references/host-evidence-schema.md);
- any non-negotiable constraints, especially reviewer independence or a
  required worktree boundary.

Read the supplied host evidence before choosing a route. A model or capability
is **available** only when the current Host evidence directly verifies it.
Treat an omitted claim, stale/unreadable evidence, a contradiction, a model
name seen only in conversation, and an unsupported inferred capability as
**unknown**. Do not promote unknown to available. Treat unavailable as
unavailable. Never guess a model inventory from memory and never encode a
provider-specific model or lane name into the plan.

If the host exposes a concurrency cap, honor it exactly. If it does not, do
not invent a number: schedule one worker at a time or return `BOUNDARY` when
the task requires parallelism. A capability can support only the operation
that its evidence states; for example, subagents do not prove parallelism,
and parallelism does not prove isolated worktrees.

## Select exactly one route

Choose the first applicable route below. Report why every more capable route
was not selected.

1. **Multi-model, multi-agent.** Select this only when at least two distinct
   selectable models, subagents, per-agent model selection, parallelism, and
   the needed independent session/thread are all available. Assign the
   Controller, Explorer, Implementer, Reviewer, and Merger by role, not by
   product-specific model name. Assign a named, evidenced model to every
   delegated role. The Reviewer must use a fresh session/thread and be
   read-only; it must not be the implementing agent.
2. **Single-model, multi-agent.** Select this when exactly one selectable
   model is available and subagents plus the needed independent
   session/thread are available. All delegated roles use that one model, but
   the Reviewer still runs in a fresh, read-only agent/session distinct from
   the Implementer. Parallel work is allowed only up to the evidenced cap and
   only for disjoint ownership units.
3. **Single-model, single-agent.** Select this when subagents or an independent
   session/thread are unavailable or unknown. The Controller
   performs exploration and implementation serially, one ownership unit at a
   time. It records a self-check as a self-check, never as independent review.
   If the acceptance source requires an independent Reviewer, return a plan
   with the execution work `READY` and the final review gate `BLOCKED`; name
   the smallest host capability needed to unblock it.

If no selectable model is available, return `BOUNDARY` rather than pretending
that a single-agent route can run. A route may be simplified as the evidence
requires, but no role may silently inherit a different model, execution lane,
or authority.

## Build the plan

Return the bounded schema in
[`references/plan-schema.md`](references/plan-schema.md). It must include:

- **Evidence ledger:** each model and capability used, its state, source, and
  observation time; unknown and rejected claims remain visible.
- **Role assignment:** Controller, Explorer, Implementer, Reviewer, and
  Merger. Controller owns routing, scope resolution, evidence verification,
  and final handoff. Explorer investigates only its assigned question;
  Implementer changes only assigned files; Reviewer is read-only and has no
  implementation ownership; Merger is exactly one named role and applies no
  unreviewed conflict resolution.
- **Ownership matrix and waves:** every file belongs to one active change
  unit. Units with overlapping files run serially. Units without overlap may
  run together only when the Host evidence supports parallelism and the wave
  respects the concurrency cap. Do not issue duplicate investigation or
  implementation assignments.
- **Review gate:** independent review must be a fresh session/thread distinct
  from every Implementer, use the frozen scope and accumulated diff, and
  return findings without edits. When this cannot be supplied, state
  `BLOCKED`; do not rename a Controller self-check as a Reviewer.
- **Merge rule:** the Merger integrates only completed, verified ownership
  units. With no worktrees, serially integrate one unit before the next; do
  not claim isolated merging. With worktrees, assign a worktree only when the
  Host evidence makes worktrees available.

Keep the plan executable, not aspirational. Do not assume a task board,
background scheduler, remote service, credential, external Skill, or a fixed
orchestration hierarchy. Stop after returning this plan; the Controller
decides whether to execute it.

## Questions and boundary outcomes

Return `NEED-INPUT` only when a missing choice changes outcome or risk, such
as overlapping ownership that must be split, an acceptance source that is
unclear about independent review, or a choice between two evidenced models
with materially different authorization. State the one decision and its
effect.

When one safe route follows from the evidence, return it without asking a
preference question. Return `BOUNDARY` when required host evidence is absent,
when no selectable model is available, or when a required independent review,
parallelism, or worktree isolation cannot be provided. A partial plan may
identify work that is safe to execute, but it must keep the blocked gate
visible and must not present the task as accepted.
