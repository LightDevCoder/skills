# `project-init` user guide

[中文指南](../zh-CN/skills/project-init.md)

The behavior authority is [skills/project-init/SKILL.md](../../skills/project-init/SKILL.md).

## What it solves

`project-init` bootstraps the stable repository configuration consumed by later
Light Project Skills. It preserves existing instructions and manual notes,
creates only consumer-backed contracts, and is safe to rerun.

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
status. It needs project type, goal, outputs, collaboration, constraints,
relevant Skills, issue tracker, domain-context locators, review profile and
acceptance strategy, working area, and the instruction filename established by
current host evidence. The supported tracker locator is
`.scratch/<effort>/issues`; other locators need an adapter. If two presets fit,
it compares their consequences, recommends one, and asks for the choice. It does not use a separate clarification Skill; deep
discovery belongs to `$clarify` / `$project-clarify` / `$decision-map`.

```text
$project-init
```

The output is one instruction pointer plus `docs/agents/light-project.md` and
`docs/agents/issue-tracker.md`, followed by an exact created/updated/preserved
report. It does not create triage labels, tickets, implementation plans,
final-review records, or a competing specification.

The transactional bootstrap helper requires Python 3.9 or newer. If that
runtime is unavailable, initialization returns `BLOCKED` before writing.

## Success and `BLOCKED`

Success means exactly one instruction target points to the stable contract,
both managed contracts exist inside the requested root, manual content remains,
all three targets resolve to distinct files, and rerunning updates one managed
block without duplication. Return `BLOCKED`
when the root is absent, a preset choice is unresolved, or a confirmed fallback
lacks evidence. On rejection or an unconfirmed fallback, write nothing.

## Composition and stopping

`ask-light` may recommend this Skill. After initialization, the user may
explicitly choose `project-spec`, `manuscript-ops`, or `project-review`; this
Skill does not call them. Initialization is the stopping boundary: it is not
discovery, specification, implementation, or final review.

## Installation and discovery check

Install with `npx skills add LightDevCoder/skills --skill project-init`,
refresh the host, and confirm the package is discovered without the source
checkout. Run the contract and behavior tests in
[skills/project-init/tests/](../../skills/project-init/tests/) and record any
host limitation in the release evidence.
