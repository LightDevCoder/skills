# `review-loop` user guide

[中文指南](../zh-CN/skills/review-loop.md)

The package contract at [skills/review-loop/SKILL.md](../../skills/review-loop/SKILL.md)
is authoritative. This guide explains how to enter it without duplicating the
contract.

## What it solves

`review-loop` turns an approved target and acceptance source into a bounded
evidence, critique, repair, evaluation, and final-verdict loop. Its Core role
freezes the baseline, preserves durable state, enforces stopping rules, and
owns `PASS`, `FAIL`, or `BLOCKED`.

## When to use it

Use it when the target, scope, acceptance authority, evidence boundary, and
applicable Profile are already clear. Use `agent-skill` for an installable
Skill package, `software` for executable software, `manuscript` for document
deliverables, or `specification` for a brief/spec/ticket acceptance contract.

Do not use it to invent a product goal, settle unresolved architecture, write
the artifact as the reviewer, publish a release, or weaken the acceptance
source to fit a result. Use `ask-light`, `project-init`, `to-spec`, or another
explicit handoff first when those decisions are missing.

## Boundary, inputs, and outputs

This is `model-invoked` and also supports a manual entry point. An explicit
manual request remains valid:

```text
$review-loop init using docs/acceptance.md
$review-loop review
$review-loop resume
```

The input is a target, approved acceptance source, selected Profile, review
scope/exclusions, evidence requirements, and writable `.review-loop/` state
when the mode needs durable records. The output is a Charter, state, findings,
round evidence, repair disposition, and ultimately a verdict. A successful
run ends at a durable `PASS`/`FAIL`/`BLOCKED` record; specialist findings do
not replace that verdict.

## Success and `BLOCKED`

Success means the baseline is frozen, admissible evidence covers the declared
axes, findings are dispositioned, repairs stay in scope, and an independent
Evaluator has supplied evidence to the Core. `BLOCKED` is correct when the
acceptance source is missing/unapproved, the target cannot be inspected, the
required Profile/evidence is unavailable, or the independence/state gate
cannot proceed. Record the exact smallest unblock action and stop.

## Composition and stopping

It may consume a confirmed `project-init` result, a `to-spec` or `to-tickets`
handoff, implementation evidence, `code-review` findings, or manuscript
format QA. `code-review` is a specialist source of findings; `review-loop`
remains the final authority. Stop at the verdict and preserve the state before
handing off to `handoff` or release closeout. It does not invoke another
user-invoked Skill implicitly.

## Installation and discovery check

After the v0.1.1 release gate passes, install from the target release with
`npx skills add LightDevCoder/skills#v0.1.1 --skill review-loop`, refresh the
host, and inspect the discovered `SKILL.md` plus `agents/openai.yaml` without
the source checkout. Run the Profile tests under
[skills/review-loop/tests/](../../skills/review-loop/tests/) and keep the
fresh-install result in
[INSTALLATION_VERIFICATION.md](../evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md).
