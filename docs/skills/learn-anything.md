# `learn-anything` user guide

[中文指南](../zh-CN/skills/learn-anything.md)

The package contract at [skills/learn-anything/SKILL.md](../../skills/learn-anything/SKILL.md)
is the sole behavior authority.

## What it solves

`learn-anything` tests whether source material contains a repeatable method,
then extracts a source-backed internal Method Contract. It preserves triggers,
decisions, commands, constraints, failure modes, resources, outputs, and
verification instead of turning a passive summary into a Skill.

## When to use and when not to

Use it when a conversation, transcript, issue, folder workflow, README, or
repeated correction contains a reusable operating method. Do not use it for a
one-off task, narration, sparse notes, or generic authoring advice. Incomplete
evidence must produce a learning summary or `BLOCKED`, not invented fields.

This is `user-invoked only`:

```text
$learn-anything
```

The input is the source material, provenance, exact commands/paths/errors, and
any existing project or Skill rules. A complete result is an internal Method
Contract. Only after that gate may the deterministic Package Build Layer render
or update a package, using for example:

```text
python learn-anything/hooks/package_builder.py --contract-file <method-contract-result.json> --output-root <skill-collection-root>
```

The package builder reports `created`, `updated`, `no-op`, `duplicate`, or
`blocked`; install only complete generated packages and verify idempotency.

## Success and `BLOCKED`

Success means every required method field is evidenced and unresolved markers
are absent. `BLOCKED` names the missing method fields, contradictory
invocation evidence, unresolved resource, or duplicate ownership conflict.
`not_promoted` is correct for a passive or one-off source. Do not fill a gap
with generic Purpose, Workflow, or Quality Checks.

## Composition and stopping

`writing-great-skills` may provide optional authoring knowledge after the Method
Contract. It is not an implicit runtime dependency. A deterministic package
build hands to `review-loop` with the `agent-skill` Profile; admission owns the
next gate. Stop at the Method Contract, package-build result, or exact
`BLOCKED` gap. `learn-anything` never silently invokes another user-invoked
Skill.

## Installation and discovery check

For the published v0.1.1 release, install with `npx skills add LightDevCoder/skills#v0.1.1 --skill learn-anything`,
refresh the host, and confirm `SKILL.md`, `agents/openai.yaml`, and the `hooks/`
resources are discovered without the source checkout. The explicit metadata
policy must read `allow_implicit_invocation: false`.
