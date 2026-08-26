---
name: decision-map
description: Plan a large, multi-session, decision-heavy effort as a persistent decision map of tickets. Use only when the user explicitly invokes $decision-map; it maintains .scratch/<effort>/map.md and child decision tickets until fog clears, then hands off to project-spec.
disable-model-invocation: true
---

# Decision Map

`decision-map` is an explicit, user-invoked planning stage for foggy, large,
or multi-session work. Run it only after an explicit `$decision-map` request.
It charts a persistent decision map on the local markdown tracker and resolves
it one ticket per session.

## Core model

```text
.scratch/<effort>/map.md              ← canonical map
.scratch/<effort>/issues/NN-<slug>.md ← child decision tickets
```

- **Map:** `Destination`, `Notes`, `Decisions so far`, `Not yet specified`,
  `Out of scope`.
- **Ticket:** one decision-sized question with `Type`, `Status`, and
  `Blocked by`.

Exact shapes and tracker operations are in
[MAP-CONTRACT.md](references/MAP-CONTRACT.md).

## Execution

- **Charting:** name the destination, surface the frontier/fog breadth-first,
  create the map and specifiable tickets, wire blocking edges, fire `research`
  tickets in parallel, and stop.
- **Working:** load the map, claim the chosen frontier ticket, resolve it via
  the ticket's capability, append `## Answer` and update the map, then stop
  after one ticket (parallel `research` on charting excepted).

Full mode steps are in [WORKFLOW.md](references/WORKFLOW.md); examples are in
[EXAMPLES.md](references/EXAMPLES.md).

## Composition

Resolve tickets with the owning capability: `research`, `prototype`,
`socratic` (human decisions), or `to-questionnaire` (another person). One
session resolves at most one non-research ticket.

## Handoff

When open tickets are zero, fog is empty, and remaining scope is in
`Out of scope`, recommend explicit `$project-spec` and stop.

```text
decision-map → project-spec
```