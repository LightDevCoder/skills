# Socratic examples

## Example 1 — Frontier round with three independent decisions

**Initial state**
- Current understanding: user wants a CLI tool to migrate Markdown notes,
  target is local files only.
- Open decisions:
  - `D1` output format (keeps structure vs flat)
  - `D2` conflict strategy (overwrite vs skip vs prompt)
  - `D3` first-version platform (macOS only vs cross-platform)
- Dependencies: `D2` depends on `D1` because flat output has more name
  collisions; `D3` is independent.
- Frontier: `D1`, `D3`.

**Turn 1 — Ask the whole frontier in one round**
> Q1 — Output format
> A. Keep the source folder structure
> B. Flatten all notes into one directory
> Recommended: A. Keeping structure preserves context and avoids most rename
> collisions for a first version.
>
> Q2 — First-version platform
> A. macOS only
> B. Cross-platform
> Recommended: A. macOS only keeps v1 small; cross-platform can follow once
> the migration shape is proven.

`D2` is **not** asked yet because it depends on `D1`.

**User answers**: `1A, 2B`

**Update**
- Newly resolved: `D1 = keep structure`, `D3 = cross-platform`.
- Dependency `D2` unblocked (collisions still possible with structure).
- New frontier: `D2`.

## Example 2 — Batch reply with qualifiers

**User reply**: `1B, 2A, 3C` or `1B; 2A, but only locally; 3C`

The engine maps answers to the correct questions, keeps the qualifier
(`but only locally`) attached to `D2`, marks `D1`/`D2`/`D3` resolved, and
recomputes the next frontier. Unanswered questions in a partial reply remain
open.

## Example 3 — Fact vs decision distinction

User says: "I don't know whether the Obsidian vault uses wikilinks or
Markdown links."

- This is **not** a user decision. It is an inspectable project fact.
- Socratic records: `Dependency: vault link style → needs local inspection`.
- Does not ask user to decide the link style.
- Reports: `Dependencies and fact-finding gaps: vault link style (inspect
  README/CONTEXT.md or vault sample); blocks D3: migration mapping`.

If inspection capability is unavailable, reports `missing capability: local
inspection` and keeps `D3` out of the frontier.

## Example 4 — Converging without repeating

User answers both frontier questions and adds: "Also, we only migrate notes
updated in the last year."

Engine must:
- Mark the resolved frontier decisions as resolved.
- Update current understanding with the new constraint (time filter).
- Not re-ask the time-scope question later.
- Add a new open decision if the time filter creates one (e.g., archive vs
  drop old notes), otherwise keep frontier empty and report `Next step: done
  or authorize fact work`.

## Example 5 — Missing capability, not a fabricated decision

Needed fact: "Does the target sync support frontmatter aliases?"
- `research` would check official Obsidian docs, but is not authorized in this
  turn.
- Socratic must **not** turn this into: "Do you want to support aliases?"
- Instead: `Dependencies: alias support → research (not-authorized); blocks
  D4: alias migration strategy; Current frontier: (empty - blocked)`.
- Reports `Next step: separately authorize fact work`.

## Example 6 — Final shared-understanding confirmation

When the frontier is empty and no dependency blocks the result, return a
concise synthesis, not a new question:

> The tool keeps the source structure, supports macOS and Windows, uses prompt
> on collisions, and only migrates notes updated in the last year. If that
> matches what you mean, this clarification is complete.

`confirmed` completes the session; a correction updates state and recomputes
the frontier.