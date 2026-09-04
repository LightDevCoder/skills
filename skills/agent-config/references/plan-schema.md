# Execution plan schema

`agent-config` outputs an adaptive, Markdown-formatted execution plan.
Formatting scales with task shape: single-pass tasks emit a concise configuration
without bureaucratic role matrices, while decomposed tasks include routing,
coordination, and conditional dependencies.

---

## 1. Header contract

Every plan begins with this structured header:

```text
Status: READY | NEED-INPUT | BOUNDARY
Scope: current-item | spec-assessment | ticket-frontier | ticket-graph
Provider mode: tiered-multi-model | fixed-single-model
Task shape: single-pass | decomposed
Execution readiness: executable | needs-project-tickets | waiting-on-frontier | blocked-gate
Apply mode: plan-only | adapter-available-awaiting-approval | applied

Reason: <concise explanation of mode, sizing, and topology choices>
```

### Status semantics

- `READY`: Host has at least one usable executable model and a safe execution path
  is defined (including single-model serial execution).
- `NEED-INPUT`: Missing information that fundamentally changes execution scope,
  model spend, security boundaries, or task constraints.
- `BOUNDARY`: Host cannot safely provide an execution path (e.g. no usable current
  model, or a hard requirement cannot be fulfilled by the host runtime).

### Execution readiness semantics

- `executable`: The plan is ready for immediate implementation.
- `needs-project-tickets`: A decomposed task requires formal tickets before execution
  can be scheduled; hands off to `project-tickets`.
- `waiting-on-frontier`: Tickets exist but current unblocked frontier is blocked by
  external gates or dependencies.
- `blocked-gate`: An isolated gate is blocked; unblocked work may still be executable.

---

## 2. Core plan sections

Every plan includes the following standard sections:

```markdown
## Host summary
- Current model: <model id and status>
- Selectable models / tiers: <model ids with user-confirmed tiers, or "fixed single model">
- Reasoning control: <available levels and scopes, or "unavailable">
- Context & execution: <threads, subagents, parallelism, concurrency cap>
- Adapter: <adapter id or "none (plan-only)">

## Task assessment
- Task shape: single-pass | decomposed
- Assessment rationale: <semantic justification; never word count>
- Work-item difficulty: routine | moderate | demanding | critical

## Execution config
<Adaptive body: see Single-pass layout vs Decomposed layout below>

## Review strategy
- Review type: Controller Review | Self-check | Independent Review
- Review model & effort: <assigned tier, effort, and context>
- Review handoff: <review-loop / project-review handoff instruction>

## Limitations / unknowns
- <Known constraints, unverified capabilities, or adapter limitations>
```

---

## 3. Single-pass layout (Adaptive)

For `Task shape: single-pass`, output a streamlined phase table. Do not force an
ownership matrix, execution waves, or separate Explorer/Merger roles:
- **Single-model (Case A):** Direct execution in current session using the single model with resolved effort policy.
- **Multi-model (Case C):** Uses the model and resolved effort mapped from the task difficulty tier in the user profile.

```markdown
## Execution config

| Phase | Model / tier | Effort | Context | Purpose |
|---|---|---|---|---|
| Implementation | <model id or tier> | <effort> | current-session | Primary implementation |
| (Optional helper) | <model id or tier> | <effort> | subagent / thread | Focused research / test |
```

---

## 4. Decomposed layout (Adaptive)

For `Task shape: decomposed` with existing tickets, include ticket-level work-item
routing and coordination:
- **Single-model (Case B):** Controller in main session delegates each ticket to a fresh worker context (thread/subagent) using the same model with resolved effort. No synthetic tier names.
- **Multi-model (Case D):** Controller coordinates workers launched with each ticket's designated tier model and resolved effort.

```markdown
## Execution config

### Work-item routing

| Ticket | Difficulty | Model / tier | Effort | Context | Dependencies | Review |
|---|---|---|---|---|---|---|
| 01-slug | routine | <model / tier> | low | thread A | None | Controller |
| 02-slug | demanding | <model / tier> | high | thread B | 01-slug | Independent |

### Coordination

- Controller: <assigned model / tier, effort, and context>
- Concurrency cap: <number of concurrent threads, or 1 for serial>
- Frontier: <currently unblocked ready tickets>
- Integration: <how worker outputs are integrated and reviewed>
```

### Conditional sections for decomposed tasks

- **Ownership matrix:** Include ONLY if multiple workers touch shared directories
  or when exact file boundaries prevent concurrency merge conflicts.
- **Execution waves:** Include ONLY when multi-wave dependency scheduling is required
  to observe concurrency caps across ready tickets.

---

## 5. Review semantics

1. **Controller Review:** Controller reviews outputs from delegated workers before
   merging. Appropriate for multi-ticket coordination.
2. **Self-check:** Single executor verifies its own diff against test suites and specs.
   Must be labeled `Self-check`, never misrepresented as independent review.
3. **Independent Review:** Executed in a fresh, distinct session/thread with read-only
   assignment, ideally using an equal or higher model tier and higher effort.

Formal code convergence belongs to `review-loop`; final acceptance belongs to
`project-review`. `agent-config` configures review context and models, not rubrics.
