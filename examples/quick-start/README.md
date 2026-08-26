# Quick Start example

[中文版本](README.zh-CN.md)

This tiny example shows the explicit selection boundary for the first-party
collection. It is intentionally a documentation fixture, not a project
workflow and not a record of commands already run.

## 1. Install

The commands below install the published v0.1.2 release. The output remains a
recommendation boundary; installation does not authorize automatic chaining.

```text
npx skills add LightDevCoder/skills --yes --copy --agent '*'
```

Refresh the Agent host and confirm discovery without this source checkout.
For a single package, use for example:

```text
npx skills add LightDevCoder/skills --skill ask-light --yes --copy --agent '*'
```

## 2. Inspect the example

Read [brief.md](brief.md) and [AGENTS.md](AGENTS.md). They provide just
enough context for an Agent to choose an entry point; they do not authorize
writing business code or silently chaining Skills.

## 3. Invoke explicitly

```text
$ask-light next
$project-init
$project-review init using brief.md
```

Choose only the command that matches the current state. The expected result is
an inspectable recommendation, minimal initialization report, or review
Charter/state. The following is illustrative output, not a claim that this
repository ran it:

```text
Status: RECOMMEND
Execution: recommendation only; nothing was invoked, installed, or orchestrated
```

## 4. Stop and hand off

After `$ask-light`, stop and let the user select the next Skill. After
`$project-init`, stop before discovery/specification/implementation/final
review. After `$project-review`, stop at its durable `PASS`, `FAIL`, or
`BLOCKED` verdict. See [workflow recipes](../../docs/workflows/recipes.md) for longer
handoff examples and [fresh-install evidence](../../docs/evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.md)
for real release verification.
