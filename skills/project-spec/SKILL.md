---
name: project-spec
description: Turn already-clarified outputs from project-clarify or decision-map into a formal project SPEC without reopening an interview. Use only when the user explicitly invokes $project-spec; it returns to project-clarify when a blocking user decision remains and hands off to project-tickets when ready.
disable-model-invocation: true
---

# Project Spec

`project-spec` is an explicit, user-invoked planning stage. Run it only after
an explicit `$project-spec` request. It turns already-clarified material into
one formal SPEC that `project-tickets` can slice.

## Core behavior

1. **Gather and validate** the clarification handoff or map answers plus a
   light repo inspection (glossary, ADRs, existing seams). Use the settled
   facts and decisions as-is; do not reopen them as new questions.
2. **Check the blocking-decision gate.** If a truly blocking user-owned
   decision remains, stop spec work and return to `project-clarify` (or the
   map) with the exact blocker and context pointer.
3. **Synthesize and publish** one bounded SPEC using
   [OUTPUT-FORMAT.md](references/OUTPUT-FORMAT.md), to
   `.scratch/<feature>/spec.md`. Confirm the publish when seams affect scoping.
4. **Stop and recommend** explicit `$project-tickets`.

```text
project-spec → project-tickets
```

## References

- [WORKFLOW.md](references/WORKFLOW.md) — full step sequence and seam check.
- [OUTPUT-FORMAT.md](references/OUTPUT-FORMAT.md) — required SPEC shape.
- [EXAMPLES.md](references/EXAMPLES.md) — dog-food and boundary examples.