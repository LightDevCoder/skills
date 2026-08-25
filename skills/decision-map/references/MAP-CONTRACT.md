# Map contract

Canonical shapes for the local-markdown tracker, compatible with
`docs/agents/issue-tracker.md` Wayfinding operations.

## Map file

Path: `.scratch/<effort>/map.md`

```markdown
## Destination

<what reaching the end looks like — the spec, decision, or change this effort
is finding its way to. One or two lines; every session orients to it before
choosing a ticket.>

## Notes

<domain, skills every session should consult, standing preferences>

## Decisions so far

<!-- index — one line per closed ticket: gist + link to ticket -->

- [<closed ticket title>](issues/NN-<slug>.md) — <one-line gist of answer>

## Not yet specified

<!-- in-scope fog you cannot ticket yet; graduates as frontier advances -->

- suspected question / area to revisit

## Out of scope

<!-- work ruled beyond the destination; closed, never graduates -->

- gist + why out of scope — link to closed ticket when applicable
```

Open tickets are **not** listed here; they are the open child files under
`issues/`.

## Child ticket file

Path: `.scratch/<effort>/issues/NN-<slug>.md` (NN from `01`, zero-padded)

Header lines near the top:

- `Type: research | prototype | grilling | task`
- `Status: open | claimed | resolved`
- `Blocked by: NN, NN` (list ticket numbers that block this one; omit or empty
  when unblocked)

Body:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

On resolve, append:

```markdown
## Answer

<recorded resolution, linked assets, or context pointer>
```

## Map operations

Per `docs/agents/issue-tracker.md`:

- **Blocking**: `Blocked by: NN, NN` near the top. A ticket is **unblocked**
  when every ticket it lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are
  `open` (status `open`), unblocked, and unclaimed (not `claimed`). First by
  number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append `## Answer`, set `Status: resolved`, then append a gist
  to the map's `Decisions so far`.

Naming: always refer to tickets by title (link-wrapped) in narration and in
the map's `Decisions so far`, never by bare `NN` or id.

## Ticket types

- **research** — AFK fact: read primary sources. Use `research`.
- **prototype** — HITL experiment: cheap artifact via `prototype`.
- **grilling** — HITL conversation: default for human decisions. Use `socratic`.
- **task** — work that must happen before a decision can be made (credentials,
  provisioning, data movement). HITL or AFK. Resolved when work is done.

A research ticket may be resolved by a `research` subagent in parallel during
charting; all other types resolve at most one per session.
