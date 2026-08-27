---
name: ask-light
description: Inspect the first-party Skills available to the active Agent host and recommend either one appropriate next Skill or one bounded workflow recipe from the current goal, artifacts, blockers, project type, task kind, availability, and invocation control. Use only when the user explicitly invokes $ask-light; it reports a recommendation and never executes, installs, or orchestrates it.
disable-model-invocation: true
---

# Ask Light

`ask-light` is the **Light Workflow Router** — a user-invoked, read-only
router built last, after the first-party Skill map exists. It answers "which
installed first-party Skill is the best next fit?" from the active host and
project state. It does not replace project discovery, specification,
implementation, or final acceptance. It never reimplements the capabilities it
routes to.

## Invocation and safety boundary

Run only after an explicit `$ask-light` request. Do not run a recommended
Skill, call a Skill, launch a sub-agent, install a package, edit a project, or
create workflow state. Print the host-appropriate invocation and stop.

The deterministic router in [ask_light.py](scripts/ask_light.py) is the
portable read-only implementation; [ask-light.ps1](scripts/ask-light.ps1) is a
compatibility launcher. Use `$ask-light next` for one next Skill, or
`$ask-light workflow` for one bounded recipe. The two-layer protocol is in
[discovery-contract.md](references/discovery-contract.md).

The executable helper requires Python 3.9 or newer. The PowerShell launcher
returns a structured `BLOCKED` record when that runtime is absent. In that
case, follow the two layers in `discovery-contract.md` manually from the same
declared first-party roots and host evidence; do not guess availability.

## Required input context

Understand current intent, project context, existing artifacts, available
first-party Skills, current project stage, specialized workflow, and host
capabilities before routing. Collect what is known; do not invent missing
facts. The context fields are defined in
[discovery-contract.md](references/discovery-contract.md).

## Routing source

Resolve logical fit from the Light-owned
[Skill Map](references/light-skill-map.json), then verify the selected Skill
against the active host. Installed Skill prose is availability evidence, not
routing semantics. A generic host root or an unknown package beside Light
Skills is not first-party provenance.

## Workflow mode

`$ask-light workflow` returns one bounded recipe recommendation, not an
orchestration engine. It includes each step's Skill, invocation type, expected
input/output, handoff artifact, stop condition, optional flag, and missing
dependency. It never invokes, installs, edits, creates a permanent state
machine, or silently chains user-invoked Skills. Recipe details are in
[discovery-contract.md](references/discovery-contract.md).

When no reliable recipe exists, return `NEED-INPUT`; when a required first-party
Skill is not visible/readable, return `BLOCKED` with an accurate availability
gap.

## Source and host rules

Route only among names in the Light Skill Map and roots explicitly identified
as Light first-party. Optional UI metadata is not proof of existence; a readable
`SKILL.md` is the package requirement. A missing or unreadable selection gets a
manual-install fallback: restore the first-party package, refresh the host, and
re-run `$ask-light`.

## Result contract

Return a compact record with these fields:

```text
Mode: next | workflow
Status: RECOMMEND | NEED-INPUT | BLOCKED
Skill: <one name, or none>
Source: first-party: <resolved package path>
Reason: <context-specific evidence, not a generic description>
Invocation: <host-specific command or picker action>
Confidence: high | medium | low
Alternative: <at most one, only for a material tie>
Gaps: <missing/unreadable metadata and actionable guidance>
Reads: metadata=<count>; bodies=<count>; references=<count>
Execution: recommendation only; nothing was invoked or installed
```

Workflow mode additionally returns `workflow`, `entryCondition`, `steps`,
`stoppingBoundary`, and `finalAuthority`. For a recipe that reaches acceptance,
`finalAuthority` is `project-review`; `ask-light` only reports the recipe and
stops.

## Verification

Run the package contract and behavior tests. They exercise the representative
intent matrix, Frozen metadata compatibility, first-party provenance, host
availability, host invocation rendering, local-pointer failure, workflows, and
the no-execution boundary.
