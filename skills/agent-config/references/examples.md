# Execution plan examples

These examples illustrate the adaptive output produced across the four execution
modes defined by `agent-config`.

---

## Example 1: Tiered Multi-model + Single-pass (Multi + Small)

**Context:** Host profile maps confirmed tiers (`routine`: `model-alpha`, `standard`: `model-beta`, `high`/`review`: `model-gamma`)
with tunable reasoning control. Task is a moderate single-pass bug fix in a parser.

```markdown
Readiness: READY
Scope: current-item
Provider mode: tiered-multi-model
Task shape: single-pass
Execution status: executable
Apply mode: plan-only

Reason: Tiered multi-model profile available; task is a bounded single-pass fix. Right-sizing implementation to sufficient model tier (standard) while reserving review tier (review) for verification.

## Host summary
- Current model: model-beta (available)
- Selectable models / tiers: model-alpha (routine), model-beta (standard), model-gamma (high, review)
- Reasoning control: available (supported: low, medium, high)
- Context & execution: subagents available, threads available, parallelism available (cap: 3)
- Adapter: none (plan-only)

## Task assessment
- Task shape: single-pass
- Assessment rationale: Bounded parser bug fix confined to single module; tests verify directly.
- Work-item difficulty: moderate

## Execution config

| Phase | Model / tier | Effort | Context | Purpose |
|---|---|---|---|---|
| Implementation | model-beta (standard) | medium | current-session | Implement AST parser edge-case fix and unit tests |

```json
{
  "task_shape": "single-pass",
  "model_mode": "multi",
  "readiness": "executable",
  "reason": "Tiered multi-model single-pass task right-sized to standard tier",
  "topology": {
    "type": "single-session",
    "concurrency": 1
  },
  "execution": {
    "model": "model-beta",
    "effort": "medium",
    "context": "current-session"
  },
  "review": {
    "strategy": "independent-review",
    "tier": "review",
    "model": "model-gamma",
    "effort": "high",
    "context": "fresh-thread"
  }
}
```

## Review strategy
- Review type: Independent Review
- Review model & effort: model-gamma (review), effort: high, context: fresh session context
- Review handoff: Hand verified diff to review-loop with code-review

## Limitations / unknowns
- No isolated worktree available; implementation runs in working directory.
```

---

## Example 2: Tiered Multi-model + Decomposed (Multi + Large)

**Context:** Host profile maps confirmed tiers with concurrency cap 3. The task has 4 tickets
on the local tracker (01 routine, 02 moderate, 03 demanding, 04 critical).

```markdown
Readiness: READY
Scope: ticket-graph
Provider mode: tiered-multi-model
Task shape: decomposed
Execution status: executable
Apply mode: plan-only

Reason: Tiered host with active tickets. Monotonically scaling model tiers and effort with ticket difficulty; Controller runs on high/review tier; parallelizing unblocked tickets within cap.

## Host summary
- Current model: model-gamma (available)
- Selectable models / tiers: model-alpha (routine), model-beta (standard), model-gamma (high, review)
- Reasoning control: available (low, medium, high)
- Context & execution: subagents available, threads available, parallelism available (cap: 3)
- Adapter: none (plan-only)

## Task assessment
- Task shape: decomposed
- Assessment rationale: Multi-tier architectural refactor with formal ticket graph and blocking edges.
- Work-item difficulty: routine to critical

## Execution config

### Work-item routing

| Ticket | Difficulty | Model / tier | Effort | Context | Dependencies | Review |
|---|---|---|---|---|---|---|
| 01-schema-types | routine | model-alpha (routine) | low | subagent-1 | None (Ready) | Controller Review |
| 02-api-endpoint | moderate | model-beta (standard) | medium | subagent-2 | None (Ready) | Controller Review |
| 03-auth-policy | demanding | model-gamma (high) | high | subagent-3 | None (Ready) | Controller Review |
| 04-audit-cutover | critical | model-gamma (high) | high | serial | Blocked by 01, 02, 03 | Independent Review |

```json
{
  "task_shape": "decomposed",
  "model_mode": "multi",
  "readiness": "executable",
  "reason": "Tiered multi-model decomposed execution with per-ticket tier routing",
  "topology": {
    "type": "controller-workers",
    "concurrency": 3,
    "fresh_contexts": true,
    "subagent_contexts": true
  },
  "controller": {
    "model": "model-gamma",
    "effort": "high",
    "context": "current-session"
  },
  "work_items": [
    {
      "ticket_id": "01",
      "difficulty": "routine",
      "tier": "routine",
      "model": "model-alpha",
      "effort": "low",
      "context": "subagent-1",
      "review_strategy": "controller-review"
    },
    {
      "ticket_id": "02",
      "difficulty": "moderate",
      "tier": "standard",
      "model": "model-beta",
      "effort": "medium",
      "context": "subagent-2",
      "review_strategy": "controller-review"
    },
    {
      "ticket_id": "03",
      "difficulty": "demanding",
      "tier": "high",
      "model": "model-gamma",
      "effort": "high",
      "context": "subagent-3",
      "review_strategy": "independent-review"
    }
  ],
  "review": {
    "strategy": "independent-review",
    "tier": "review",
    "model": "model-gamma",
    "effort": "high",
    "context": "fresh-thread"
  }
}
```

### Coordination

- Controller: model-gamma (high), effort: high, context: current-session
- Concurrency cap: 3 concurrent workers (tickets 01, 02, 03 execute in parallel)
- Frontier: tickets 01, 02, 03 are unblocked ready work
- Integration: Workers return to Controller; Controller conducts integration review; final acceptance handed to project-review

## Review strategy
- Review type: Controller Review for worker integration; final project-review upon ticket graph completion
- Review model & effort: model-gamma (review), effort: high
- Review handoff: review-loop / project-review

## Limitations / unknowns
- Ticket 04 requires completion and merge of 01-03 before scheduling.
```

