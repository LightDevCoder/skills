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
   (`AGENTS.md` or `CLAUDE.md`). Ask only fields inspection did not settle, one
   short question at a time.
4. **Bootstrap idempotently.** Use
   [bootstrap.py](scripts/bootstrap.py) to write or update
   `docs/agents/light-project.md`, `docs/agents/issue-tracker.md`, and one
   instruction pointer in the inspected host target. Preserve manual additions
   and previously valid decisions; revise only confirmed fields. The current
   local-markdown adapter uses `.scratch/<effort>/issues`; other tracker
   locators fail closed until an adapter exists.
   The helper requires Python 3.9 or newer; if unavailable, report `BLOCKED`
   before any write instead of emulating the transaction manually.
5. **Validate and report.** Confirm every created path is inside the target
   root, the managed blocks are unique, existing text is preserved, and named
   capabilities are readable or marked unavailable. Report the exact created,
   updated, and preserved paths, then stop.

## References

- [presets.md](references/presets.md) — preset table and minimal instruction
  blocks.
- [initialization-contract.md](references/initialization-contract.md) —
  stable output schema, instruction precedence, plan gate, downstream
  consumption, validation, and capability boundary.
