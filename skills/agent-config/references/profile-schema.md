# Profile schema

A profile stores user-confirmed execution settings for a specific host and workspace.
It represents the persistent output of the setup workflow and the single source of truth
for model assignments and effort policies.

---

## 1. Governance invariants

1. **Strictly user-confirmed:** Profiles are created or updated only through explicit user
   decisions during setup. Models and tiers are never guessed, inferred from marketing names,
   or algorithmically ordered by the Skill or MCP.
2. **Host- and workspace-scoped:** Profiles are tied to a specific `host_id` and `workspace` path.
   Settings from one host are never silently applied to another host.
3. **No automatic model ranking:** Profiles record user-assigned model bindings to abstract tiers,
   not an automated capability rank.
4. **No silent substitution:** If a configured model becomes unavailable, the profile is marked
   `stale`. The engine never silently swaps models.

---

## 2. Profile structure

```yaml
profile_version: 1

host:
  id: "opaque-host-id"
  adapter: "host-adapter-id"

scope:
  type: "project"               # "project" | "global"
  workspace: "/path/to/project"

model_mode: "single"            # "single" | "multi"

models:
  available:                    # Snapshot of models verified during setup
    - "model-alpha"
    - "model-beta"

# Configured when model_mode == "single"
single_model:
  model: "model-alpha"
  execution_effort:
    policy: "highest-supported" # Abstract policy or specific host enum
  review_effort:
    policy: "highest-supported"

# Configured when model_mode == "multi"
tiers:
  routine:
    model: "model-alpha"
    effort: "medium"
  standard:
    model: "model-alpha"
    effort: "high"
  high:
    model: "model-beta"
    effort: "highest-supported"
  review:
    model: "model-beta"
    effort: "highest-supported"

capabilities:
  subagents: true
  session_threads: true
  parallelism: true
  concurrency_cap: 4
```

---

## 3. Field definitions

### Identity & scope
- `profile_version`: Positive integer (currently `1`).
- `host.id`: Identifier of host environment where profile was configured.
- `host.adapter`: Identifier of adapter handling translation for this host.
- `scope.type`: `"project"` (scoped to workspace directory) or `"global"` (user-level default for host).
- `scope.workspace`: Canonical path to project workspace when `scope.type == "project"`.

### Mode & model assignments
- `model_mode`:
  - `"single"`: All tasks and tickets execute with one model. Tiers are not used.
  - `"multi"`: Work-item difficulties map to user-assigned tiers. Multiple tiers may map to the same model.
- `single_model` (required if `model_mode == "single"`):
  - `model`: Model identifier to use for all execution.
  - `execution_effort.policy`: Effort policy for implementation (e.g. `"highest-supported"`, `"default"`, or explicit value).
  - `review_effort.policy`: Effort policy for review passes.
- `tiers` (required if `model_mode == "multi"`):
  - `routine`: Work with clear templates, low ambiguity, and minimal verification.
  - `standard`: Normal feature work, bug fixes, standard components.
  - `high`: Deep reasoning, cross-module architecture, high ambiguity.
  - `review`: Independent verification, integration review, security check.
  - Each tier specifies:
    - `model`: Explicit model ID chosen by user from host availability.
    - `effort`: Abstract effort policy (`"highest-supported"`, `"default"`) or explicit host enum.

### Host execution capabilities
- `capabilities.subagents`: True if host can launch isolated subagents.
- `capabilities.session_threads`: True if host supports distinct fresh session contexts.
- `capabilities.parallelism`: True if host supports simultaneous concurrent workers.
- `capabilities.concurrency_cap`: Maximum concurrent execution contexts (integer ≥ 1).

---

## 4. Effort policies

Effort in a profile can be specified as an abstract policy or a concrete host value:

- `highest-supported`: Resolves at runtime to the highest discrete effort level supported by the host (e.g. `"high"` on a `["low", "medium", "high"]` host).
- `default`: Uses the host runtime's default effort level.
- `<concrete-host-value>`: An explicit enum value validated against host capabilities (e.g. `"medium"`).

---

## 5. Profile stale conditions

A profile is flagged as `stale: true` when runtime facts conflict with saved configuration:

1. **Configured model missing:** A model mapped to `single_model` or any active tier in `tiers` is no longer present in host `available_models`.
2. **Host identity mismatch:** Profile was created for a different `host_id`.
3. **Adapter incompatibility:** Adapter contract or major version has changed.
4. **Capability regression:** Host no longer supports a capability required by the profile mode (e.g. `concurrency_cap` dropped to 0).

**Elapsed time is not a stale trigger:** A profile does not expire merely because N days have elapsed. As long as host capabilities and model availability remain consistent, the profile remains valid. When stale, the Skill directs into the Setup Gate for repair.
