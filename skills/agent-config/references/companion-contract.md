# Companion MCP contract

This document specifies the companion MCP tool contract for `agent-config`.
The companion MCP provides host inspection, profile persistence, configuration preview,
and host-native application. The companion MCP runtime is maintained in the dedicated
repository `LightDevCoder/agent-config`.

---

## 1. Protocol versioning and health semantics

Both the companion MCP server and the `agent-config` Skill share a versioned interface:

- `protocol_version: 1`: Current tool interface version (Agent Config Companion contract version).
- `profile_version: 1`: User-confirmed profile schema version.
- `adapter_id`: Identifier of the host adapter (e.g. `generic`, host-specific adapter).
- `host_id`: Opaque identifier of the current execution host environment.

### Companion health semantics
Companion `healthy` / `ready` status strictly requires all of the following:
1. **Protocol compatibility:** Both the underlying MCP transport protocol must be compatible (supported by the MCP SDK runtime), and the Agent Config Companion contract version must match (`protocol_version === 1`).
2. **Tool contract completeness & compatibility:** All eight canonical MCP tools (`get_setup_status`, `inspect_host`, `get_profile`, `save_profile`, `preview_configuration`, `apply_configuration`, `validate_configuration`, `reset_profile`) are registered and exposed with parameter and return schemas matching canonical contracts (`CANONICAL_TOOL_CONTRACTS`).
3. **Reachability & responsiveness:** Process is reachable and responsive to status/ping handshakes without timing out or throwing connection errors.

If any canonical tool is missing, if input/output schemas mismatch canonical contracts, or if either MCP transport or Agent Config contract protocol version is incompatible, the companion is classified as `stale` or `unsupported`, never `ready` or `healthy`.

The Skill depends only on the public tool contract, never on companion internal file layout.

---

## 2. Tool protocol (8 tools)

The companion MCP server provides exactly eight focused tools:

### `get_setup_status`
Queries whether the current host environment has a valid user-confirmed profile.
- **Parameters:**
  - `scope` (string, optional): `"project"` (default) or `"global"`.
  - `workspace` (string, optional): Path to project workspace. Defaults to active directory.
  - `host_id` (string, optional): Host identifier.
- **Returns:**
  ```json
  {
    "configured": true,
    "protocol_version": 1,
    "profile_version": 1,
    "host_id": "current-host",
    "adapter_id": "host-adapter",
    "scope": "project",
    "stale": false,
    "stale_reasons": [],
    "companion_registered": true,
    "companion_status": "active"
  }
  ```

### `inspect_host`
Queries host runtime for active model, available models, supported effort values, and execution capabilities.
- **Parameters:**
  - `workspace` (string, optional): Path to project workspace.
  - `host_id` (string, optional): Host identifier.
- **Returns:**
  ```json
  {
    "host_id": "current-host",
    "adapter_id": "host-adapter",
    "workspace": "/path/to/workspace",
    "available_models": [
      { "id": "model-alpha" },
      { "id": "model-beta" }
    ],
    "supported_effort_values": ["low", "medium", "high"],
    "capabilities": {
      "model_selection": true,
      "model_selection_scopes": ["current-session", "new-session", "per-agent"],
      "subagents": true,
      "session_threads": true,
      "parallelism": true,
      "concurrency_cap": 4,
      "configuration_mutation": true
    }
  }
  ```
- **Prohibition:** Must never return guessed intelligence rankings or ordering. Records availability only.

### `get_profile`
Reads the persisted user-confirmed profile for the current host and workspace.
- **Parameters:**
  - `scope` (string, optional): `"project"` (default) or `"global"`.
  - `workspace` (string, optional): Target workspace path.
  - `host_id` (string, optional): Host identifier.
- **Returns:** User-confirmed profile object matching `profile-schema.md`, or `null` if unconfigured.

### `save_profile`
Persists a user-confirmed profile after rigorous validation.
- **Parameters:**
  - `profile` (object, required): Full profile object matching `profile-schema.md`.
  - `workspace` (string, optional): Optional workspace path override.
- **Validation requirements:**
  - Validates profile schema (`profile_version: 1`).
  - Verifies configured model IDs exist in host `available_models`.
  - Verifies effort policies or explicit values are supported by host.
  - Verifies host identity matches current host.
- **Behavior:** Atomic write. Rejects malformed or mismatched profiles without partial writes.

### `preview_configuration`
Generates a deterministic change preview and diff before mutating any host configuration, returning a canonical `FrozenMutationPreview`.
- **Parameters:**
  - `config` (object, required): Canonical execution configuration object conforming to `execution-config.schema.json`.
  - `workspace` (string, optional): Target workspace path.
  - `host_id` (string, optional): Host identifier.
- **Returns (`FrozenMutationPreview`):**
  ```json
  {
    "preview_id": "prev-8f3e2b1c",
    "preview_hash": "sha256-...",
    "adapter_id": "codex",
    "host_identity": "codex",
    "scope": "project",
    "target": "execution-config",
    "baseline_hash": "sha256-...",
    "mutation": {
      "diff": "--- current\n+++ proposed\n...",
      "patch": "...",
      "files": [{ "path": "...", "content": "..." }]
    },
    "created_at": "2026-09-05T00:00:00Z",
    "expires_at": "2026-09-05T00:15:00Z"
  }
  ```
