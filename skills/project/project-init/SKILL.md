---
name: project-init
description: Bootstrap the stable Light project and tracker contracts consumed by downstream Project Skills, preserving manual content and supporting safe reruns. Use only when a user explicitly invokes $project-init for a new or incompletely initialized repository.
disable-model-invocation: true
---

# Project Init

`project-init` is the one-time Light project bootstrap. Run it only after an
explicit `$project-init` request. It creates the stable repository contract
that later Project Skills consume; it does not clarify requirements, create
tickets, or run later workflow stages.

## Execution loop

1. **Inspect before writing.** Read the target root's instructions, README,
   manifests, project documents, and current status. Record confirmed paths
   and missing evidence.
2. **Resolve the preset.** Match [presets.md](references/presets.md). When two
   presets plausibly fit, show a one-line consequence for each, recommend one
   with a reason, and ask which to use. If none fits, draft a sourced fallback
   and wait for explicit `confirm` before writing.
3. **Capture the stable contract.** Record project type, user-visible goal,
   expected outputs, collaboration mode, important constraints, relevant
   Skills, issue tracker, domain-context locations, review profile/acceptance
   strategy, working area, and the active host's inspected instruction filename
   (`AGENTS.md` or `CLAUDE.md`). When confirmed by the user, optionally onboard
   the TypeSafe Jev ecosystem (`typesafe-ai`). Ask only
   fields inspection did not settle, one short question at a time.
4. **Bootstrap idempotently.** Use
   [bootstrap.py](scripts/bootstrap.py) to write or update
   `docs/agents/light-project.md`, `docs/agents/issue-tracker.md`, and one
   instruction pointer in the inspected host target.
   
   **TypeSafe Jev Onboarding Contract:**
   Supports optional `--jev` and `--no-jev` flags for TypeSafe Jev onboarding (key detection, gitignore protection, and global skill reuse).
   When Jev onboarding is selected:
   - Inspect the active Agent host environment.
   - Resolve the supported canonical installer target (`bootstrap.py` canonical mapping is authoritative: `pi` → `pi`, `claude` → `claude-code`, `cursor` → `cursor`, `codex` → `codex`, `agy` → `antigravity`, `grok-build` → `grok`, `hermes` → `hermes-agent`).
   - Pass it explicitly via `--agent-target <target>` to `bootstrap.py`.
   - Never guess unsupported CLI targets; if the host target is unresolved or unsupported (e.g. DeepSeek Harness / DSH), fail closed with `TARGET_UNRESOLVED` (the core project bootstrap still succeeds with 0 installer calls).
   - SDK Policy (`--auto-install-sdk`): Use `--auto-install-sdk` only when the user has explicitly authorized automated dependency installation in non-interactive workflows. In interactive sessions, prompt the user for permission before running `pip install` in the active Python runtime.

   Preserve manual additions and previously valid decisions; revise only confirmed fields. The current local-markdown adapter uses `.scratch/<effort>/issues`; other tracker locators fail closed until an adapter exists.
   The helper requires Python 3.9 or newer; if unavailable, report `BLOCKED` before any write instead of emulating the transaction manually.
5. **Validate and report.** Confirm every created path is inside the target
   root, the managed blocks are unique, existing text is preserved, and each
   declared relevant capability is classified as `available`, `unavailable`,
   or `unknown`. Never silently promote `unknown` to `available`. Report the
   exact created, updated, and preserved paths, the capability statuses, and
   then stop.

## References

- [presets.md](references/presets.md) — preset table and minimal instruction
  blocks.
- [initialization-contract.md](references/initialization-contract.md) —
  stable output schema, instruction precedence, plan gate, downstream
  consumption, validation, and capability boundary.
