# Ticket contract

Canonical file shape for the tickets `project-tickets` publishes. This contract
matches the local-markdown tracker selected by `docs/agents/light-project.md`
and described in `docs/agents/issue-tracker.md`.

## Location and naming

```text
.scratch/<feature>/issues/<NN>-<slug>.md
```

- `<feature>` — the feature slug from the SPEC path used (parent directory of
  `spec.md`) or the invoke slug confirmed with the user.
- `<NN>` — zero-padded number from `01`, allocated in dependency order:
  blockers are published before the tickets that block on them. Allocation is
  by dependency order, not alphabetical convenience.
- One ticket per file — never a single combined tickets file.

## Required file template

Each file is one ticket. Use this shape (adapted from upstream
`to-tickets`'s `local-ticket-template` plus Light's `Status`/`Blocked by`
conventions):

```markdown
# <NN> — <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the
user's perspective — not a layer-by-layer implementation list.

**Blocked by:** <numbers/titles of the tickets that gate this one, or
"None — can start immediately">.

**Status:** ready-for-agent

- [ ] Acceptance criterion 1 (observable, verifiable)
- [ ] Acceptance criterion 2 (…)

## Comments

Source: <spec path or parent reference>. <One-line relation to SPEC section>.
```

Notes on the header lines:

- `**What to build:**` — a single complete slice: narrow but demoable on its
  own. For code, it cuts through schema/API/UI/tests. For a Skill/doc/config,
  it cuts through structure/template/render/verify. State the user-visible
  outcome, not internal file edits.
- `**Blocked by:**` — the parseable blocking edge. Format either:
  - `None — can start immediately`
  - `01 — <slug>, 02 — <slug>` (numbers stable because blockers published first)
  - or `Blocked by: 01, 02` — the edge parser treats both forms as the set
    `{01, 02}`.
  A ticket is **unblocked** when every file it lists is `Status: resolved`.
- `**Status:**` — initial `ready-for-agent` (the triage label for "ready work").
  The Wayfinding frontier also matches `Status: open` as an unblocked/unclaimed
  alias; see lifecycle below.

Avoid specific file paths or code snippets in the body — they decay quickly.
Exception: when a prototype snippet proved a decision more precisely than prose
(state machine, reducer, schema, type shape), inline the trimmed fragment near
the criterion it clarifies and note "from prototype".

## Lifecycle and Wayfinding operations

Per the configured `docs/agents/issue-tracker.md` contract:

| Operation | Meaning on this tracker |
|-----------|-------------------------|
| `Blocked by:` near top | The edge set. Unblocked when every listed `NN` file is `resolved`. |
| **Frontier** | Scan `.scratch/<feature>/issues/` for files that are `ready-for-agent` or `open`, unblocked, and not `claimed`; first by number wins. Independent frontier tickets are parallelizable. |
| **Claim** | Before any work, set `**Status:** claimed` and save so concurrent sessions skip it. |
| **Resolve** | Append `## Answer` with the verification pointer, set `**Status:** resolved`, and (when the effort maintains a map) append a gist+link to the map's `Decisions so far` or to the SPEC evidence section. |

Alias rule: `ready-for-agent` means "open and unclaimed" for frontier
purposes. Claiming rewrites it to `claimed`; resolving rewrites it to
`resolved`. The raw scan that checks for `Status: open` should also accept
`Status: ready-for-agent` as open.

## Acceptance criteria and verification

Acceptance criteria are checkable, external behaviour — what an observer can
confirm after the slice lands. Typical styles:

- `given <context> when <action> then <observable outcome>`;
- `--help` / discovery probe succeeds or fails as defined;
- the published artifact renders and links resolve;
- the composition handoff (`project-spec → project-tickets → implement`) is
  probe-able.

A criterion is not a line-numbered code instruction or a paragraph from the
SPEC; it is the slice's demo.

## Dependency hygiene

- A ticket's `Blocked by` lists only tickets that genuinely gate it — a
  missing genuine edge is a schedule bug; a spurious edge is a false
  sequentialization. The workflow quiz validates this.
- Ready work (`Blocked by: None — can start immediately`) should exist;
  a fully linear graph is valid but less useful — the quiz asks whether some
  tickets should be parallelizable.
- Cycles are forbidden. If a cycle is introduced during the quiz iteration,
  the workflow stops and reports it.

## Wide-refactor variant

See `WORKFLOW.md`'s wide-refactor exception (expand–contract). Its tickets
use the same file shape but the `What to build` text names the phase
(`expand`, `migrate batch <scope>`, `contract`/`integrate-and-verify`) and
the `Blocked by` edges mirror the expand→migrate→contract chain.
