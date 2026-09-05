# Execution plan schema

`agent-config` outputs an adaptive, Markdown-formatted execution plan and returns an authoritative `AgentConfigResult` structured envelope.
Formatting scales with task shape: single-pass tasks emit a concise configuration
without bureaucratic role matrices, while decomposed tasks include routing,
coordination, and conditional dependencies.

---

## 0. Two-layer result architecture (`AgentConfigResult`)

`agent-config` returns a canonical result envelope:

```typescript
interface AgentConfigResult {
  readiness: "READY" | "NEED_INPUT" | "NEED_PROJECT_TICKETS" | "BLOCKED" | "UNSUPPORTED";
  mode: "persisted" | "session-local" | "plan-only";
  setup_state: {
    companion: "ready" | "missing" | "stale";
    profile: "persisted" | "session-local" | "missing";
  };
  handoff: "project-tickets" | "setup" | "implement" | null;
  execution_config: ExecutionConfig | null;
  reason?: string;
  diagnostics?: string[];
}
```

### Readiness and execution_config invariant
- `readiness` is the single authoritative execution-readiness field (`READY | NEED_INPUT | NEED_PROJECT_TICKETS | BLOCKED | UNSUPPORTED`). Redundant status is removed.
- `execution_config` exists **only** when `readiness === "READY"`. For any non-ready state, `execution_config` is strictly `null`.
- `handoff` explicitly directs caller orchestration:
  - `"implement"` when `readiness === "READY"`.
  - `"setup"` when `readiness === "NEED_INPUT"`.
  - `"project-tickets"` when `readiness === "NEED_PROJECT_TICKETS"`.
  - `null` when `readiness === "BLOCKED"` or `"UNSUPPORTED"`.

---

## 1. Header contract

Every plan begins with this structured header:

```text
Readiness: READY | NEED_INPUT | NEED_PROJECT_TICKETS | BLOCKED | UNSUPPORTED
Scope: current-item | spec-assessment | ticket-frontier | ticket-graph
Provider mode: tiered-multi-model | fixed-single-model
Task shape: single-pass | decomposed
Execution status: executable | waiting-on-dependencies | blocked-gate
Apply mode: plan-only | adapter-available-awaiting-approval | applied

Reason: <concise explanation of mode, sizing, and topology choices>
```

### Readiness semantics

`Readiness` in the header mirrors the authoritative `AgentConfigResult.readiness`:

- `READY`: Host has at least one usable executable model, profile authorization is satisfied, and a safe execution path is defined. `execution_config` is present.
- `NEED_INPUT`: Missing profile, unconfirmed tier mapping, or ambiguous configuration. Hands off to `setup`.
- `NEED_PROJECT_TICKETS`: Decomposed task requires formal ticket breakdown before execution can be scheduled. Hands off to `project-tickets`.
- `BLOCKED`: Required capability or model unavailable; execution cannot safely proceed.
- `UNSUPPORTED`: Host environment or requested topology cannot be satisfied.

### Execution status semantics (Internal Execution Topology)

Within an executable plan, `Execution status` indicates the dispatch condition of the immediate work items:

- `executable`: The plan is ready for immediate implementation.
- `waiting-on-dependencies`: Work items exist but unblocked frontier depends on in-progress predecessors.
- `blocked-gate`: An isolated gate is blocked; other unblocked work may still be executable.

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
