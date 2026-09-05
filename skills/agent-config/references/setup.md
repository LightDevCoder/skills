# Setup questionnaire

This reference defines the questionnaire flow for configuring host-scoped execution profiles.
`agent-config setup` prepares or repairs the runtime environment and Profile. It does not plan execution for the current task.

Setup runs either via explicit invocation (`agent-config setup`) or when the user explicitly chooses to enter setup after normal `agent-config` reports an unconfigured or stale environment via the Setup Gate. It is never silently entered.

---

## 1. Setup entry and host inspection

1. **Companion & Host discovery:**
   - Detect companion MCP availability with real reachability checks (tool ping / live handshake; never assume reachability from static configuration or file existence).
   - If companion is absent, ask user whether to install/register. If declined, stop setup (portable Skill remains usable in session-local / plan-only mode). Never auto-install.
   - Call companion tool `inspect_host`.
2. **Display environment context:**
   Present the detected environment concisely:
   ```text
   Host: <host_id> (<adapter_id>)
   Workspace: <workspace_path>
   Detected models: <list of model IDs>
   Supported effort values: <e.g. low, medium, high>
   ```
3. **Mode question:**
   Ask the user to select the execution model structure:
   ```text
   How does this environment expose execution models?
     A. Single model (one model used for all work; right-sized via effort and context freshness)
     B. Multiple selectable models (assign specific models to abstract execution tiers)
   ```

---

## 2. Single-model setup flow

When the user selects **Single model**:

1. **Model confirmation:**
   Confirm the active model identifier to use (e.g. `model-alpha`).
2. **Effort policies:**
   Present available host effort values and ask the user to choose:
   - **Execution effort policy:** e.g. `highest-supported`, `default`, or a specific host value.
   - **Review effort policy:** e.g. `highest-supported` or a specific host value.
3. **Topology capabilities:**
   Confirm host execution capabilities:
   - Concurrency cap (default to host inspection value, or prompt user if unknown).
   - Thread and subagent support.
4. **Summary & confirmation:**
   Present structured profile preview to user.
   Upon explicit user confirmation, call `save_profile`.
5. **Setup completion boundary:**
   Setup completes and ends. Do not automatically plan current tickets or route execution.

---

## 3. Multi-model setup flow

When the user selects **Multiple selectable models**:

1. **Display verified model inventory:**
   Show the list of models returned by `inspect_host`. Do not guess intelligence rankings.
2. **Tier binding questionnaire:**
   Prompt the user to assign an available model ID to each abstract tier:
   - **`routine`:** Low uncertainty, mechanical refactoring, config edits, boilerplate tests.
   - **`standard`:** Typical feature implementation, standard bug fixes, integration tests.
   - **`high`:** Complex architecture, concurrency, high ambiguity, critical paths.
   - **`review`:** Controller review, independent verification, cross-ticket integration.

   *Note:* Multiple tiers may be mapped to the same model (e.g. routine & standard map to `model-beta`, while high & review map to `model-gamma`).
3. **Tier effort policies:**
   Prompt the user to select the effort policy for each tier:
   - Example: `routine: medium`, `standard: high`, `high: highest-supported`, `review: highest-supported`.
4. **Topology capabilities:**
   Confirm concurrency cap and worker context capabilities.
5. **Summary & confirmation:**
   Present structured profile preview matching `profile-schema.md`.
   Upon explicit user confirmation, call `save_profile`.
6. **Setup completion boundary:**
   Setup completes and ends. Do not automatically plan current tickets or route execution.

---

## 4. Resolving effort policies

Effort policies separate user intent from provider-specific host enumerations:

### Policy vs resolved host value
- **User policy:** Recorded in profile (e.g. `highest-supported`, `default`, or explicit value).
- **Resolved value:** The concrete string emitted in execution plans and passed to host runtime.

### Resolution algorithm for `highest-supported`
Inspect the host's `supported_effort_values` list (ordered from lowest to highest):
- If host supports `["low", "medium", "high"]`:
  `highest-supported` resolves to `"high"`.
- If host supports `["high"]`:
  `highest-supported` resolves to `"high"`.
- If host supports `["low", "high", "max"]`:
  `highest-supported` resolves to `"max"`.
- If host supports `["standard", "deep"]`:
  `highest-supported` resolves to `"deep"`.

### Strict anti-literal-max rule
An execution plan must **never** output literal `"max"` unless the current host runtime
explicitly lists `"max"` in its verified `supported_effort_values`. If the host's highest
level is `"high"`, the resolved value is `"high"`.

---

## 5. Configuration mutation & preview semantics

When setup registers the companion MCP or mutates host configuration:

1. **FrozenMutationPreview generation:**
   - Call `preview_configuration` to produce a `FrozenMutationPreview`.
   - The preview freezes target path, mutation contents, scope (`project` or `global`), baseline hash, and expiration timestamp.
2. **Target & scope immutability:**
   - Once generated, target paths and scope are immutable. Apply cannot re-derive targets, switch scope, or touch un-previewed files.
3. **Stale preview checks:**
   - Before applying, `apply_configuration` verifies that the preview has not expired, has not already been applied, and that the on-disk target baseline matches `baseline_hash` exactly. Any baseline drift triggers immediate fail-closed abort.
4. **Post-apply validation:**
   - `validate_configuration` reads back real host state (runtime and/or filesystem) to confirm the changes took effect.
