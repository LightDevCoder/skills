# `ask-light` user guide

[中文指南](../zh-CN/skills/ask-light.md)

The router and output contract are defined by
[skills/ask-light/SKILL.md](../../skills/ask-light/SKILL.md) and
[discovery-contract.md](../../skills/ask-light/references/discovery-contract.md).

## What it solves

`ask-light` first maps intent through the Light-owned 33-Skill semantic map,
then checks whether that selection is available on the active host. Optional UI
metadata never hides a known package, and generic host roots are not accepted
as first-party provenance.

## Modes and boundaries

This is `user-invoked only`. The first explicit commands are:

```text
$ask-light next
$ask-light workflow
```

`next` returns one recommendation and at most one materially different tied
alternative. `workflow` returns one recipe with entry condition, ordered steps,
source, invocation type, expected input/output, handoff artifact, stop
condition, optional flag, and missing dependency. Neither mode invokes,
installs, edits, delegates, or creates a permanent state machine. It does not
reintroduce `project-workflow`.

## Inputs and outputs

Supply goal, artifacts, blockers, project type, task kind, actual host
availability/readable roots, and invocation control. Logical routing comes from
`light-skill-map.json`; package reads only prove host availability and local
pointer integrity. Missing context returns `NEED-INPUT`; an unavailable
selection returns `BLOCKED` while preserving the logical recommendation.

The executable router requires Python 3.9 or newer. The PowerShell launcher
returns a structured `BLOCKED` result when Python is unavailable; use the
documented two-layer manual protocol in that environment.

Example result handling:

```text
Mode: workflow
Status: RECOMMEND
Workflow: software-feature
Execution: recommendation only; nothing was invoked, installed, or orchestrated
```

The output above is illustrative, not a claim that this host ran the recipe.

## Misuse, composition, and stopping

Do not use it as a discovery/specification engine, installer, scheduler, or
automatic chain. It routes only among real first-party Skills and may point to
`project-init`, `learn-anything`, `manuscript-ops`, `project-spec`,
`implement`, `code-review`, or `project-review`; the user chooses each next
explicit entry point. `project-review` owns the final verdict for recipes that
reach acceptance. Stop after the recommendation or the
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
including representative top-result, Frozen metadata, provenance, host
availability, invocation rendering, and pointer-failure cases.
