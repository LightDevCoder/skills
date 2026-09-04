# Companion MCP contract

This document specifies the companion MCP tool contract for `agent-config`.
The companion MCP provides host inspection, profile persistence, configuration preview,
and host-native application.

---

## 1. Protocol versioning

Both the companion MCP server and the `agent-config` Skill share a versioned interface:

- `protocol_version: 1`: Current tool interface version.
- `profile_version: 1`: User-confirmed profile schema version.
- `adapter_id`: Identifier of the host adapter (e.g. `generic`, host-specific adapter).
- `host_id`: Opaque identifier of the current execution host environment.

The Skill depends only on the public tool contract, never on companion internal file layout.

---

## 2. Tool protocol (8 tools)

The companion MCP server provides exactly eight focused tools:

### `get_setup_status`
Queries whether the current host environment has a valid user-confirmed profile.
- **Parameters:**
  - `workspace` (string, optional): Path to project workspace. Defaults to active directory.
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
    "stale_reasons": []
  }
  ```

### `inspect_host`
Queries host runtime for active model, available models, supported effort values, and execution capabilities.
- **Parameters:** None.
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
- **Returns:** User-confirmed profile object matching `profile-schema.md`, or `null` if unconfigured.

### `save_profile`
Persists a user-confirmed profile after rigorous validation.
- **Parameters:**
  - `profile` (object, required): Full profile object matching `profile-schema.md`.
- **Validation requirements:**
  - Validates profile schema (`profile_version: 1`).
  - Verifies configured model IDs exist in host `available_models`.
  - Verifies effort policies or explicit values are supported by host.
  - Verifies host identity matches current host.
- **Behavior:** Atomic write. Rejects malformed or mismatched profiles without partial writes.

### `preview_configuration`
Generates a deterministic change preview and diff before mutating any host configuration.
- **Parameters:**
  - `intent` (object, required): Execution plan intent containing target tiers, resolved effort values, and ticket assignments.
- **Returns:**
  ```json
  {
    "preview_id": "prev-8f3e2b1c",
    "preview_hash": "sha256-...",
    "diff": "--- current\n+++ proposed\n...",
    "changes": [
      { "target": "execution-config", "action": "update", "description": "Set worker tier to standard" }
    ],
    "expires_at": "2026-09-04T12:15:00Z"
  }
  ```

### `apply_configuration`
Applies a previously generated and user-approved preview.
- **Parameters:**
  - `preview_id` (string, required): Active, unexpired preview identifier.
- **Behavior:**
  - Validates `preview_id` exists and has not expired.
  - Verifies host target configuration has not drifted since preview creation.
  - If drift is detected, refuses application and requires fresh preview.
  - Mutates host-native configuration files atomically.

### `validate_configuration`
Validates that the host configuration on disk or in runtime reflects expected settings.
- **Parameters:**
  - `preview_id` (string, optional): Preview identifier to validate against.
- **Behavior:**
  - Inspects real runtime or file system state.
  - Compares expected vs actual configuration.
  - Never assumes write success without reading back post-apply state.
- **Returns:** `{ "valid": true, "mismatches": [] }`

### `reset_profile`
Clears persisted profile for the given host and workspace scope.
- **Parameters:**
  - `scope` (string, optional): `"project"` (default) or `"global"`.
  - `workspace` (string, optional): Target workspace path.
- **Returns:** `{ "reset": true, "host_id": "current-host", "scope": "project" }`

---

## 3. Preview-apply lifecycle

Host configuration mutations must strictly follow a two-phase gated lifecycle:

```text
1. inspect_host / get_profile
        ↓
2. preview_configuration (intent)
        ↓
   Returns preview_id, hash, diff
        ↓
3. Explicit user inspection & confirmation
        ↓
4. apply_configuration (preview_id)
        ↓
5. validate_configuration
```

- **Blind apply forbidden:** An agent must never call `apply_configuration` without first generating a preview and receiving affirmative user approval.
- **Expiration & drift check:** Previews expire after a bounded duration (typically 10-15 minutes). If target files or environment change between preview and apply, apply is aborted.
- **Post-apply validation:** Every apply step must be followed by `validate_configuration` to ensure the host runtime accurately reflects the intended configuration.

---

## 4. Non-blocking companion-absent fallback

When `agent-config` is invoked in an environment where companion MCP tools are not registered or reachable:

1. **No silent installation:** The Skill must never run automatic shell commands (e.g. `npm install`, background daemons, or host configuration mutations) without user knowledge.
2. **User notification:** Inform the user cleanly:
   ```text
   Agent Config companion MCP is not detected.
   Options:
     A. Set up / register companion MCP for persistent host configuration.
     B. Continue with session-only manual configuration (plan-only mode).
   ```
3. **Session-only manual mode:**
   - If the user chooses to continue without MCP:
     - Prompt for manual confirmation: single model vs selectable models, and preferred effort policy.
     - Build an in-memory plan conforming to `plan-schema.md` with `Apply mode: plan-only`.
     - Never pretend persistence succeeded; clearly note `Status: READY`, `Apply mode: plan-only (companion absent)`.
4. **Zero downstream disruption:**
   - Absence of the companion MCP never blocks downstream skills (`implement`, `ask-light`, `project-tickets`, `review-loop`).
   - Portable Skill reasoning remains 100% functional even without companion MCP runtime.
