---
name: code-review
description: Review the diff since a fixed point along Standards and Spec axes in parallel sub-agents, reporting findings without editing the target or deciding the final verdict. Use when the user wants to review a branch, PR, or work-in-progress diff, or when review-loop or project-review requests a specialist software check.
---

# Code Review

`code-review` is a **read-only specialist reviewer**. It checks a bounded `git
diff` along two independent axes and returns findings. It does not edit files,
run a repair loop, or decide the final `PASS` / `FAIL` / `BLOCKED` — that
belongs to `project-review` (which uses `review-loop` as its convergence
engine). The engine never issues the final acceptance verdict.

Read [WORKFLOW.md](references/WORKFLOW.md) before starting a run. The smell
baseline is in [SMELL-BASELINE.md](references/SMELL-BASELINE.md); examples are
in [EXAMPLES.md](references/EXAMPLES.md).

Reference baseline: Matt `code-review` per [ATTRIBUTION.md](ATTRIBUTION.md).
Light keeps its two-axis method and exposes it as a reviewer invokable via
`review-loop` / `project-review` (SPEC §9, §15 ADAPT). It may be invoked
explicitly (`$code-review`) or as a model-invoked reviewer inside
`review-loop` (engine) on behalf of `project-review` or another caller.

## When to use

- User explicitly invokes `$code-review` on a diff since a fixed point, or
  `review-loop` (on behalf of `project-review` or another caller) invokes
  this Skill with a frozen fixed point and approved Spec. `project-review`
  uses the `software` Profile; `review-loop` is the convergence engine.
  Locate the originating issue/Spec through the active repository's tracker
  convention or the path the user supplied.
- The diff exists (`git diff <fixed-point>...HEAD` is non-empty). Do not use
  it to invent a target, hunt generic bugs outside the diff, or perform a
  whole-repo redesign.

## Core behavior

1. **Pin the fixed point.** Resolve the user-supplied ref (commit, branch, tag,
   `HEAD~N`, or the frozen point from `review-loop`) with `git rev-parse`,
   capture `git diff <fixed-point>...HEAD` (three-dot, against the merge-base)
   and `git log <fixed-point>..HEAD --oneline`, and fail early on a bad ref or
   empty diff before spawning sub-agents (see [WORKFLOW.md](references/WORKFLOW.md)).

2. **Locate the Spec and standards sources.** Fetch the originating issue/Spec
   via the tracker, the path the user passed, or a `docs/` / `.scratch/`
   lookup; and skim repository standards docs (`CODING_STANDARDS.md`,
   `CONTRIBUTING.md`, etc.). A missing Spec yields “no spec available” on the
   Spec axis rather than an invented one.

3. **Run both axes in parallel sub-agents.** Invoke a dedicated Standards
   sub-agent and a Spec sub-agent with non-overlapping contexts and forbid them
   from re-invoking `code-review` or spawning further agents. Prompt briefs and
   finding shapes are in [WORKFLOW.md](references/WORKFLOW.md).

4. **Aggregate separately.** Present verbatim or lightly cleaned reports under
   `## Standards` and `## Spec`, plus a one-line per-axis summary (total
   findings and worst issue within that axis). Do not merge or rerank across
   axes.

## Composition

```text
review-loop (engine) → code-review → findings → Producer repair → re-review → handoff
project-review → review-loop → code-review → findings → Core validation → bounded repair → Evaluator → PASS/FAIL/BLOCKED
```

`code-review` supplies `review` evidence and candidate findings; `project-review`
Core validates dispositions (`confirmed` / `rejected` / `duplicate` /
`out-of-scope`), directs only bounded Producer repairs via `review-loop`, and
owns the final `PASS` / `FAIL` / `BLOCKED` under the `software` Profile.
`review-loop` itself drives only the lightweight
`resolve → invoke → receive → return repair → re-run` loop and stops at
`Findings: []` or bounded limit without issuing a project verdict.

## Stopping boundary

- Read-only: never edits the target, never runs a repair loop, never claims
  the final verdict.
- One bounded diff per run; every finding carries a citation — standards file
  + rule or smell name + quoted hunk on Standards, spec line on Spec.
- Tooling-enforced style is skipped; repo standards override the baseline smell
  set; smells remain labelled judgement calls.

