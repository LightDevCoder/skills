---
name: project-tickets
description: Turn a formal SPEC into tracer-bullet vertical slices with blocking edges, then publish them as single-file-per-ticket issues on the local markdown tracker. Use only when the user explicitly invokes $project-tickets; it verifies the SPEC handoff, drafts a quiz-able breakdown, and hands execution to the frontier via implement.
disable-model-invocation: true
---

# Project Tickets

`project-tickets` is an explicit, user-invoked planning stage. Run it only
after an explicit `$project-tickets` request. It turns a verified SPEC into
numbered, one-file-per-ticket issues on the local markdown tracker.

## Core behavior

1. **Verify the SPEC handoff.** Read the SPEC at the supplied path; a missing
   or malformed SPEC is a handoff gap — report it and stop.
2. **Draft tracer-bullet vertical slices.** Each slice is a narrow, complete,
   demoable path through the relevant layers, with `Blocked by` edges,
   `ready work`, and `parallelizable` groups.
3. **Quiz the user.** Show title, Blocked by, and what each ticket delivers;
   iterate until the granularity and edges are approved.
4. **Publish one file per ticket** under `.scratch/<feature>/issues/`, numbered
   from `01` in dependency order with the approved shape unchanged.

## Handoff

After publishing, describe the frontier and recommend explicit `$implement`
on the chosen ticket, then stop.

## References

- [WORKFLOW.md](references/WORKFLOW.md) — full slicing procedure and
  wide-refactor sequencing.
- [TICKET-CONTRACT.md](references/TICKET-CONTRACT.md) — canonical ticket file
  shape and Wayfinding compatibility.
- [EXAMPLES.md](references/EXAMPLES.md) — dog-food and boundary examples.