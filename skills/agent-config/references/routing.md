# Execution routing

This reference defines execution topology selection, the four peer execution modes,
and work-item routing across single-model and multi-model host environments.

---

## 1. The 2×2 peer execution matrix

`agent-config` organizes all work into four peer modes based on **Task shape** and **Model mode**:

| | Task shape: Single-pass | Task shape: Decomposed |
|---|---|---|
| **Model mode: Single-model** | **Case A**<br>Direct execution, single model, resolved effort, no fake roles | **Case B (P0)**<br>Controller main session + fresh worker contexts, same model, actual effort |
| **Model mode: Multi-model** | **Case C**<br>Task difficulty mapped to user profile tier, minimal topology | **Case D (P0)**<br>Ticket difficulty mapped to profile tiers, real effort resolved, Controller integration |

### Peer invariant
Single-model mode is an equal, first-class execution topology—never a degraded fallback.
Both Case B and Case D are high-frequency P0 paths.

---

## 2. Four peer execution modes

### Case A: Single-model + Single-pass
- **Trigger:** Single cohesive task in a single-model environment.
- **Topology:** Main session direct execution.
- **Model & effort:** Current model with execution effort resolved from profile policy.
- **Execution rules:**
  - Execute directly in the active session.
  - Never invent fake agent roles (no synthetic explorer, implementer, or reviewer personas).
  - Optional helper context used only if isolated read-only research or test execution is beneficial.
  - Self-check verification before completion.

### Case B: Single-model + Decomposed (P0)
- **Trigger:** Multi-ticket or partitioned workload in a single-model environment.
- **Prerequisite:** Formal ticket graph already exists. If not, emit `readiness: NEED_PROJECT_TICKETS`, `handoff: "project-tickets"`, and `execution_config: null`.
- **Topology:**
  - **Main session:** Acts as Controller (orchestrates, reviews diffs, manages git state).
  - **Worker contexts:** Each ticket is executed in a fresh context (thread or subagent) to maintain context freshness and prevent token pollution.
- **Model & effort:** All workers and Controller run the same configured model, using the profile's effort policy resolved to host values.
- **Execution rules:**
  - If host lacks thread/subagent capabilities, Controller executes tickets serially in the main session.
  - Parallelism is throttled to the host `concurrency_cap`.
  - Controller reviews worker deliverables before merging.
  - Strictly no fake model tiers (do not invent "routine model" or "high model").

### Case C: Multi-model + Single-pass
- **Trigger:** Single cohesive task in a multi-model environment.
- **Topology:** Streamlined execution without superfluous agent bureaucracy.
- **Model & effort:**
  - Map task difficulty (`routine`, `moderate`, `demanding`, `critical`) to user profile tier (`routine`, `standard`, `high`).
  - Resolve effort policy to concrete host value.
- **Execution rules:**
  - Run implementation in the active context using the mapped tier.
  - Review step uses the profile's `review` tier in a fresh context if independent review is required.
  - Do not create subagents merely because multiple models are available.

### Case D: Multi-model + Decomposed (P0)
- **Trigger:** Multi-ticket workload in a multi-model environment.
- **Prerequisite:** Formal ticket graph exists.
- **Topology:**
  - **Controller:** Runs in main session on user-confirmed `review` or `high` tier model.
  - **Workers:** Each ticket launched in a fresh context with the model and resolved effort matching the ticket's difficulty tier:
    - `routine` → `routine` tier model + resolved effort
    - `moderate` → `standard` tier model + resolved effort
    - `demanding` → `high` tier model + resolved effort
    - `critical` → `high` tier model + `highest-supported` effort
- **Execution rules:**
  - Inspect ticket graph, dependencies, and ready frontier.
  - Schedule unblocked ready tickets concurrently up to `concurrency_cap`.
  - Controller integrates results, verifies cross-cutting tests, and conducts Controller Review.
  - Critical tickets receive independent review in a fresh context with the `review` tier.

---

## 3. Topology selection logic

### Task shape determination
1. **Single-pass:**
   - Single cohesive concern or bounded module.
   - Entire implementation and test cycle easily fits into a single context window.
   - Verification surface is compact.
2. **Decomposed:**
   - Multiple distinct, independently verifiable changes.
   - Clear dependency ordering across components (e.g. schema → service → API → UI).
   - High risk of context degradation if attempted in a single context.
   - Formal tickets exist or are required for safe execution.

*Strict anti-wordcount rule:* Task shape is determined by structural complexity and risk, never by document length or word count.

### Context freshness and concurrency
- **Context freshness:** Decomposing work into fresh worker contexts isolates error states, prevents context saturation, and improves implementation quality.
- **Concurrency control:** Concurrent workers must operate on disjoint files or well-defined boundaries to avoid merge conflicts.
- **Host cap adherence:** Active concurrent workers must never exceed the host's evidenced `concurrency_cap`. If the cap is 1 or unknown, workers execute serially.

---

## 4. Routing output envelope (`AgentConfigResult`)

Topology and routing decisions are emitted within the canonical `AgentConfigResult` envelope:

- **Ready execution (Cases A, B, C, D):**
  - `readiness`: `"READY"`
  - `mode`: `"persisted"` | `"session-local"` | `"plan-only"`
  - `setup_state`: `{ companion: "ready" | "missing" | "stale", profile: "persisted" | "session-local" }`
  - `handoff`: `"implement"`
  - `execution_config`: Non-null structured `ExecutionConfig` matching `execution-config.schema.json`.
- **Missing profile / setup required:**
  - `readiness`: `"NEED_INPUT"`
  - `setup_state`: `{ companion: "ready" | "missing" | "stale", profile: "missing" }`
  - `handoff`: `"setup"`
  - `execution_config`: `null`
- **Decomposed task without tickets:**
  - `readiness`: `"NEED_PROJECT_TICKETS"`
  - `handoff`: `"project-tickets"`
  - `execution_config`: `null`
- **Blocked or unsupported constraints:**
  - `readiness`: `"BLOCKED"` | `"UNSUPPORTED"`
  - `handoff`: `null`
  - `execution_config`: `null`

