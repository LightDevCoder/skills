# Execution plan examples

These examples illustrate the adaptive output produced across the four execution
modes defined by `agent-config`.

---

## Example 1: Tiered Multi-model + Single-pass (Multi + Small)

**Context:** Host provides 3 model ranks (`model-alpha`: 1, `model-beta`: 2, `model-gamma`: 3)
with tunable reasoning control. Task is a moderate single-pass bug fix in a parser.

```markdown
Status: READY
Scope: current-item
Provider mode: tiered-multi-model
Task shape: single-pass
Execution readiness: executable
Apply mode: plan-only

Reason: Tiered multi-model host available; task is a bounded single-pass fix. Right-sizing implementation to sufficient model tier (rank 2) while reserving highest tier (rank 3) for review.

## Host summary
- Current model: model-beta (available, routing_rank: 2)
- Selectable models / ranks: model-alpha (1), model-beta (2), model-gamma (3)
- Reasoning control: available (levels: low, medium, high; scopes: current-session, per-agent)
- Context & execution: subagents available, session_threads available, parallelism available (cap: 3)
- Adapter: none (plan-only)

## Task assessment
- Task shape: single-pass
- Assessment rationale: Bounded parser bug fix confined to single module; tests verify directly.
- Work-item difficulty: moderate

## Execution config

| Phase | Model / tier | Effort | Context | Purpose |
|---|---|---|---|---|
| Implementation | model-beta (rank 2) | medium | current-session | Implement AST parser edge-case fix and unit tests |

## Review strategy
- Review type: Independent Review
- Review model & effort: model-gamma (rank 3), effort: high, context: fresh session_thread
- Review handoff: Hand verified diff to review-loop with code-review

## Limitations / unknowns
- No isolated worktree available; implementation runs in working directory.
```

---

## Example 2: Tiered Multi-model + Decomposed (Multi + Large)

**Context:** Host provides 3 model ranks with concurrency cap 3. The task has 4 tickets
on the local tracker (01 routine, 02 moderate, 03 demanding, 04 critical).

```markdown
Status: READY
Scope: ticket-graph
Provider mode: tiered-multi-model
Task shape: decomposed
Execution readiness: executable
Apply mode: plan-only

Reason: Tiered host with active tickets. Monotonically scaling model ranks and effort with ticket difficulty; Controller runs on highest tier; parallelizing unblocked tickets within cap.

## Host summary
- Current model: model-gamma (available, routing_rank: 3)
- Selectable models / ranks: model-alpha (1), model-beta (2), model-gamma (3)
- Reasoning control: available (low, medium, high)
- Context & execution: subagents available, session_threads available, parallelism available (cap: 3)
- Adapter: none (plan-only)

## Task assessment
- Task shape: decomposed
- Assessment rationale: Multi-tier architectural refactor with formal ticket graph and blocking edges.
- Work-item difficulty: routine to critical

## Execution config

### Work-item routing

| Ticket | Difficulty | Model / tier | Effort | Context | Dependencies | Review |
|---|---|---|---|---|---|---|
| 01-schema-types | routine | model-alpha (rank 1) | low | subagent-1 | None (Ready) | Controller Review |
| 02-api-endpoint | moderate | model-beta (rank 2) | medium | subagent-2 | None (Ready) | Controller Review |
| 03-auth-policy | demanding | model-gamma (rank 3) | high | subagent-3 | None (Ready) | Controller Review |
| 04-audit-cutover | critical | model-gamma (rank 3) | high | serial | Blocked by 01, 02, 03 | Independent Review |

### Coordination

- Controller: model-gamma (rank 3), effort: high, context: current-session
- Concurrency cap: 3 concurrent workers (tickets 01, 02, 03 execute in parallel)
- Frontier: tickets 01, 02, 03 are unblocked ready work
- Integration: Workers return to Controller; Controller conducts integration review; final acceptance handed to project-review

## Review strategy
- Review type: Controller Review for worker integration; final project-review upon ticket graph completion
- Review model & effort: model-gamma (rank 3), effort: high
- Review handoff: review-loop / project-review

## Limitations / unknowns
- Ticket 04 requires completion and merge of 01-03 before scheduling.
```

---

## Example 3: Fixed Single-model + Single-pass (Single + Small)

**Context:** Host provides only a single executable model (`model-alpha`). Task is a small typo/refactor.

```markdown
Status: READY
Scope: current-item
Provider mode: fixed-single-model
Task shape: single-pass
Execution readiness: executable
Apply mode: plan-only

Reason: Single-model host; single-pass solo task. Direct execution with current model at maximum supported effort without artificial multi-agent bureaucracy.

## Host summary
- Current model: model-alpha (available)
- Selectable models / ranks: fixed single model
- Reasoning control: available (levels: standard, high)
- Context & execution: subagents unavailable, session_threads unavailable
- Adapter: none (plan-only)

## Task assessment
- Task shape: single-pass
- Assessment rationale: Local edit touching documentation and one constant; trivial verification.
- Work-item difficulty: routine

## Execution config

| Phase | Model / tier | Effort | Context | Purpose |
|---|---|---|---|---|
| Implementation | model-alpha | high | current-session | Direct single-pass implementation |

## Review strategy
- Review type: Self-check
- Review model & effort: model-alpha, effort: high, context: current-session
- Review handoff: Self-check against tests; review-loop when requested

## Limitations / unknowns
- Fresh session threads unavailable; reviewer independence marked as Self-check.
```

---

## Example 4: Fixed Single-model + Decomposed (Single + Large)

**Context:** Host provides a single model (`model-alpha`), but supports subagent threads and parallelism (cap: 2). Task consists of multiple tickets.

```markdown
Status: READY
Scope: ticket-graph
Provider mode: fixed-single-model
Task shape: decomposed
Execution readiness: executable
Apply mode: plan-only

Reason: Fixed single-model host with multi-ticket workload. All contexts utilize the single model at maximum effort; execution coordinates ticket dependencies and thread scheduling.

## Host summary
- Current model: model-alpha (available)
- Selectable models / ranks: fixed single model
- Reasoning control: unavailable (host default)
- Context & execution: subagents available, session_threads available, parallelism available (cap: 2)
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
