# Project-tickets workflow

Supporting detail for `project-tickets`. `SKILL.md` is the entry;
`TICKET-CONTRACT.md` is the file-shape contract. This file holds the full
execution order with Light's local markdown tracker.

## Entry condition

- User explicitly invokes `$project-tickets`.
- A formal SPEC exists, normally at `.scratch/<feature>/spec.md` from
  `project-spec`. The user may pass a different spec path as the invoke
  argument.

Do not synthesize tickets from a vague conversation or an incomplete thread
without a SPEC — that case belongs to `project-spec` first.

## Steps

### 1. Gather context

- Read the supplied SPEC at its stated path. Use the spec body and its linked
  evidence (ADRs, domain glossary terms, seam sketch) as the authoritative
  source.
- When the invoke argument is a feature slug rather than a file path, resolve
  it to `.scratch/<feature>/spec.md` and confirm the resolved file exists.
- When the conversation carries a distinct parent issue, record its path but
  do not close or mutate the parent.

If the SPEC file is missing, unreadable, or lacks the sections required by
`project-spec`'s `OUTPUT-FORMAT.md`, report a handoff gap and stop — do not
invent tickets.

### 2. Explore the codebase (optional, inspect before slicing)

When the SPEC's Implementation Decisions touch source, skim the repo to:

- verify the vocabulary matches the domain glossary and ADRs;
- locate prefactoring opportunities ("make the change easy, then make the easy
  change");
- size slices so each fits in a single fresh context window.

This is bounded inspection, not a re-architecture pass. Record no file paths
or code snippets in the tickets themselves unless the reasoning exception
below applies.

### 3. Draft vertical slices with blocking edges

Break the SPEC into **tracer-bullet** tickets:

- Each slice cuts a narrow but **complete** path through every relevant layer
  (for code: schema → API → UI → tests; for a Skill/doc/configuration: the
  structure → template → render → verification boundary the SPEC names).
  The slice is demoable or verifiable on its own.
- Each slice fits in one fresh context window.
- Prefactoring is a slice that comes first when it makes later slices easy.
- Declare the graph explicitly:
  - **Blocked by** — the numbers/titles that gate this slice (those that must
    be `resolved` before this slice can start);
  - **Ready work** — tickets with no blockers or whose blockers are already
    `resolved`;
  - **Parallelizable** — tickets that share no `Blocked by` edge and touch
    disjoint ownership (they may be taken together by the frontier scanner);
  - **Verification** — what demo or check makes the slice done (see
    `TICKET-CONTRACT.md`).

**Wide-refactor exception.** A mechanical, codebase-wide change (rename,
retype) whose blast radius breaks thousands of call sites cannot be forced
into a tracer bullet. Sequence it as **expand–contract**: expand (add the new
form beside the old, CI still green), migrate call sites in batches sized by
blast radius (each batch a ticket blocked by expand, keeping CI green because
the old form persists), then contract (delete the old form, blocked by every
migrate batch). When even the batches cannot stay green alone, keep the
sequence on an integration branch and add a final `integrate-and-verify`
ticket blocked by all batches; green is promised only there.

Keep the SKILL.md concise by leaving the template,Blocking rules, lifecycle,
and wide-refactor sequencing to `TICKET-CONTRACT.md`; this step describes only
the slicing procedure.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket show:

- **Title** — short descriptive name;
- **Blocked by** — which tickets gate it (or "None — can start immediately");
- **What it delivers** — the end-to-end behaviour this slice makes work,
  from the user's perspective.

Ask the three canonical questions:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct — does each ticket only depend on tickets
  that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves. The approved graph is the one you publish;
do not reorder or rewrite it silently before publishing.

### 5. Publish the tickets to the local tracker

Publish the approved tickets in **dependency order** (blockers first) so each
ticket's `Blocked by` references resolve to real files.

- **Path**: `.scratch/<feature>/issues/<NN>-<slug>.md`, numbered from `01`,
  zero-padded. Create `.scratch/<feature>/issues/` if needed.
- **One ticket per file** — never a single combined tickets file.
- **Header lines near the top**: `**Blocked by:**` and `**Status:**` per
  `TICKET-CONTRACT.md`.
- **Template**: `TICKET-CONTRACT.md`'s local ticket template (What to build,
  Blocked by, Status, acceptance criteria).

Work the **frontier** after publishing: any ticket whose `Blocked by` set is
empty or entirely `resolved`, whose `Status` is `ready-for-agent` (or `open`
for a map-style scan), and which is not `claimed` is immediately ready work.
First by number wins; independent tickets are parallelizable.

Do not close or modify the parent SPEC or the map that supplied it.

### 6. Describe ready work and stop

Report the published paths, the blocker graph, and the current frontier
(first ready tickets, plus which are parallelizable). Recommend explicit
`implement` on the chosen ticket and stop — do not auto-invoke it.

## Wayfinding compatibility

The published layout is intentionally parseable by the Wayfinding operations
defined in `docs/agents/issue-tracker.md:21`:

- **Blocking** — `Blocked by: NN, NN` near the top. A ticket is unblocked
  when every file it lists is `resolved`.
- **Frontier** — scan `.scratch/<feature>/issues/` for `open` /
  `ready-for-agent`, unblocked, unclaimed files; first by number wins.
- **Claim** — set `Status: claimed` before any work so concurrent sessions
  skip it.
- **Resolve** — append `## Answer`, set `Status: resolved`, optionally link
  from the map's `Decisions so far` or the SPEC's evidence when applicable.

A browser that only understands the map contract's `Status: open | claimed |
resolved` must still be able to identify the frontier; see
`TICKET-CONTRACT.md` for the alias `ready-for-agent ↔ open` (unblocked,
unclaimed) and the lifecycle note.

## Non-goals

- No implementation, test execution, review, or merge is performed.
- No file paths or code snippets are embedded except the prototype-snippet
  exception noted in step 3.
- No native-tracker API calls — the local markdown file-per-ticket form is
  the primary product.
