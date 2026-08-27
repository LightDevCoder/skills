# `ask-light` user guide

[中文指南](../zh-CN/skills/ask-light.md)

The workflow advisor, router, and output contract are defined by
[skills/ask-light/SKILL.md](../../skills/ask-light/SKILL.md) and
[discovery-contract.md](../../skills/ask-light/references/discovery-contract.md).

## What it solves

`ask-light` first inspects the current project/workflow state, maps intent
through the Light-owned 33-Skill semantic map, then checks whether that
selection is available on the active host. It recommends the next Skill with
workflow reasoning, waits for user approval, and then begins the accepted
Skill. Optional UI metadata never hides a known package, and generic host
roots are not accepted as first-party provenance.

## Modes and boundaries

This is `user-invoked only`. The first explicit commands are:

```text
$ask-light next
$ask-light workflow
$ask-light <category>
```

`next` returns one evidence-based recommendation and at most one materially
different tied alternative. `workflow` returns one recipe with entry condition,
ordered steps, source, invocation type, expected input/output, handoff
artifact, stop condition, optional flag, and missing dependency. `navigate`
answers collection-browsing questions such as “show project Skills” or “which
Skills are for learning?”.

Before approval, `ask-light` is read-only: it does not invoke, install, edit,
delegate, or create a permanent state machine. After the user approves with a
normal `yes`/`可以`/`go ahead`, it begins the recommended Skill in the current
conversation (Codex) or uses the host-supported transition mechanism. It does
not reintroduce `project-workflow` and does not auto-chain past the accepted
Skill.

## Inputs and outputs

Supply goal, artifacts, blockers, project type, task kind, actual host
availability/readable roots, and invocation control when routing a project
stage. Logical routing comes from `light-skill-map.json`; package reads only
prove host availability and local pointer integrity. Missing context returns
`NEED-INPUT`; an unavailable selection returns `BLOCKED` while preserving the
logical recommendation.

The executable router requires Python 3.9 or newer and now supports root
discovery without requiring `--roots-json` (via `LIGHT_SKILL_ROOTS`, a source
checkout `skills/` root, or documented host roots). The PowerShell launcher
returns a structured `BLOCKED` result when Python is unavailable; use the
documented manual protocol in that environment.

Example result handling:

```text
Mode: next
Status: RECOMMEND
Skill: project-tickets
Next: awaiting-approval
Execution: recommendation phase was read-only; execution begins only after explicit user approval
```

## Misuse, composition, and stopping

Do not use it as a discovery/specification engine, installer, scheduler, or
silent automatic chain. It routes only among real first-party Skills and may
point to `project-init`, `learn-anything`, `manuscript-ops`, `project-spec`,
`implement`, `code-review`, or `project-review`; execution begins only after
user consent. `project-review` owns the final verdict for recipes that reach
acceptance. Stop after the recommendation until approval, or at the
`NEED-INPUT`/`BLOCKED` record.

## Installation and discovery check

This router is part of the unreleased 33-package branch. For pre-release
acceptance, copy the complete `ask-light` package into an isolated
host-recognized Skill root, refresh, and inspect `SKILL.md`,
`light-skill-map.json`, the Python router, and the PowerShell compatibility
launcher without the source checkout. Do not publish an installer command as
verified until the containing release has passed the release installation gate. Run
[ask-light contract tests](../../skills/ask-light/tests/test_ask_light_contract.py)
and [behavior tests](../../skills/ask-light/tests/test_ask_light_behavior.py),
including project-state recommendation, approval-to-execution, root discovery,
provenance, host availability, invocation rendering, and pointer-failure cases.