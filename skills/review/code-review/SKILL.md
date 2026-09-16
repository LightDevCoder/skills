---
name: code-review
description: Review the diff since a fixed point along Standards and Spec axes in parallel sub-agents, reporting findings without editing the target or deciding the final verdict. Use when the user wants to review a branch, PR, or work-in-progress diff, or when review-loop or project-review requests a specialist software check.
---

# Code Review

`code-review` is a read-only specialist reviewer for a bounded git diff. It
reports findings on Standards and Spec axes and returns them; it never edits
files, runs a repair loop, or issues the final `PASS` / `FAIL` / `BLOCKED`.

## Core behavior

1. **Pin the fixed point.** Resolve the ref with `git rev-parse`; capture
   `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`.
   A bad ref or empty diff stops before any sub-agent runs.
2. **Locate sources.** Find the originating issue/Spec and repository
   standards docs. A missing Spec yields "no spec available", not an invented
   requirement.
3. **Run both axes in parallel sub-agents.** Dedicated Standards and Spec
   sub-agents share no context and may not re-invoke `code-review` or spawn
   further agents.
4. **Aggregate separately.** Present `## Standards` and `## Spec` reports with
   a one-line per-axis summary. Do not merge or rerank across axes.

Every finding carries a citation: standards file + rule or smell name + quoted
hunk, or the Spec line. Tooling-enforced style is skipped; repo standards
override the baseline smell set; smells remain labelled judgement calls.

## Composition

```text
review-loop → code-review → findings → Producer repair → re-review → handoff
project-review → review-loop → code-review → findings → Core validation → bounded repair → PASS/FAIL/BLOCKED
```

Detailed prompts and smell baseline are in
[WORKFLOW.md](references/WORKFLOW.md) and
[SMELL-BASELINE.md](references/SMELL-BASELINE.md); examples are in
[EXAMPLES.md](references/EXAMPLES.md).