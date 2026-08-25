# Socratic examples

## Example 1 — Dynamic follow-up and frontier recomputation

**Initial state**
- Current understanding: user wants a CLI tool to migrate Markdown notes,
  target is local files only.
- Open decisions: `D1` output format (keeps structure vs flat), `D2` conflict
  strategy (overwrite vs skip vs prompt) — `D2` depends on `D1` because flat
  output has more name collisions.
- Frontier: `D1` only.

**Turn 1 — Ask D1**
> Q: Should the output preserve the source folder structure or flatten all
> notes into one directory? Keeping structure preserves context but needs
> longer paths; flattening needs collision handling.

**User answers**: "Keep structure."

**Update**
- Newly resolved: `D1 = keep structure`.
- Dependency `D2` unblocked — collisions less likely but still possible.
- New frontier: `D2`.

No fixed questionnaire was followed; `D2` surfaced only after `D1` settled.

## Example 2 — Fact vs decision distinction

User says: "I don't know whether the Obsidian vault uses wikilinks or
Markdown links."

- This is **not** a user decision. It is an inspectable project fact.
- Socratic records: `Dependency: vault link style → needs local inspection`.
- Does not ask user to decide the link style.
- Reports: `Dependencies and fact-finding gaps: vault link style (inspect
  README/CONTEXT.md or vault sample); blocks D3: migration mapping`.

If inspection capability is unavailable, reports `missing capability: local
inspection` and keeps `D3` out of the frontier.

## Example 3 — Converging without repeating

User answers both the frontier question and adds: "Also, we only migrate
notes updated in the last year."

Engine must:
- Mark the frontier decision as resolved.
- Update current understanding with the new constraint (time filter).
- Not re-ask the time-scope question later.
- Add a new open decision if the time filter creates one (e.g., archive vs
  drop old notes), otherwise keep frontier empty and report `Next step: done
  or authorize fact work`.

## Example 4 — Missing capability, not a fabricated decision

Needed fact: "Does the target sync support frontmatter aliases?"
- `research` would check official Obsidian docs, but is not authorized in this
  turn.
- Socratic must **not** turn this into: "Do you want to support aliases?"
- Instead: `Dependencies: alias support → research (not-authorized); blocks
  D4: alias migration strategy; Current frontier: (empty - blocked)`.
- Reports `Next step: separately authorize fact work`.

