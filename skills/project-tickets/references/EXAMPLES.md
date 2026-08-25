# Project-tickets examples

## Example 1 — Dog-food: slicing this Planning SPEC (Issue 08)

This ticket (08) is itself the dog-food "SPEC → tickets" input that
`project-tickets` consumes. Assume `project-spec` has published the verified
SPEC to `.scratch/planning-demo/spec.md` with the Implementation Decisions
from the issue body.

**Quiz presented to the user**

> **Ticket 01 — Project-spec entry and contract**
> Blocked by: None — can start immediately
> What it delivers: a concise user-invoked `$project-spec` entry that turns
> `project-clarify`/`decision-map` outputs into a bounded SPEC at
> `.scratch/<feature>/spec.md`, returns to `project-clarify` when blocked,
> and exposes a verifiable handoff.
>
> **Ticket 02 — Project-tickets entry and publishing**
> Blocked by: 01 — Project-spec entry and contract
> What it delivers: a concise user-invoked `$project-tickets` entry that
> slices a verified SPEC into numbered tracer-bullet tickets under
> `.scratch/<feature>/issues/` with `Blocked by`/`Status` edges compatible
> with Wayfinding ops.
>
> Parallelizable after 01? No — 02 consumes 01's template/contract shapes, so
> the quiz keeps the edge.

User approves granularity and edges. Publish in dependency order under
`.scratch/planning-demo/issues/`:

```markdown
# 01 — Project-spec entry and contract

**What to build:** A `$project-spec` Skill that synthesizes the
project-clarify handoff or decision-map answers into a formal SPEC at
.scratch/<feature>/spec.md without reopening an interview, with a blocking
return to project-clarify when a user decision remains.

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

- [ ] Takes a spec at .scratch/<feature>/spec.md's material from a
      project-clarify handoff or map without re-asking settled facts
- [ ] Blocking user decision returns to project-clarify rather than
      speculating
- [ ] Published spec satisfies OUTPUT-FORMAT.md and is the verifiable handoff

# 02 — Project-tickets entry and publishing

**What to build:** A `$project-tickets` Skill that slices the verified SPEC
into one-file-per-ticket issues at .scratch/<feature>/issues/NN-<slug>.md,
with a dependency quiz and a Wayfinding-compatible frontier.

**Blocked by:** 01 — Project-spec entry and contract

**Status:** ready-for-agent

- [ ] Takes the verified .scratch/<feature>/spec.md as input and drafts
      tracer bullets with Blocked by / ready work / parallelizable
- [ ] Presents title / Blocked by / What it delivers per ticket and iterates
      until approved
- [ ] Published files numbered 01.. in dependency order, one per file, with
      parseable Status / Blocked by for Frontier / Claim / Resolve
```

Frontier before work is `01` (the only ready ticket); first by number wins.

## Example 2 — Three-slice tracer bullets (feature with blocked work)

SPEC: "Add keyword search to the catalog at CATALOG.md with discovery and
installation guidance."

**Approved breakdown**

- **01 — Catalog search index** — Blocked by: None — delivers a file-based
  search index over `skills/*/SKILL.md` frontmatter, demoable via a small
  discovery probe.
- **02 — Query UI** — Blocked by: 01 — delivers the query surface that reads
  the index and renders results; verifiable by running the probe against a
  known skill.
- **03 — Installation guidance** — Blocked by: 01 — delivers the installation
  copy-pastes that are verified against a fresh environment, not the index UI.

`02` and `03` share an edge only to `01`; they are independent after `01`
resolves, so they are parallelizable — the frontier after `01` resolves is
`02, 03` and a dual-agent host may claim one each up to its cap.

## Example 3 — Wide refactor (expand–contract)

SPEC: "Rename `lightKanbanWorker` → `kanbanWorker` across the repo and
release artifacts."

A single vertical slice cannot land green — the rename fans across the whole
codebase.

**Approved graph**

- **01 — Expand** — Blocked by: None — add `kanbanWorker` export alongside
  `lightKanbanWorker`; CI remains green.
- **02 — Migrate docs/** — Blocked by: 01
- **03 — Migrate skills/** — Blocked by: 01
- **04 — Migrate tests/fixtures** — Blocked by: 01
- **05 — Contract** — Blocked by: 02, 03, 04 — delete `lightKanbanWorker`
  after no caller remains.
- **04 and 02, 03** are parallelizable (disjoint ownership).

When even the migrate batches cannot stay green alone, they share an
integration branch and a final `06 — integrate-and-verify` ticket blocked by
`02,03,04` is the only place green is promised.

## Example 4 — Frontier, Claim, and Resolve on the local tracker

From Example 1, `.scratch/planning-demo/issues/01-*` is `ready-for-agent` and
unblocked → frontier is `01`:

```bash
ls .scratch/planning-demo/issues/
# 01-project-spec-entry-and-contract.md  02-project-tickets-entry-and-publishing.md
```

Before work, Claim:

```markdown
**Status:** claimed
```

After work, Resolve:

```markdown
## Answer

SPEC published and verified; quiz loop iterated twice.

**Status:** resolved
```

Append a gist to the map's `Decisions so far` when this effort maintains a
map, or to the SPEC evidence section otherwise. Frontier now advances to `02`.

## Example 5 — Rejected input: no SPEC

User: `$project-tickets turn the brainstorming chat into tickets`

No `.scratch/<feature>/spec.md` exists and the conversation carries no bounded
SPEC sections.

Behaviour: report the handoff gap:

```text
No verifiable SPEC found at .scratch/<feature>/spec.md — cannot slice
without the Problem Statement / Solution / User Stories / Implementation
Decisions shape from project-spec. Recommended: $project-spec first.
```

Stop without publishing. Producing tickets speculatively would reintroduce the
interview this stage is designed to avoid.
