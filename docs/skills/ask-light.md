# `ask-light` user guide

[中文指南](../zh-CN/skills/ask-light.md)

The workflow advisor, router, and output contract are defined by
[skills/ask-light/SKILL.md](../../skills/ask-light/SKILL.md) and
[discovery-contract.md](../../skills/ask-light/references/discovery-contract.md).

## What it solves

`ask-light` is the Light workflow advisor, navigator, and router. It inspects
real project and host evidence deterministically, understands the user's
situation and candidate Skill contracts, reasons about the best next Light Skill
with context-specific workflow reasoning, waits for user approval, and validates
the chosen action against repository constraints before transitioning.

Architecture:
```text
Code establishes trustworthy facts.
Model understands the situation.
Model chooses the workflow action.
Code validates that choice.
```

## Modes and boundaries

This is `user-invoked only`. The primary commands are:

```text
$ask-light next
$ask-light workflow
$ask-light <category>
```

`next` returns one evidence-based recommendation and at most one materially
different alternative. `workflow` returns one recipe anchored at the current
state with step availability, handoff contracts, and stop conditions. `navigate`
answers collection-browsing questions such as “show project Skills” or exact
comparisons.

Before approval, `ask-light` is read-only: it does not invoke, install, edit,
delegate, or create a permanent state machine. After the user approves with a
normal `yes`/`可以`/`go ahead`, it may begin a model-invoked recommended Skill
where the host supports that. For a user-invoked recommended Skill, an approved
transition begins directly only where verified host evidence supports approved
transitions; otherwise it renders the exact invocation (`$<skill>` on Codex,
`/<skill>` on Claude Code) and asks the user to start it. It does not fake
execution, does not auto-chain past the accepted Skill, and never assumes
capabilities without host evidence.

## Inputs and outputs

`ask_light.py` provides deterministic evidence collection (`--mode next`),
recipe publication (`--mode workflow`), taxonomy lookup (`--mode navigate`),
and post-selection validation (`--mode validate`). Semantic routing judgment
belongs to the model. An unavailable selection or constraint conflict returns
`BLOCKED` while preserving the logical recommendation.

The executable helper requires Python 3.9 or newer and supports root discovery
(via `LIGHT_SKILL_ROOTS`, source checkout `skills/` root, or documented host
roots). The PowerShell launcher returns a structured `BLOCKED` result when
Python is unavailable; use the documented manual protocol in that environment.

Example result handling:

```text
Mode: next
Status: RECOMMEND
Skill: project-tickets
Scope: current-workflow
Next: awaiting-approval
Execution: recommendation phase was read-only; execution begins only after explicit user approval
```

## Misuse, composition, and stopping

Do not use it as a discovery/specification engine, installer, scheduler, or
silent automatic chain. It routes among real first-party Skills, including
`project-init`, `project-clarify`, `project-spec`, `project-tickets`,
`implement`, `code-review`, `project-review`, `learn-anything`, or
`manuscript-ops`. Execution begins only after user consent and then only in the
host-supported way. Canonical project flow is `project-clarify → project-spec →
project-tickets → implement → project-review`. `project-review` owns final
acceptance. Stop after the recommendation until approval, or at the
`NEED-INPUT`/`BLOCKED` record.

## Installation and discovery check

For verification, copy the complete `ask-light` package into an isolated
host-recognized Skill root, refresh, and inspect `SKILL.md`,
`light-skill-map.json`, the Python helper, and the PowerShell compatibility
launcher without relying on the source checkout. Do not publish an installer
command as verified until it has succeeded against the actual released
repository. Run [ask-light contract tests](../../skills/ask-light/tests/test_ask_light_contract.py)
and [behavior tests](../../skills/ask-light/tests/test_ask_light_behavior.py),
covering evidence inspection, selection validation, review transaction safety,
freshness checks, root discovery, provenance, host availability, and
approval-transition boundaries.