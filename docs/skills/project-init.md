# `project-init` user guide

[中文指南](../zh-CN/skills/project-init.md)

The behavior authority is [skills/project-init/SKILL.md](../../skills/project-init/SKILL.md).

## What it solves

`project-init` inspects a target and writes the smallest confirmed project
guidance from a preset. It preserves existing instructions and validates the
paths it changed; it is an initialization aid, not a project manager.

## When to use and when not to

Use it for a new or poorly initialized software, manuscript, research,
knowledge-base, data-analysis, or Skill-development project when a minimal
preset is enough. Do not use it to perform discovery, write a specification,
create tickets, implement business code, establish acceptance, or manage a
permanent workflow. Those are later explicit choices.

## Boundary and inputs

This is `user-invoked only`; the user must select `$project-init`. The target
defaults to the current directory. Before writing, it reads root
`AGENTS.md`/`CLAUDE.md`, README, manifests, project documents, and current
status. It needs the project type, visible goal, outputs, collaboration mode,
constraints, and required review level, either from the brief or from its
short questions. It does not use a separate clarification Skill; deep
discovery belongs to `$clarify` / `$project-clarify` / `$decision-map`.

```text
$project-init
```

The output identifies the selected preset or confirmed fallback, one
instruction target, paths changed, capabilities available/unavailable,
validation results, and optional next Skills. It must not create tickets,
implementation plans, final-review records, or a competing specification.

## Success and `BLOCKED`

Success means exactly one instruction target was updated or created, existing
content remains present, the `## Project Initialization` section is singular,
paths stay inside the requested root, and rerunning is idempotent. Return
`BLOCKED` when the root is absent, instructions conflict without a safe
precedence decision, the preset is ambiguous, or a confirmed fallback lacks
its evidence. On rejection or an unconfirmed fallback, write nothing.

## Composition and stopping

`ask-light` may recommend this Skill. After initialization, the user may
explicitly choose `project-spec`, `manuscript-ops`, or `project-review`; this
Skill does not call them. Initialization is the stopping boundary: it is not
discovery, specification, implementation, or final review.

## Installation and discovery check

For the published v0.1.2 release, install with `npx skills add LightDevCoder/skills --skill project-init --yes --copy --agent '*'`,
refresh the host, and confirm the package is discovered without the source
checkout. Run the contract and behavior tests in
[skills/project-init/tests/](../../skills/project-init/tests/) and record any
host limitation in the release evidence.
