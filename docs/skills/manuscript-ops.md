# `manuscript-ops` user guide

[中文指南](../zh-CN/skills/manuscript-ops.md)

The full behavior contract is [skills/manuscript-ops/SKILL.md](../../skills/manuscript-ops/SKILL.md).

## What it solves

`manuscript-ops` routes and governs manuscript engineering from notes and
structured reports through multilingual, multi-format deliverables. It keeps
source authority, user decisions, reproducible generation, review evidence,
format QA, locks, and resume boundaries visible.

## When to use and when not to

Use it for a manuscript, manual, book, multilingual edition, or format-heavy
document project with meaningful source, batch, review, or production risk.
Preflight scores Quick, Structured, or Project and takes exactly one route.
Do not use it as a generic task router, silent project initializer, automatic
workflow manager, or substitute for `review-loop`'s generic verdict mechanics.

It is `model-invoked` and may also be manually entered when the host permits:

```text
$manuscript-ops
$manuscript-ops resume
```

## Preconditions, inputs, and outputs

Resolve the exact project root, read applicable instructions and state, inspect
formats/sources/capabilities, and ensure Python 3.11+ for the bundled tools.
Inputs include the six routing dimensions, source register, Manuscript Brief,
Project Profile, format set, acceptance axes, and existing state. Outputs are
routing snapshots, explicit handoffs, resumable state, source/batch/format
records, review evidence, and production QA records.

## Handoffs, success, and `BLOCKED`

On a Project route, choose one discovery handoff: `grill-me` for one-session
decisions or `wayfinder` for multi-session uncertainty, then stop. `grill-me`
is the user-facing entry point; its underlying model-invoked capability is
`grilling`, so it is one clarification capability rather than two user steps.
Continue only after the user explicitly resumes `manuscript-ops`. Before initialization,
the user must explicitly choose `project-init`; before review, an approved
`review-loop` Charter is required. `BLOCKED` is correct for a missing root,
missing dependency, unapproved brief, absent capability, missing evidence, or
unavailable rendering/round-trip proof. Never claim visual acceptance from a
syntactically valid file.

## Composition and final authority

The normal governed path is `manuscript-ops` → `grill-me`/`wayfinder` →
`project-init` → `review-loop init` → production → `review-loop` manuscript
review. The user controls every user-invoked handoff and resume. `review-loop`
owns generic findings, independence, state, and final `PASS`/`FAIL`/`BLOCKED`;
`manuscript-ops` supplies the manuscript-specific evidence boundary and
consumes that verdict. Stop at every stated handoff or final verdict.

## Installation and discovery check

For the published v0.1.1 release, install with `npx skills add LightDevCoder/skills#v0.1.1 --skill manuscript-ops`,
refresh, and verify the complete package including `assets/`, `references/`,
and `scripts/` without the source checkout. Probe local capabilities and run
the package's state/dependency checks before treating a format result as
verified.
