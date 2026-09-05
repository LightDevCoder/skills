---
name: agent-config
description: Map the current Agent Host's evidenced capabilities and confirmed profile to a right-sized execution topology, model tier, and effort.
---

# Agent Config

`agent-config` maps verified Agent Host capabilities and user-confirmed profile tiers to a right-sized execution topology, model, and effort. It never guesses model intelligence, never mutates host config silently, and treats single-model as a first-class peer topology. It provides native support for primary coding-agent harnesses (Codex, Claude Code, Antigravity, DSH, OpenCode, ZCode, Cursor, Grok Build, Hermes) with safe generic/manual fallback for others. It has no required companion capability, no external Skill, and no external service requirements.

## When to use
- Before complex multi-agent or partitioned work where topology, model tier, or effort matters.
- Explicit setup intent (`agent-config setup`) to configure or reconfigure host models and tiers.
- When invoked or offered by `implement` or `ask-light`.

## Inputs
- Bounded task, SPEC, or ticket graph.
- Evidenced host capabilities and confirmed profile (via companion MCP or session input).

## Setup Gate
- **Explicit setup:** If invoked with setup intent (`agent-config setup`), run setup mode to prepare or repair the runtime environment and Profile (see [`references/setup.md`](references/setup.md)). Setup never plans execution for the current task.
- **Normal invocation:** `agent-config` is the only mode that plans execution topology and routing for current work. Check setup status via companion `get_setup_status`. Companion health requires `protocol_version === 1`, all 8 canonical tools present with matching schemas, and reachable responsive process; missing tools or schema mismatch is classified as `stale` or `unsupported`, not healthy. If companion is missing/stale, offer setup or continue plan-only. If Profile is missing or stale, offer setup or continue session-local where safely possible. Never silently enter setup, auto-install MCP tools, or mutate host files.

## Output Contract: AgentConfigResult
`agent-config` yields a canonical `AgentConfigResult` envelope:
- `readiness`: `READY | NEED_INPUT | NEED_PROJECT_TICKETS | BLOCKED | UNSUPPORTED` (authoritative execution-readiness; redundant status removed).
- `mode`: `persisted | session-local | plan-only`
- `setup_state`: `companion` (`ready | missing | stale`), `profile` (`persisted | session-local | missing`).
- `handoff`: `"project-tickets" | "setup" | "implement" | null`
- `execution_config`: `ExecutionConfig | null` (strictly present when `readiness === "READY"`; strictly `null` for all non-ready states).

## Core flow
1. **Setup check:** Verify confirmed profile via companion MCP or session input (never guess single-model without profile). Companion health requires `protocol_version === 1`, all 8 canonical tools, and responsiveness.
2. **Inspect host:** Read active models, supported effort values, and concurrency limits.
3. **Determine task shape:** Classify as `single-pass` or `decomposed` (never by word count).
4. **Decomposition gate:** If decomposed and formal tickets do not exist, emit `readiness: NEED_PROJECT_TICKETS`, `handoff: "project-tickets"`, `execution_config: null`, and hand off to `project-tickets`.
5. **Difficulty & tier:** For multi-model, map work difficulty (`routine`..`critical`) to user-confirmed profile tiers (`routine`, `standard`, `high`, `review`).
6. **Resolve effort:** Resolve abstract policies (e.g. `highest-supported`) strictly to verified host-supported strings (e.g. `high`), never emitting unverified literal `max`.
7. **Select execution mode:**
   - **Case A (Fixed Single-model + Single-pass):** Direct execution in main session, single model, resolved effort, no fake roles.
   - **Case B (Fixed Single-model + Decomposed, P0):** Controller main session coordinates fresh worker contexts, same model, actual effort.
   - **Case C (Tiered Multi-model + Single-pass):** User-configured tier mapped from task difficulty, minimal topology.
   - **Case D (Tiered Multi-model + Decomposed, P0):** Ticket difficulty mapped to user profile tiers, resolved effort, Controller integration.
8. **Emit plan & apply:** Output plan conforming to [`references/plan-schema.md`](references/plan-schema.md) and `AgentConfigResult`. Host config mutations require preview approval (`preview_configuration` → user approval → `apply_configuration` → `validate_configuration`).

## Invariants
- **No intelligence guessing:** Never infer model strength from names or metadata; model tiers are strictly user-confirmed.
- **Single-model is first-class:** Single-model is a peer topology, not a degraded fallback. Case B and Case D are both P0 paths.
- **No silent mutation:** No automatic package installations, background daemons, or host file edits without explicit consent.
- **Anti-wordcount rule:** Semantic complexity and dependencies determine task shape, never prose length.

## Handoff
- If tickets needed: emit `readiness: NEED_PROJECT_TICKETS` (`handoff: "project-tickets"`) and hand off to `project-tickets`.
- When ready: Controller proceeds to `implement` (`handoff: "implement"`). Code review converges via `review-loop`; final acceptance belongs to `project-review`.

## References
- [`references/setup.md`](references/setup.md) — Setup questionnaire and tier binding flow
- [`references/routing.md`](references/routing.md) — 4 peer execution modes and topology selection
- [`references/task-assessment.md`](references/task-assessment.md) — Task shape and difficulty criteria
- [`references/companion-contract.md`](references/companion-contract.md) — Companion MCP tool protocol (8 tools)
- [`references/harness-support.md`](references/harness-support.md) — Primary coding-agent harnesses (9 native adapters) and generic fallback
- [`references/profile-schema.md`](references/profile-schema.md) — Host-scoped profile schema
- [`references/plan-schema.md`](references/plan-schema.md) — Execution plan format and review semantics
- [`references/host-evidence-schema.md`](references/host-evidence-schema.md) — Host evidence schema v2
- [`references/provider-adapter-contract.md`](references/provider-adapter-contract.md) — Adapter boundaries and preview-apply