---

## Example 3: Single-model + Single-pass (Single + Small)

**Context:** Host provides only a single executable model (`model-alpha`). Task is a small typo/refactor.

```markdown
Readiness: READY
Scope: current-item
Provider mode: single-model
Task shape: single-pass
Execution status: executable
Apply mode: plan-only

Reason: Single-model host; single-pass solo task. Direct execution with current model at resolved effort (high) without artificial multi-agent bureaucracy.

## Host summary
- Current model: model-alpha (available)
- Selectable models / tiers: single model
- Reasoning control: available (supported: standard, high)
- Context & execution: subagents unavailable, threads unavailable
- Adapter: none (plan-only)

## Task assessment
- Task shape: single-pass
- Assessment rationale: Local edit touching documentation and one constant; trivial verification.
- Work-item difficulty: routine

## Execution config

| Phase | Model / tier | Effort | Context | Purpose |
|---|---|---|---|---|
| Implementation | model-alpha | high | current-session | Direct single-pass implementation |

```json
{
  "task_shape": "single-pass",
  "model_mode": "single",
  "readiness": "executable",
  "reason": "Single model direct execution for bounded single-pass task",
  "topology": {
    "type": "single-session",
    "concurrency": 1
  },
  "execution": {
    "model": "model-alpha",
    "effort": "high",
    "context": "current-session"
  },
  "review": {
    "strategy": "self-check",
    "model": "model-alpha",
    "effort": "high",
    "context": "current-session"
  }
}
```

## Review strategy
- Review type: Self-check
- Review model & effort: model-alpha, effort: high, context: current-session
- Review handoff: Self-check against tests; review-loop when requested

## Limitations / unknowns
- Fresh session threads unavailable; reviewer independence marked as Self-check.
```

---

## Example 4: Single-model + Decomposed (Single + Large)

**Context:** Host provides a single model (`model-alpha`), but supports subagent threads and parallelism (cap: 2). Task consists of multiple tickets.

```markdown
Readiness: READY
Scope: ticket-graph
Provider mode: single-model
Task shape: decomposed
Execution status: executable
Apply mode: plan-only

Reason: Fixed single-model host with multi-ticket workload. All contexts utilize the single model with confirmed effort policy; execution coordinates ticket dependencies and thread scheduling.

## Host summary
- Current model: model-alpha (available)
- Selectable models / tiers: fixed single model
- Reasoning control: unavailable (host default)
- Context & execution: subagents available, threads available, parallelism available (cap: 2)
- Adapter: none (plan-only)

## Task assessment
- Task shape: decomposed
- Assessment rationale: Work spans 3 distinct modules organized as numbered tickets.
- Work-item difficulty: moderate to demanding

## Execution config

### Work-item routing

| Ticket | Difficulty | Model / tier | Effort | Context | Dependencies | Review |
|---|---|---|---|---|---|---|
| 01-db-layer | moderate | model-alpha | default | thread-A | None (Ready) | Controller Review |
| 02-service-layer | moderate | model-alpha | default | thread-B | None (Ready) | Controller Review |
| 03-api-gateway | demanding | model-alpha | default | thread-A | Blocked by 01, 02 | Controller Review |

```json
{
  "task_shape": "decomposed",
  "model_mode": "single",
  "readiness": "executable",
  "reason": "Single model decomposed execution with Controller coordinating fresh contexts",
  "topology": {
    "type": "serial-tickets",
    "concurrency": 2,
    "fresh_contexts": true,
    "subagent_contexts": true
  },
  "controller": {
    "model": "model-alpha",
    "context": "current-session"
  },
  "work_items": [
    {
      "ticket_id": "01",
      "difficulty": "moderate",
      "model": "model-alpha",
      "context": "thread-A",
      "review_strategy": "controller-review"
    },
    {
      "ticket_id": "02",
      "difficulty": "moderate",
      "model": "model-alpha",
      "context": "thread-B",
      "review_strategy": "controller-review"
    },
    {
      "ticket_id": "03",
      "difficulty": "demanding",
      "model": "model-alpha",
      "context": "thread-A",
      "dependencies": ["01", "02"],
      "review_strategy": "controller-review"
    }
  ],
  "review": {
    "strategy": "controller-review",
    "model": "model-alpha",
    "context": "current-session"
  }
}
```

### Coordination

- Controller: model-alpha, context: current-session
- Concurrency cap: 2 concurrent threads (tickets 01 and 02 run concurrently)
- Frontier: tickets 01 and 02 are ready
- Integration: Controller integrates worker diffs into main working tree and coordinates tests

## Review strategy
- Review type: Controller Review
- Review model & effort: model-alpha, context: current-session
- Review handoff: review-loop

## Limitations / unknowns
- Single model throughout; no intelligence tiering available on this host.
```
