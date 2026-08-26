# `review-loop` user guide

[中文指南](../zh-CN/skills/review-loop.md)

The package contract at [skills/review-loop/SKILL.md](../../skills/review-loop/SKILL.md)
is authoritative. This guide explains how to enter it without duplicating the
contract.

## What it solves

`review-loop` is the lightweight review engine. It drives one loop —
`review → findings → repair → re-review` — by resolving a reviewer, invoking
it, collecting normalized findings, returning confirmed in-scope findings to
the Producer, and re-running until clean or a bounded limit.

It owns no project final `PASS`/`FAIL`/`BLOCKED`. That acceptance role belongs
to `project-review`.

## When to use it

Use it when a bounded review needs repair convergence: an implementation
handoff, a package review, or a routine review where the caller has a bounded
packet and a concrete repair path.

Do not use it to freeze an acceptance baseline, issue a project verdict, or
replace `project-review`.

## Boundary, inputs, and outputs

It is `model-invoked` and also supports a manual entry point.

The input packet has four fields: Target, Requirements, Relevant context, and
Previous findings. Output is normalized findings (`Findings: []` on clean) or
`REVIEW-ERROR` when a required input is absent. At the bounded limit it hands
outstanding findings to the caller.

## Success and `BLOCKED`

Success means the loop reached `Findings: []` or the caller received the
outstanding findings at the configured limit. `BLOCKED`/`PASS`/`FAIL` are not
engine verdicts; `project-review` issues those after composing reviewers
through this engine.

## Composition and stopping

It composes `generic-review` by default, `code-review` for software diffs, and
accepted domain reviewers. `project-review` is the final-acceptance owner. Stop
at a clean result or at the limit and hand off to the caller; do not invoke
another user-invoked Skill implicitly.

## Installation and discovery check

Install with
`npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'`, refresh the
host, and inspect the discovered `SKILL.md` plus `agents/openai.yaml` without
the source checkout. Run the tests under
[skills/review-loop/tests/](../../skills/review-loop/tests/) and keep the
fresh-install result in
[INSTALLATION_VERIFICATION.md](../evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.md).