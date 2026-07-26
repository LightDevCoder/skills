# `ask-light` user guide

[中文指南](../zh-CN/skills/ask-light.md)

The scanner and output contract are defined by
[skills/ask-light/SKILL.md](../../skills/ask-light/SKILL.md) and
[discovery-contract.md](../../skills/ask-light/references/discovery-contract.md).

## What it solves

`ask-light` inspects visible Skill metadata and availability, then reports one
best next Skill or one bounded workflow recipe. It keeps duplicate source
identities, reads bodies only for a shortlist, reports missing metadata, and
preserves invocation policy.

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
availability/readable roots, and invocation control. Metadata is read first;
body/reference reads are bounded. `RECOMMEND` includes reason and invocation.
Missing context returns `NEED-INPUT`; an unavailable required package or
unreadable metadata returns `BLOCKED` with an accurate gap. A private
`skills-3rdParty` root must never be described as visible when it is absent.

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
automatic chain. It may point to `project-init`, `learn-anything`,
`manuscript-ops`, `to-spec`, `implement`, `code-review`, or `review-loop`; the
user chooses each next explicit entry point. `review-loop` owns any final
verdict. Stop after the recommendation or the `NEED-INPUT`/`BLOCKED` record.

## Installation and discovery check

For the published v0.1.1 release, install with `npx skills add LightDevCoder/skills#v0.1.1 --skill ask-light`,
refresh, and inspect `SKILL.md`, `agents/openai.yaml`, and the PowerShell
scanner without the source checkout. Run
[ask-light contract tests](../../skills/ask-light/tests/ask-light-contract-tests.ps1)
and [behavior tests](../../skills/ask-light/tests/ask-light-behavior-tests.ps1),
including the learn-anything, missing-private-dependency, and ambiguity
fixtures.
