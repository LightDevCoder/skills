# 01 — Host Evidence Schema v2 & Provider Adapter Contract

**What to build:** Upgrade the host evidence schema to v2 and define the provider adapter contract, enabling host-aware model routing by relative rank and reasoning effort while preserving backward compatibility for v1 evidence and maintaining strict provider neutrality.

**Blocked by:** None — can start immediately

**Status:** resolved

- [x] `skills/agent-config/references/host-evidence-schema.md` defines `schema_version: 2` with explicit fields for `routing_rank`, `routing_metadata_evidence`, `reasoning_control` (state, levels, assignment_scope), `model_selection` scope, and provider/project adapter metadata.
- [x] Schema specifies backward-compatibility rules where v1 evidence missing `routing_rank` or effort levels normalizes to `tier routing unavailable` without parsing errors.
- [x] Unknown vs unavailable semantics are strictly distinguished across all capability fields.
- [x] `skills/agent-config/references/provider-adapter-contract.md` specifies the semantic interface for inspecting host capabilities, normalizing routing metadata, reporting observation timestamps, and optional project-level configuration apply requests.
- [x] Adapter contract specifies read-only by default, explicit user confirmation required before any configuration mutation, and non-blocking failure recovery when adapter is absent or fails.
- [x] Both documents remain strictly provider-neutral with no vendor-specific paths or model names hardcoded.

## Comments

Source: .scratch/agent-config-refactor/spec.md. §5, §6, §7, §16, §17, §18, §19, §20.

## Answer

Implemented Host Evidence Schema v2 in `skills/agent-config/references/host-evidence-schema.md` and created Provider Adapter Contract in `skills/agent-config/references/provider-adapter-contract.md`. Verified provider neutrality, schema v1 backward compatibility, explicit approval gates for mutation, and unknown vs unavailable separation.
