# Provider adapter contract

The provider adapter is an optional, provider-specific bridge between the Agent
Host runtime and the provider-neutral `agent-config` planning engine.

The core `agent-config` skill maintains zero vendor coupling and does not hardcode
vendor model identifiers, configuration file formats, or proprietary CLI flags.

## Responsibilities

1. **Host capability inspection:** Query the runtime host or verified manifest
   to observe active models, selectable alternatives, session/thread capabilities,
   subagents, parallelism, and concurrency limits with timestamps.
2. **Metadata normalization:** Map provider-specific model variants to neutral
   relative `routing_rank` values (higher integer = higher reasoning capability)
   and normalize reasoning effort settings into ordered levels and scopes.
3. **Optional project configuration application:** When supported, receive a
   declarative project-level execution configuration request and apply it to
   project files only after explicit user confirmation.

## Observation contract

An adapter outputs or populates the structured host evidence conforming to
`host-evidence-schema.md` (v2):

- `provider.identity`: string identifying the underlying provider
- `adapter.identity` & `adapter.version`: adapter implementation info
- `observed_at`: ISO-8601 timestamp of host inspection
- `models.current`: executable model in active session
- `models.selectable`: list of selectable models with normalized `routing_rank`
- `capabilities`: normalized capabilities (model selection, subagents,
  parallelism, reasoning control, threads, worktrees, concurrency cap)
- `adapter.project_config_support`: `available | unavailable | unknown`

## Apply request contract

When the host adapter supports applying project-level agent configurations,
`agent-config` may emit an apply request:

```yaml
apply_request:
  project_root: "/path/to/project"
  controller:
    model: "highest-ranked-model-id"
    effort: "high"
  workers:
    routine:
      model: "rank-1-model-id"
      effort: "low"
    moderate:
      model: "rank-2-model-id"
      effort: "medium"
    demanding:
      model: "rank-3-model-id"
      effort: "high"
    critical:
      model: "rank-3-model-id"
      effort: "high"
  review:
    model: "rank-3-model-id"
    effort: "high"
```

## Governance and safety boundaries

- **Read-only by default:** Standard or implicit invocations of `agent-config`
  always produce plans in `Apply mode: plan-only`. The engine never invokes
  configuration mutations automatically.
- **Explicit user approval required:** Configuration mutation requires explicit,
  affirmative user approval before execution (`Apply mode: applied`). If the
  user declines, the plan remains valid for manual Controller execution.
- **Graceful adapter absence:** When no adapter exists, `agent-config` operates
  in `Apply mode: plan-only` and notes `Limitation: no project-config adapter available`.
  It never emits a `BOUNDARY` status due to absent adapter tooling.
- **Non-blocking adapter failure:** If an adapter fails to apply configuration,
  the failure is reported with specifics, the plan remains valid, and execution
  proceeds manually without blocking work items.
- **No invented framework:** This contract defines semantic boundaries and fallback
  rules. It does not introduce a runtime plugin daemon or heavy framework into
  the skills repository.
