---
name: agent-config
description: Map the current Agent Host's evidenced models, reasoning effort, and execution capabilities to a right-sized model and execution configuration. Use before complex work when model tier, reasoning effort, or execution topology affects the result.
---

# Agent Config

`agent-config` is a model-invoked host-aware model and execution configurator.
It turns current, inspectable Agent Host evidence and task characteristics into
a right-sized model, effort, and execution plan.

It does not install agents, automatically mutate host/project configuration, spawn
unapproved background work, or merge changes; execution remains with the Controller
after the plan is accepted. It has no required companion capability, no external Skill,
and no external service requirements.

## Inputs and boundaries

Require:
- a bounded task or ticket graph and its acceptance authority;
- current host evidence per [`references/host-evidence-schema.md`](references/host-evidence-schema.md);
- task assessment per [`references/task-assessment.md`](references/task-assessment.md);
- optional provider adapter metadata per [`references/provider-adapter-contract.md`](references/provider-adapter-contract.md).

### Capability invariants

- A capability is **available** only when current host evidence directly verifies it.
  Omitted, stale, or contradictory claims are **unknown**; never promote unknown to available.
- `models.current` (active executable model) is distinct from `models.selectable`.
- `routing_rank` must originate from verified host runtime or provider manifest metadata.
  If multiple models lack trusted ranking, do not guess relative intelligence; fall back
  to fixed-model execution mode.
- Subagents do not prove parallelism, parallelism does not prove isolated worktrees,
  and a model selector does not prove per-agent model assignment.
- Concurrency limits require a positive integer evidenced by host runtime. Without evidence,
  run serially or within verified limits.
- When `reasoning_control` is unavailable or unknown, proceed with default reasoning behavior
  without returning `BOUNDARY`.

## Decision grid: Provider mode × Task shape

Select the operating mode across two primary dimensions:

```text
                   Task Shape
              Single-pass     Decomposed
             ┌──────────────┬──────────────┐
Tiered       │ Mode 1:      │ Mode 2:      │
Multi-model  │ Multi +      │ Multi +      │
             │ Single-pass  │ Decomposed   │
             ├──────────────┼──────────────┤
Fixed        │ Mode 3:      │ Mode 4:      │
Single-model │ Single +     │ Single +     │
             │ Single-pass  │ Decomposed   │
             └──────────────┴──────────────┘
```

1. **Provider mode:**
   - `tiered-multi-model`: At least two available selectable models with trusted relative
     `routing_rank`, an active selection mechanism, and supported execution context.
   - `fixed-single-model`: One executable model, unranked models, or absence of per-context
     model selection.
2. **Task shape:**
   - `single-pass`: Bounded cohesive unit safe in one continuous context window.
   - `decomposed`: Multiple independent or dependency-ordered work units/tickets.
   - *Never use word count or SPEC length as a proxy for task shape.*

---

## Four execution modes

### Mode 1 — Tiered Multi-model + Single-pass
- Right-size implementation to the minimum sufficient model rank and appropriate effort.
- Default to single-session execution; do not create helper subagents unless focused research
  or isolated exploration materially reduces controller burden.
- Review strategy: Recommend a higher model rank and higher effort when supported (fresh
  thread if available, else self-check).
- Do not output execution waves, ownership matrices, or separate Explorer/Merger roles.

### Mode 2 — Tiered Multi-model + Decomposed
- If tickets do not exist yet: return `Execution readiness: needs-project-tickets` and hand
  off to `project-tickets`. Never persist tickets directly.
- When tickets exist:
  - Controller runs on the highest evidenced model rank with high/max effort.
  - Worker assignments scale monotonically with difficulty: demanding/critical tickets
    receive higher tier and effort; routine tickets receive economical tiers.
  - Parallelism is scheduled only for ready, disjoint tickets within evidenced concurrency caps.
  - Each ticket executes via an independent `$implement <ticket>` run; never batch sibling tickets.
  - Controller performs integration review; formal convergence is handed to `review-loop`.

### Mode 3 — Fixed Single-model + Single-pass
- Direct execution using the current model at maximum supported effort in the current session.
- No artificial role matrices (no identical Controller, Implementer, Reviewer entries).
- Subagents are used only for bounded exploration, research, or isolated testing.
- Missing reasoning controls continue with host defaults without returning `BOUNDARY`.

### Mode 4 — Fixed Single-model + Decomposed
- All execution contexts, Controller, and workers use the same model at maximum supported effort.
- Value focuses on ticket scheduling, session/thread distribution, dependencies, and concurrency.
- Controller oversees the frontier and conducts integration review.
- If subagents or threads are unavailable, execution degrades safely to serial execution.

---

## Roles and review semantics

- **Roles are conditional:**
  - Controller: Defaults to current session; coordinates decomposed execution.
  - Implementer: Active implementer of a specific work item.
  - Explorer: Included only when research or exploration is specifically delegated.
  - Reviewer: Included only when a distinct, fresh review context is established.
  - Merger: Included only when worktree or integration topology requires an isolated role.
- **Review semantics:**
  - `Controller Review`: Controller inspecting outputs from delegated workers.
  - `Self-check`: Executor checking its own diff; never called independent review.
  - `Independent Review`: Read-only review in a fresh session/thread, ideally at equal
    or higher model rank and effort.
  - Formal convergence belongs to `review-loop`; project acceptance belongs to `project-review`.

---

## Adapter and mutation boundaries

- **Read-only by default:** Invocations return `Apply mode: plan-only`. The engine never
  mutates configuration files automatically.
- **Explicit user approval:** Calling an adapter to apply project-level agent configuration
  requires explicit user consent (`Apply mode: applied`).
- **Graceful adapter absence/failure:** If no adapter exists or an adapter fails, record
  the limitation and continue with the plan in manual Controller mode. Never return `BOUNDARY`
  for missing adapter tooling.

---

## Output contract and status

Output conforms to [`references/plan-schema.md`](references/plan-schema.md).

- `Status: READY`: At least one usable executable model and a safe path defined.
- `Status: NEED-INPUT`: Missing choice that fundamentally alters scope, spend, or risk.
- `Status: BOUNDARY`: No executable model available or an unfulfillable hard constraint.
  Mark isolated blocked gates specifically; do not block unblocked serial work.