- **Immutability Contract:** Target paths, mutation payload, and scope are frozen upon generation. Apply cannot alter targets, widen scope, or re-derive diffs.

### `apply_configuration`
Applies a previously generated and user-approved preview.
- **Parameters:**
  - `preview_id` (string, required): Active, unexpired preview identifier.
  - `workspace` (string, optional): Target workspace path.
- **Behavior:**
  - Validates `preview_id` exists, has not expired, and has not already been applied.
  - Verifies target files on disk match the frozen `baseline_hash`. If drift is detected, aborts immediately (`STALE_PREVIEW` fail-closed).
  - Applies the exact frozen mutation without re-derivation or scope expansion.
- **Returns:**
  ```json
  {
    "success": true,
    "preview_id": "prev-8f3e2b1c",
    "applied_targets": ["execution-config"],
    "target": "execution-config",
    "baseline_hash": "sha256-...",
    "message": "Configuration successfully applied."
  }
  ```

### `validate_configuration`
Validates that the host configuration on disk or in runtime reflects expected settings.
- **Parameters:**
  - `expected_config` (object, optional): Expected execution configuration to validate against.
  - `preview_id` (string, optional): Preview identifier to validate against.
  - `workspace` (string, optional): Target workspace path.
  - `host_id` (string, optional): Host identifier.
- **Behavior:**
  - Inspects real runtime or file system state.
  - Compares expected vs actual configuration.
  - Never assumes write success without reading back post-apply state.
- **Returns:** `{ "valid": true, "workspace": "/path/to/workspace", "message": "Host configuration matches expected state." }`

### `reset_profile`
Clears persisted profile for the given host and workspace scope.
- **Parameters:**
  - `scope` (string, optional): `"project"` (default) or `"global"`.
  - `workspace` (string, optional): Target workspace path.
  - `host_id` (string, optional): Host identifier.
- **Returns:** `{ "success": true, "cleared": true, "reset": true, "host_id": "current-host", "scope": "project" }`

---

## 3. Preview-apply lifecycle

Host configuration mutations must strictly follow a two-phase gated lifecycle:

```text
1. inspect_host / get_profile
        ↓
2. preview_configuration (config)
        ↓
   Returns FrozenMutationPreview (preview_id, preview_hash, baseline_hash, diff, target, scope)
        ↓
3. Explicit user inspection & confirmation
        ↓
4. apply_configuration (preview_id)
        ↓
   Verifies unexpired, not-applied, baseline match; executes frozen mutation
        ↓
5. validate_configuration
        ↓
   Reads back real runtime/disk state to confirm match
```

- **Blind apply forbidden:** An agent must never call `apply_configuration` without first generating a preview and receiving affirmative user approval.
- **Target and scope immutability:** The preview freezes the mutation targets and scope (`project` or `global`). `apply_configuration` cannot re-derive the target list, broaden scope, or switch files.
- **Expiration & drift check (Fail-Closed):** Previews expire after a bounded duration (typically 10-15 minutes). If target files or baseline hash change between preview and apply, apply is aborted fail-closed (`STALE_PREVIEW`).
- **Post-apply validation:** Every apply step must be followed by `validate_configuration` to ensure the host runtime accurately reflects the intended configuration.

---

## 4. Non-blocking companion-absent operation / fallback

When `agent-config` is invoked in an environment where companion MCP tools are not registered or reachable:

1. **Real reachability verification:** Tool availability must be checked via real reachability (live tool handshake / ping), never inferred from dormant configuration files.
2. **No silent installation:** The Skill must never run automatic shell commands (e.g. `npm install`, background daemons, or host configuration mutations) without user knowledge.
3. **User notification:** Inform the user cleanly:
   ```text
   Agent Config companion MCP is not detected.
   Options:
     A. Run agent-config setup to set up / register companion MCP.
     B. Continue session-local / plan-only.
   ```
4. **Session-only manual mode:**
   - If the user chooses to continue without MCP:
     - Prompt for manual confirmation: single model vs selectable models, and preferred effort policy.
     - Build an in-memory plan conforming to `plan-schema.md` with `Apply mode: plan-only`.
     - Never pretend persistence succeeded; clearly note `readiness: READY`, `Apply mode: plan-only (companion absent)`.
5. **Zero downstream disruption:**
   - Absence of the companion MCP never blocks downstream skills (`implement`, `ask-light`, `project-tickets`, `review-loop`).
   - Non-blocking companion-absent fallback ensures portable Skill reasoning remains 100% functional even without companion MCP runtime.

---

## 5. Result envelope integration (`AgentConfigResult`)

Companion status and profile readiness feed into the canonical `AgentConfigResult` envelope:
- `readiness`: `READY | NEED_INPUT | NEED_PROJECT_TICKETS | BLOCKED | UNSUPPORTED` (authoritative).
- `mode`: `persisted | session-local | plan-only` (derived from profile persistence and companion state).
- `setup_state`:
  - `companion`: `ready | missing | stale` (evaluated per health semantics above).
  - `profile`: `persisted | session-local | missing`.
- `handoff`: `"project-tickets" | "setup" | "implement" | null`.
- `execution_config`: `ExecutionConfig | null` (strictly non-null when `readiness === "READY"`; strictly `null` otherwise).

