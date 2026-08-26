---
name: project-init
description: Initialize a software or non-software project from a minimal preset, preserving existing instructions and validating resulting paths and capabilities. Use only when a user explicitly invokes $project-init to set up generic, software, manuscript, Skill-development, research, knowledge-base, or data-analysis work.
disable-model-invocation: true
---

# Project Init

`project-init` is a user-invoked minimum initialization aid. Run it only
after an explicit `$project-init` request. It creates a small project
structure from a preset; it does not clarify requirements, manage tickets, or
run later workflow stages.

## Execution loop

1. **Inspect before writing.** Read the target root's instructions, README,
   manifests, project documents, and current status. Record confirmed paths
   and missing evidence.
2. **Ask lightweight project questions.** Capture only what is not already
   explicit, one short question at a time: project type, user-visible goal,
   expected outputs, collaboration mode, important constraints, and required
   review level.
3. **Select a preset or prepare a fallback.** Match [presets.md](references/presets.md);
   if no preset matches, draft a plan from `research` and wait for explicit
   `confirm` before writing.
4. **Write the minimum initialization.** Update one instruction target in
   place: existing `AGENTS.md`, else existing `CLAUDE.md`, else a new
   `AGENTS.md`. Preserve existing content and keep one
   `## Project Initialization` section.
5. **Validate and report.** Confirm created paths are inside the target root,
   exactly one instruction target exists, existing text is preserved, and
   declared capabilities are readable or marked unavailable. Report
   implemented/verified/blocked/not-tested/out-of-scope and stop.

## References

- [presets.md](references/presets.md) — preset table and minimal instruction
  blocks.
- [initialization-contract.md](references/initialization-contract.md) —
  instruction precedence, plan gate, validation record, and capability
  boundary.