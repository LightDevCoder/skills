# Skills CLI Canonical Conventions & Upstream Provenance

> **Role & Authority Boundary:**
> This document is a **human-readable provenance reference** documenting the verified conventions of the official upstream Skills CLI.
> It is **not** a secondary runtime source of truth.
> The single runtime source of truth for agent target mapping is `skills/project/project-init/scripts/bootstrap.py` (`AGENT_TARGETS` and `AGENT_TARGET_ALIASES`), guarded by parameterized contract tests in `skills/project/project-init/tests/test_project_init_behavior.py`.

---

## Upstream Provenance

- **Upstream Package:** `vercel-labs/skills` (npm: `skills`)
- **Verified Version:** `v1.7.0`
- **Verified Date:** 2026-09-20
- **Upstream CLI Command:** `npx skills add <package> --skill <name> --agent <cli_agent_id> --yes`

---

## Canonical Agent Mapping & Scope Matrix

The following table records the canonical mapping from Light internal host keys to official Skills CLI agent identifiers (`--agent <cli_agent>`) and project-level skill directories:

| Internal Host Key | Canonical CLI Agent ID (`--agent`) | Canonical Project Scope | Official Global Search Roots | Aliases |
| :--- | :--- | :--- | :--- | :--- |
| `pi` | `pi` | `.pi/skills` | `~/.pi/agent/skills` | `pi` |
| `claude` | `claude-code` | `.claude/skills` | `~/.claude/skills` | `claude-code` |
| `cursor` | `cursor` | `.agents/skills` | `~/.cursor/skills` | `cursor` |
| `codex` | `codex` | `.agents/skills` | `~/.codex/skills` | `codex` |
| `agy` | `antigravity` | `.agents/skills` | `~/.gemini/antigravity/skills` | `antigravity` |
| `grok-build` | `grok` | `.grok/skills` | `~/.grok/skills` | `grok` |
| `hermes` | `hermes-agent` | `.hermes/skills` | `~/.hermes/skills` | `hermes-agent` |

### Critical Invariants

1. **Shared `.agents/skills` Project Scope:**
   In `vercel-labs/skills` v1.7.0, Cursor, Codex, and Antigravity all install project-scoped skills into `.agents/skills/`. They do **not** use separate `.cursor/skills` or `.agy/skills` for project-local installations.
2. **Distinct CLI Agent Identifiers:**
   The CLI `--agent` argument requires canonical identifiers:
   - Claude Code uses `claude-code` (not `claude`).
   - Antigravity uses `antigravity` (not `agy`).
   - Grok Build uses `grok` (not `grok-build`).
   - Hermes uses `hermes-agent` (not `hermes`).
3. **Fail-Closed Policy for Unsupported Hosts:**
   Harnesses and environments not officially supported by `vercel-labs/skills` (such as DeepSeek Harness / DSH) must fail closed deterministically:
   - Status: `TARGET_UNRESOLVED`
   - Installer invocations: **0** (never invoke `npx skills add` with guessed or unverified agent identifiers).
   - No project skill mutation occurs; project initialization proceeds with deterministic fallbacks.
