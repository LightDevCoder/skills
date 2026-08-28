# `kb-init` user guide

[中文指南](../zh-CN/skills/kb-init.md)

The behavior authority is [skills/kb-init/SKILL.md](../../skills/kb-init/SKILL.md).
This page explains usage without creating a second contract.

## Purpose

`kb-init` is a user-invoked Skill for designing and initializing a maintainable
knowledge base. It runs a knowledge-base-specific interview first, discovers
how the selected base can actually be operated, produces an implementation
SPEC, and waits for explicit user approval before creating anything.

It is not a generic grilling skill and it is not tied to any one wiki, note
app, database, or file format.

## Invoke

Select it explicitly:

```text
$kb-init
```

It must not trigger on its own from a generic mention of knowledge bases,
notes, wikis, or research archives. Once invoked with little or no prompt, it
starts the interview automatically.

## Expected results

- **Success:** the interview surfaces the required design areas, the user ends
  it explicitly, a knowledge-base-specific SPEC is produced, and only an
  explicit approval starts implementation, validation, and handoff.
- **Boundary:** a question or challenge from the user is answered before the
  interview continues; the underlying decision stays open.
- **Failure:** producing a SPEC or implementing anything before explicit user
  approval violates the contract and must not be presented as a valid
  `kb-init` result.

`kb-init` may call the model-invoked `research` capability when current
external facts are needed. It never invokes another user-invoked Skill.

## Verification and release state

Run [the package contract test](../../skills/kb-init/tests/) and inspect
`agents/openai.yaml` for `allow_implicit_invocation: false`. The full
admission path used `project-review` (via `review-loop`); the final verdict
is `PASS` with no unresolved `BLOCKED` condition. Evidence is recorded in the
[admission record](../evidence/admissions/kb-init/README.md).

`kb-init` is released in v0.1.6. Install it with
`npx skills add LightDevCoder/skills --skill kb-init`,
refresh, and confirm discovery without the source checkout under
the [installation policy](../INSTALLATION.md).
