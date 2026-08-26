---
name: implement
description: Execute one bounded, already-decided work item — code, document, configuration, research artifact, Skill, or generic project task — by inspecting relevant context, routing execution when useful, verifying locally, and handing the result to review-loop with the appropriate specialist reviewer.
disable-model-invocation: true
---

# Implement

`implement` is a user-invoked bounded executor. Run it only after an explicit
`$implement` request. It turns one ready work item into a verified artifact and
hands it to review.

## Core loop

1. **Pin one work item.** Resolve exactly one ticket, Spec section, or explicit
   conversation slice and record it as the target.
2. **Inspect relevant context.** Skim only the glossary, ADRs, and files the
   item touches; record source locations.
3. **Route execution when useful.** Call `agent-config` only for role
   splitting, parallelism, or independent review isolation; skip it for a
   bounded solo task.
4. **Execute the bounded slice, then verify.** Use `tdd` for code when
   appropriate; produce non-code artifacts per their contract. Verify locally
   (tests, render, schema, or domain check).
5. **Hand to `review-loop`** with the matching reviewer: `code-review` for
   code, `generic-review` or a domain reviewer for non-code. Report evidence
   and stop.

## Composition

```text
implement → agent-config when useful
implement → tdd when appropriate
implement → review-loop → code-review (code) / generic-review (non-code)
```

`implement` composes these capabilities; it does not reimplement them. A
missing or blocked item is a `BLOCKED` handoff gap — report the smallest
unblock and stop. Full per-artifact procedures are in
[WORKFLOW.md](references/WORKFLOW.md); examples are in
[EXAMPLES.md](references/EXAMPLES.md).