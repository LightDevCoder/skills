# Harness Support & Companion Runtime Matrix

This reference documents host harness coverage, companion MCP registration mechanisms, and generic fallback semantics for `agent-config`.

## Primary Coding-Agent Native Harnesses (9)

The companion runtime provides native host adapters for 9 primary coding-agent harnesses:

1. **Codex CLI**: Native host identification, model inventory inspection, configuration preview, apply, and validation via project and global config.
2. **Claude Code**: Native host identification, model inventory inspection, headless configuration, and companion registration inspection.
3. **Antigravity**: Native host identification (formerly Gemini CLI adapter path), model inventory inspection, discrete effort level detection, and workflow configuration.
4. **DeepSeek Harness (DSH)**: Native harness identification, deep reasoning model detection, and concurrency inspection.
5. **OpenCode**: Native host identification via config/environment, model inventory, tool inspection, configuration preview, apply, and validation.
6. **ZCode**: Native harness identification, model configuration inspection, and execution settings.
7. **Cursor**: Native workspace/editor identification, model selection, reasoning effort, and subagent inspection.
8. **Grok Build**: Native harness identification, build/agent capability detection, and reasoning effort controls.
9. **Hermes**: Native agent harness identification, execution parameters, and model configuration.

### Native Adapter Acceptance Criteria

An adapter is classified as **Native** only if it genuinely implements applicable host-level operations:
- Host and version identification
- Host capability, model inventory, and discrete reasoning effort inspection
- Concurrency, subagent, and thread dispatch inspection
- Companion MCP registration detection, preview, apply, and validation with live reachability verification
- Host configuration preview, safe mutation (where supported), and validation
- Profile compatibility validation

Where a harness lacks a specific capability (e.g. per-agent model selection or runtime reasoning control), the adapter reports `unavailable` or `unknown` rather than fabricating support.

## Deferred Adapters & Generic Fallback

### Deferred Native Adapters
- **Pi**: Documented as `Generic/manual` (deferred native adapter pending v1 stabilization). Native adapter integration is deferred to a future iteration; currently supported via safe generic/manual planning.

### Generic / Manual Fallback
For other hosts, unsupported environments, or future agent harnesses where no native adapter is active:
- **Generic Fallback Adapter**: Automatically activated when zero native adapters identify the workspace or host environment.
- **Plan-Only Mode**: Operates in read-only / plan-only mode by default. Generates execution plans and guidance without attempting host-specific file or configuration mutations.
- **No Silent Mutation**: Forbids unverified writes or speculative configuration changes.
- **Manual Application**: Users review the generated execution plan and apply configuration changes to their host manually.
- **Acceptance Invariant**: Generic fallback does not count toward the required 9 native adapters acceptance target.

## Companion MCP Registration Mechanism & Approval Semantics

The companion MCP server provides host inspection, profile persistence, and configuration mutation through an explicit, gated protocol:

1. **Registration Detection**: Companion MCP detects registration status across host environments using real reachability checks (active tool verification, never guessing reachability from static files).
2. **Frozen Mutation Preview**: `preview_configuration` generates a `FrozenMutationPreview` with deterministic diff, immutable target path, immutable scope (`project` or `global`), cryptographic baseline hash, and expiration timestamp.
3. **User Approval Required**: Host configuration is never mutated silently. The user must inspect and explicitly confirm the preview before execution.
4. **Safe Apply with Stale Preview Checks**: `apply_configuration` validates that the preview ID is valid, unexpired, has not been applied, and that target host configuration has not drifted from the frozen baseline hash before applying changes. If drift is detected, apply is aborted fail-closed.
5. **Post-Apply Validation**: `validate_configuration` reads back real runtime or filesystem state to verify that the applied configuration matches expected state.
