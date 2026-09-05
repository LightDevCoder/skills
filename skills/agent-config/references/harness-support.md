# Harness Support & Companion Runtime Matrix

This reference documents the host harness coverage, companion MCP registration mechanism, and generic fallback semantics for `agent-config`.

## P0 Mainstream Native Harnesses (10)

The v1 companion runtime implements native host adapters for 10 mainstream agent harnesses:

1. **Codex CLI**: Native host identification, model inventory inspection, configuration preview, apply, and validation.
2. **Claude Code**: Native host identification, model inventory inspection, headless configuration and companion registration inspection.
3. **OpenCode**: Native host identification via config/environment, model inventory, tool inspection, configuration preview, apply, and validation.
4. **Gemini CLI**: Native host identification, model inventory inspection, discrete effort level detection.
5. **GitHub Copilot CLI**: Native host identification, active model inventory, and runtime capability detection.
6. **Cursor**: Native workspace/editor identification, model selection, reasoning effort, and subagent inspection.
7. **Kiro**: Native harness identification, model configuration inspection, and execution settings.
8. **Zed**: Native editor/assistant identification, model context inspection, and discrete effort capabilities.
9. **DeepSeek Harness (DSH)**: Native harness identification, deep reasoning model detection, and concurrency inspection.
10. **Grok Build**: Native harness identification, build/agent capability detection, and reasoning effort controls.

### Native Adapter Acceptance Criteria

An adapter is classified as **Native** only if it genuinely implements applicable host-level operations:
- Host and version identification
- Host capability, model inventory, and discrete reasoning effort inspection
- Concurrency, subagent, and thread dispatch inspection
- Companion MCP registration detection, preview, apply, and validation
- Host configuration preview, safe mutation (where supported), and validation
- Profile compatibility validation

Where a harness lacks a specific capability (e.g. per-agent model selection or runtime reasoning control), the adapter reports `unavailable` rather than fabricating support.

## Companion MCP Registration Mechanism & Approval Semantics

The companion MCP server provides host inspection, profile persistence, and configuration mutation through an explicit, gated protocol:

1. **Registration Detection**: Companion MCP detects registration status across host environments.
2. **Deterministic Preview**: `preview_configuration` generates a deterministic diff, preview identifier, target list, baseline hash, and expiration timestamp.
3. **User Approval Required**: Host configuration is never mutated silently. The user must inspect and explicitly confirm the preview before execution.
4. **Safe Apply**: `apply_configuration` validates that the preview ID is valid, unexpired, and that target host configuration has not drifted from the baseline hash before applying changes.
5. **Post-Apply Validation**: `validate_configuration` reads back runtime state to verify that the applied configuration matches expected state.

## Generic / Manual Fallback Semantics

For unsupported, future, or emergency harnesses where no native adapter is available:
- **Generic Fallback Adapter**: Automatically activated when zero native adapters identify the workspace or host environment.
- **Plan-Only Mode**: Operates in read-only / plan-only mode by default. Generates execution plans and guidance without attempting host-specific file or configuration mutations.
- **No Silent Mutation**: Forbids unverified writes or speculative configuration changes.
- **Manual Application**: Users review the generated execution plan and apply configuration changes to their host manually.

### Native vs. Generic Fallback Distinction

- **Native Support**: Full host-specific inspection, companion registration, preview/apply mutation lifecycle, and validation.
- **Generic Fallback**: Pure plan-only mode without host-specific mutations.
- **Acceptance Invariant**: Generic fallback does not count toward the required 10/10 P0 native harness acceptance target.
