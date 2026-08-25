# Project-spec examples

## Example 1 — Dog-food: the Planning stage itself (Issue 08)

This ticket (08 — Planning) is the dog-food handoff that `project-spec` and
`project-tickets` are designed to carry.

**Clarified input**

- `project-clarify` analogue: this issue body's `What to build` and
  `Blocked by` plus SPEC §7 / §15 / §25 Phase 5 are already clarified. The
  "interview" is complete; no new user decision is needed to write the SPEC
  for the two stages.
- `decision-map` analogue for a larger effort: the map's `Destination` would
  be "a repo-local tracker's spec owns formal SPECs and a ticket graph owns
  tracer bullets" and its `Decisions so far` would list: reference Matt
  `to-spec`/`to-tickets`, single-file-per-ticket at
  `.scratch/<feature>/issues/NN-<slug>.md`, `Blocked by:` edges compatible
  with `docs/agents/issue-tracker.md:21` Wayfinding ops, concise `SKILL.md`
  + supporting docs.

**Seam sketch (confirmed before writing)**

- Contribution is two new packages under `skills/project-spec/` and
  `skills/project-tickets/`, each with `SKILL.md`, `agents/openai.yaml`,
  `ATTRIBUTION.md`, `references/`.
- Highest verification seam: package-discovery and composition probes that
  read `SKILL.md` frontmatter and supporting-file references — no deep mock
  of ticket execution needed for the spec stage.

**Published SPEC**

Published to `.scratch/light-skills-refactor/spec.md` (the refactor effort's
canonical SPEC) or, for a scoped demo, to
`.scratch/planning-demo/spec.md` — the path recommended to `project-tickets`
is the one the run actually wrote. The SPEC contains:

- Problem Statement, Solution, User Stories (multiple actors: author, reviewer,
  agent host), Implementation Decisions (including the seam sketch and tracker
  contract), Testing/Verification Decisions, Out of Scope, Further Notes.

**Handoff**

Recommend `$project-tickets .scratch/planning-demo/spec.md` and stop. The
SPEC file at that path is the verifiable token; no automatic ticket creation
is performed.

## Example 2 — Returning to project-clarify when blocked

User: `$project-spec add offline sync to the notes app`

**Gathered material**

- `project-clarify` handoff lists: `Resolved: local-first constraint is
  intentional`; `Open: D1 sync topology = CRDT vs last-write-wins (blocked
  on user tradeoff)`; `Status: waiting-for-user`; `Capability calls:
  socratic result-read, frontier = D1`.

**Gate**

A truly blocking, user-owned decision (`D1`) remains unresolved. Writing a
SPEC would require speculating about the sync topology and its conflict
policy.

**Behaviour**

Do not write `.scratch/<feature>/spec.md`. Return:

```text
Blocking decision: D1 sync topology (CRDT vs last-write-wins) — user-owned;
blocks Implementation Decisions and the seam choice.
Context: Project clarification handoff §Open decisions and dependencies;
        notes app offline-sync thread.
Recommended next explicit invocation: $project-clarify
```

Stop after the return. The SPEC is not published and `project-tickets` is
not recommended.

## Example 3 — General-purpose (non-code) SPEC

Goal (non-code): "Turn the release notes archive into a versioned Skills
catalog with per-Skill installation evidence."

**Clarified facts** (from `project-clarify`): provenance rules for
`release-workflow`, the catalog is an inventory not a router, and the
installation evidence lives under `docs/evidence/releases/`.

**SPEC Implementation Decisions** excerpt:

- Context `docs/evidence` remains authoritative for release records; the
  catalog at `CATALOG.md` is the human-readable derived view (synchronized
  from package metadata, not authored prose).
- Verification seam: run the collection-discovery check and the per-Skill
  supporting-file reference resolver — external behaviour, not heading text.
- Schema note: no database schema; the "schema" is the markdown evidence
  record and its required fields.

Non-code verification (Testing / Verification Decisions) lists the evidence
protocol and the stale-link checks rather than a unit-test suite, but retains
the same template headings.

## Example 4 — Minimal repo, still bounded

Goal on an empty repo: "A one-page brief for the prototype's evaluation
criteria."

**Evidence after inspection**: `Evidence not found: README, docs/adr/, source
— empty project`. No domain glossary yet. The `Current goal and constraints`
in the handoff is the only authoritative brief.

**SPEC**

Still covers Problem Statement, Solution, a short but complete User Stories
list, Implementation Decisions (the brief's structure plus the single-page
constraint), Testing/Verification Decisions (how the brief will be reviewed:
readability, bounded scope, no invented claims), Out of Scope, Further Notes
(with the evidence gaps explicitly named).

No facts are invented to make the SPEC look more detailed than the evidence
supports.
