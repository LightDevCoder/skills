# Decision-map workflow

## Chart the map (from a loose idea)

1. **Name the destination.** Run a brief `socratic` exchange to pin down what
   this map is finding its way to — the spec, decision, or change. The
   destination fixes the scope and shapes every ticket.

2. **Map the frontier breadth-first.** Fan out across the whole space rather
   than diving deep on one thread. Surface open decisions and the first steps
   takeable now. **If no fog surfaces** — the way is already clear and small
   enough for one session — do not create a map; ask how the user wants to
   proceed (likely `$project-clarify` or direct `project-spec`).

3. **Create the map** (`.scratch/<effort>/map.md`) with `Destination` and
   `Notes` filled in, `Decisions so far` empty, and the dim future sketched
   into `Not yet specified`.

4. **Create specifiable tickets** as child issues
   (`.scratch/<effort>/issues/NN-<slug>.md`) with `Type:` and `Status: open`.
   Then wire `Blocked by:` edges in a second pass (tickets need numbers before
   they can reference each other). Wiring sorts them into frontier vs blocked.

5. **Fire research subagents.** For each `research` ticket, spin up a
   `research` capability in parallel, capturing findings on a throwaway branch
   or note and linking from the ticket. Leave `Not yet specified` patches that
   are not yet sharp enough to ticket as fog.

6. Stop. Charting is one session's work; it hand-resolves nothing.

## Work through the map (from an existing map)

User invokes with `effort` (path to `.scratch/<effort>/map.md` or directory)
and optionally a ticket number.

1. Load the **map** — low-resolution view, not every ticket body.
2. **Choose the ticket.** If user named one, use it. Otherwise take the first
   frontier ticket in number order. Validate it is unblocked and not claimed.
3. **Claim** it: set `Status: claimed` and save before any work, so concurrent
   sessions skip it.
4. **Resolve** it — zoom into related/closed tickets on demand; invoke the
   Type's capability:
   - `research` → `research`
   - `prototype` → `prototype`
   - `grilling` → `socratic` (+ `to-questionnaire` if the holder is another person)
   - `task` → do the work or hand the human a precise checklist
   Never resolve more than one ticket per session (except parallel `research`
   on charting).
5. **Record**: append `## Answer` to the ticket, set `Status: resolved`,
   append a gist to the map's `Decisions so far` (with title-link, not bare id).
6. **Graduate fog**: add newly-surfaced specifiable tickets (create-then-wire);
   clear each graduated patch from `Not yet specified` so it lives only as its
   new ticket. If a ticket — this one or another — now sits beyond the
   destination, rule it **Out of scope** rather than resolving it on the route
   (close it, add a line in `Out of scope` with gist + link). If the decision
   invalidates parts of the map, update or delete those tickets.

Expect concurrent sessions editing the tracker, so re-scan the frontier after
each resolve.

## Completion → handoff to project-spec

The map is complete when:

- No open tickets remain,
- `Not yet specified` is empty, and
- Remaining scope beyond destination is in `Out of scope`.

At that point the way is clear. The map's `Decisions so far` plus ticket
`## Answer` records are the material for `project-spec` to build a formal SPEC.

Recommend explicit `$project-spec` and stop. Do not auto-chain. `project-spec`
should not re-run a full clarification interview; if it does uncover a truly
blocking user decision, it returns to `$project-clarify` or this map.

