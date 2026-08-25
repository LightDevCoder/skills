# Project-clarify examples

## Example 1 — Existing project, fact already answered

**Target root** has `README.md#Purpose`, `AGENTS.md`, `docs/adr/0001-storage.md`.

User: `$project-clarify We want to add offline sync to the notes app.`

**Inspection** (before asking):
- `README.md#Purpose` — "local-first notes, no cloud"
- `docs/adr/0001-storage.md` — "IndexedDB for local, no sync"
- `src/sync/` does not exist → evidence gap, not a fact.

**Socratic call**:
- Current understanding: add offline sync, existing local-first constraint.
- Open decisions: D1 sync topology (CRDT vs last-write-wins), D2 conflict UI
  (auto-merge vs prompt) — D2 depends on D1.

**Presented frontier**: D1 only, with tradeoff referencing inspected facts.

Not asked: "What storage do you currently use?" — already answered by
`docs/adr/0001-storage.md`.

## Example 2 — Empty project boundary

New repo has no `README`, `AGENTS.md`, `docs/`, or source files.

Inspection records: `Evidence not found: README, AGENTS.md, docs/adr/, source
entry points — empty project`.

Socratic uses the user-supplied brief as the only starting evidence:

```text
Project clarification handoff
- Target and inspected project facts: (none — empty project)
- Evidence not found: README, AGENTS.md, docs/adr/, source
- Current goal and constraints: brief as supplied
- Resolved user decisions: ...
```

No invented facts are added.

## Example 3 — Missing capability, retained gap

Needed fact: "Does iOS WebKit allow background sync?"
- Local inspection cannot answer; requires `research` on official WebKit docs.
- User has not authorized fact work this turn.

Ledger:
```text
Capability call: research
Question or experiment: WebKit background sync support
Blocked decision: D3 - background sync feasibility
Authorization and input: not-authorized
Call status: not-authorized
Capability outcome: none
Result read: none
```

Handoff reports `Dependencies and fact-finding gaps: WebKit background sync
→ research not-authorized; blocks D3; Current frontier: (empty - blocked)`.
Downstream D3 is not asked.

## Example 4 — Handoff to project-spec

After frontier is empty and gaps are either resolved or marked blocked,
handoff has:

```text
Recommended next explicit invocation: project-spec
Status: ready-for-next-stage
```

`project-spec` can now build a formal SPEC directly from
`Target facts`, `Resolved decisions`, `Open decisions`, and the ledger without
re-asking inspected material.

## Example 5 — Upgrade to decision-map

Goal is large: "Migrate the entire monolith to modular contexts with new
domain language and multi-session planning."

`project-clarify` resolves two immediate decisions, detects fog beyond the
frontier (domain terms unset, many dependent decisions), and returns:

```text
Recommended next explicit invocation: decision-map
Status: blocked
```

It does not try to resolve the full map itself.
