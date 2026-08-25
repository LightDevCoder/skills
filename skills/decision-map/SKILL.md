---
name: decision-map
description: Plan a large, multi-session, decision-heavy effort as a persistent decision map of tickets. Use only when the user explicitly invokes $decision-map; it maintains .scratch/<effort>/map.md and child decision tickets until fog clears, then hands off to project-spec.
disable-model-invocation: true
---

# Decision Map

`decision-map` is an **explicit, user-invoked planning stage** for foggy,
large, or multi-session work. Use it only after an explicit `$decision-map`
request. It charts the way as a shared map on the repository's local markdown
tracker, not by executing the work.

Read [MAP-CONTRACT.md](references/MAP-CONTRACT.md) before starting a run.
Examples and lifecycle are in [WORKFLOW.md](references/WORKFLOW.md) and
[EXAMPLES.md](references/EXAMPLES.md).

## When to use

- Greenfield or giant effort with many dependent decisions.
- Duration longer than one agent session.
- Mix of research, prototype, human decisions, and async input.
- The way from the current state to the destination is not yet visible.

For a small or single-session clarification, use `$project-clarify` or
`$clarify` instead.

## Core model

One **map** plus many **decision tickets**, stored as local markdown files
per [docs/agents/issue-tracker.md](../../docs/agents/issue-tracker.md)
Wayfinding operations.

```text
.scratch/<effort>/map.md              ← canonical map
.scratch/<effort>/issues/NN-<slug>.md ← child decision tickets
```

- **Map** holds `Destination`, `Notes`, `Decisions so far`, `Not yet
  specified` (fog), and `Out of scope`. It is an index, not a store — detail
  lives in tickets.
- **Ticket** holds one decision-sized question. `Type:` is `research`,
  `prototype`, `grilling` (human decision via `socratic`), or `task`.
  `Status:` is `open`, `claimed`, or `resolved`. `Blocked by: NN, ...`
  lists blocking tickets.

The map and tickets are tracker-native; they render the frontier visually in
the file layout.

See [MAP-CONTRACT.md](references/MAP-CONTRACT.md) for the exact file shapes.

## Done by decisions, not deliverables

Each ticket resolves a decision. The map is done when the way is clear —
nothing left to decide before someone goes and does the thing. Produce
decisions, not deliverables. The pull to just do the work is usually the
signal the map edge is reached and it is time to hand off to `project-spec`.

## Composition

Tickets are resolved one at a time using the right capability:

- **research** → `research` (model-invoked, can run in parallel on charting)
- **prototype** → `prototype` (model-invoked experiment)
- **grilling** (human choice) → `socratic` (model-invoked engine) + user exchange
- **task** → work that must happen before a decision can be made; agent or
  human checklist
- **holds another person** → `to-questionnaire`

Do not copy those capabilities' instructions here; call them. One session
resolves at most one ticket (except parallel `research` on charting).

## Two modes

**Chart the map** — from a loose idea:
1. Name the **destination** (the spec/decision/change this effort finds its way to).
2. Breadth-first fan out to surface the frontier and the fog.
3. Create `map.md` and the specifiable child tickets, then wire `Blocked by`
   edges in a second pass. Fire `research` tickets in parallel.
4. Stop — charting is one session's work.

**Work through the map** — from an existing map (and optional ticket):
1. Load the map. Choose the ticket — user-named or the first frontier ticket.
2. **Claim** it (`Status: claimed`) before any work so concurrent sessions skip it.
3. Resolve via the Type's capability; zoom into related tickets as needed.
4. **Resolve**: append `## Answer` to the ticket, set `Status: resolved`,
   append a gist to the map's `Decisions so far`, graduate fog that is now
   specifiable into new tickets.

Full steps in [WORKFLOW.md](references/WORKFLOW.md).

## Handoff

When the map's open tickets are zero, fog is empty, and remaining scope is in
`Out of scope`:

```text
decision-map → project-spec
```

The map's `Decisions so far`, ticket answers, and ledger are the material for
`project-spec` to build a formal SPEC without re-asking completed decisions.

Do not auto-chain to `project-spec`; recommend its explicit invocation and stop.
