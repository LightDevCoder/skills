# Ask-light discovery and approval contract

`ask-light` resolves three independent questions in order: project/workflow
state, logical routing, and host availability. It then waits for approval
before beginning the selected Skill.

## Layer 0 — Project/workflow state

Before routing, inspect enough local evidence to answer:

- What is this project trying to do?
- What stage is it currently in?
- What has already been completed?
- What is blocking or logically next?
- Which Light Skill best owns that next step?

Relevant evidence, when present:

```text
Git repository state
docs/agents/light-project.md
docs/agents/issue-tracker.md
AGENTS.md / CLAUDE.md
current ACTIVE SPEC
.scratch/* effort state
current tickets and their completion state
existing implementation changes
review results / acceptance state
```

Do not read the entire repository blindly. If the request is clearly standalone
(ELI5, language practice, recap, bug investigation, manuscript setup, teach),
skip project inspection and route from the Skill map.

Project-state evidence is fail-closed:

- Resolve the current/active `.scratch/<effort>` before reading effort-owned
  SPEC, tickets, or review evidence. Historical efforts are ignored.
  Multiple active efforts, or historical efforts with no reliable project-level
  pointer, fail closed as `ambiguous-current-effort` instead of guessing by
  directory order. A pointer to an explicitly historical/inactive effort while
  another effort has an active SPEC is contradictory evidence and fails closed
  as `contradictory-current-effort`; `ask-light` does not choose between the
  pointer and the active SPEC. A pointer to a missing effort stays
  `ambiguous-current-effort` and is never silently re-resolved to another
  candidate.
- A SPEC counts as active only when it is not superseded, obsolete, archived,
  deprecated, or otherwise retired (including specs under obvious archive/old
  path segments).
- Ticket completion is established only from explicit resolved statuses.
  Missing statuses or statuses outside the known unresolved/resolved
  vocabulary do **not** count as resolved.
- Review evidence comes from the canonical `project-review` durable state:
  `<projectRoot>/.project-review/` (or `.review-loop/` only when no
  `.project-review/` directory exists). The durable contract — Charter,
  `state.md`, `verdict.md` — is owned by the producer Skill; this file does not
  redefine it. `ask-light` reads the Charter `Source:` line to prove the review
  belongs to the resolved current effort (a `.scratch/<current-effort>` SPEC
  citation), then reads `verdict.md` for the conclusion:
  - Proven ownership + explicit PASS (`PASS`/`passed`, markdown emphasis
    tolerated) → accepted.
  - Proven ownership + FAIL/BLOCKED/rejected/pending → `acceptance-not-passed`.
  - Proven ownership + missing/unreadable conclusion → no acceptance claim;
    `ask-light` routes back to `project-review`, whose resume mode owns the
    recorded state. Lifecycle values such as `complete`/`done` are never
    verdicts.
  - Verdicts citing another effort → ignored for current acceptance.
  - A record whose ownership cannot be established from the Charter
    `Source:` fails closed as `review-ownership-unknown`; `ask-light` never
    infers PASS from an unowned verdict.
- A verdict applies only to the baseline revision it reviewed. After ownership
  is proven, `ask-light` also verifies the Charter's frozen
  `Source revision or identity` against the cited source paths before trusting
  any conclusion (definitions remain producer-owned):
  - Canonical durable fields are singleton fields: `Source:`,
    `Source revision or identity:`, and `Profile:` in the Charter, plus the
    software-only `Fixed point:` / `Implementation scope:` and the verdict's
    `Reviewed implementation revision:`. Each must appear exactly once — a
    missing or duplicated field (even identically duplicated, in either field
    order) is invalid durable state and fails closed as
    `review-ownership-unknown` or `review-freshness-unknown`; `ask-light`
    never reads "first value wins" from an authoritative field.
  - Every cited `.scratch` path still matching the recorded Git commit —
    including uncommitted working-tree modifications — keeps the verdict
    current; PASS stays accepted. A cited directory source is reviewed as a
    whole baseline: files appearing inside it after the revision, including
    untracked and Git-ignored ones (detected via `git ls-files --others`
    without `--exclude-standard`), count as changes to it.
  - The recorded identity is usable only when it carries exactly one
    unambiguous locally resolvable Git commit; multi-candidate values
    (invalid+valid, valid+valid, duplicated tokens, or duplicate fields) fail
    closed with no partial salvage.
  - A verified change since the recorded revision makes ANY old verdict
    non-authoritative: stage `review-stale`, routed back to `project-review`
    for a fresh review of the changed baseline. A stale FAIL does not keep
    contaminating a baseline it no longer describes.
  - Freshness checks are scoped to exactly the reviewed source paths. Changes
    to unrelated files elsewhere in the repository never invalidate a review.
  - A missing, blank, or non-Git-resolvable identity cannot prove freshness
    and fails closed as `review-freshness-unknown`; such a record is never
    treated as accepted.
- A `software`-Profile review binds its verdict to the producer-frozen
  three-field baseline whose definitions are owned by the `project-review`
  references: Charter `- Fixed point:` (immutable code-review base — exactly
  one full commit SHA), Charter `- Implementation scope:` (the reviewed
  software target as repository-relative literal paths, the machine
  projection of the approved `In scope`), and the verdict's
  `- Reviewed implementation revision:` (the final evaluated candidate).
  Once source freshness holds, `ask-light` verifies this produced baseline
  strictly; nothing is partially salvaged or reinterpreted:
  - all three identities must parse exactly (one full SHA / a valid literal
    path list). Missing, malformed, unresolvable, ambiguous, absolute,
    traversal, pathspec-magic, or wildcard scope entries reject the WHOLE
    field and fail closed as `review-freshness-unknown`.
  - the base must differ from and delimit (be an ancestor of) the reviewed
    implementation revision, and their diff must contain non-empty change
    inside the scope; otherwise fail closed.
  - inside that frozen scope the current tree must exactly match the
    reviewed implementation revision — tracked, staged, committed, untracked,
    and Git-ignored additions alike (`git diff <rev> -- <scope>` plus
    `git ls-files --others` with literal pathspecs and no
    `--exclude-standard`; Git ignore controls status presentation, not scope
    membership).
  - any in-scope drift stales ANY old verdict into
    `review-stale → project-review`; changes outside the frozen scope are
    unrelated and never invalidate it. Legacy records frozen before these
    fields existed (e.g. two-value fixed points) are an intentional break:
    they never accept and require a fresh `project-review`.
- Legacy human-facing files (`docs/agents/acceptance.md`,
  `docs/agents/review-verdict.md`, and similar) are produced by no runtime
  contract here and are **not** authoritative acceptance evidence; they cannot
  contaminate or complete the current workflow result.

## Layer A — Light Skill Map

[`light-skill-map.json`](light-skill-map.json) is the Light-owned routing and
taxonomy source. It records Skill names, families/categories, intent patterns,
task-kind aliases, and bounded workflow recipes without duplicating package
metadata or Skill workflows. Logical ranking reads this map, not accidental
words in installed `SKILL.md` bodies. Category and invocation type come from
the package’s `SKILL.md` frontmatter where the map does not state them.

The caller may supply `goal`, `artifacts`, `blockers`, `projectType`,
`taskKind`, `availability`, and `invocationControl`. Missing `goal` and
`taskKind` returns `NEED-INPUT` for routing-only calls; collection-navigation
calls do **not** require project context. Workflow mode requires the full
context because a recipe is a stronger recommendation. Supported invocation
controls are `explicit-only`, `model-callable`, and `either`; a model-callable
request is compatible only with packages whose frontmatter permits model
invocation.

## Layer B — Root discovery, availability, and provenance

`ask-light` must not rely on the caller already knowing and injecting the Light
Skill installation root. Explicit roots may be supplied, and when they are,
they are validated rather than blindly trusted. When no roots are supplied, use
the supported discovery order:

1. `LIGHT_SKILL_ROOTS` environment variable — JSON array of `{category, path}`
   records, or a path-separated list of directories.
2. Source-checkout discovery — if the current working directory or the helper’s
   repository parent contains a `skills/` directory with `*/SKILL.md` packages,
   use `skills/` as a first-party root.
3. Installed-host discovery — scan documented host Skill roots (`~/.agents/skills`,
   `~/.codex/skills`, `~/.claude/skills`, and the like) for directories that
   contain `light-skill-map.json` or a `skills/*/SKILL.md` layout. Only treat a
   root as Light first-party when it is explicitly declared Light-owned or when
   it contains the Light-owned map/manifest.

A generic host Skill root is not provenance. Only names present in the Light
Skill Map are first-party candidates; a third-party Skill installed beside Light
Skills is ignored. Availability checks only the required package contract:
readable `SKILL.md` frontmatter with `name` and `description`, host
available/unavailable sets, and readable-path boundaries. `agents/openai.yaml`
is optional UI metadata and its absence never hides a known Light Skill such as
Frozen `eli5`.

After logical selection, verify that the selected package is available and that
its local pointers resolve. Missing or unavailable packages return `BLOCKED`
without replacing the logical recommendation. Metadata, body, and reference
read counts remain observable.

## Invocation rendering and approval transition

- Codex: `$<skill>`.
- Claude Code: `/<skill>`.
- Other hosts: `Skill: <skill>` as a generic supported representation.

Repository invocation policy is authoritative: `ask-light` is user-invoked and
must not auto-invoke another user-invoked Skill. Therefore after approval:

- A **model-invoked** accepted Skill may begin in the current conversation
  where the host supports that.
- A **user-invoked** accepted Skill (the normal project-stage case: `clarify`,
  `project-init`, `project-spec`, `project-tickets`, `implement`,
  `project-clarify`, …) cannot be started by `ask-light` itself. `ask-light`
  instead renders the exact host invocation and asks the user to start it.

Do not claim a direct Codex transition for a user-invoked target unless the
host is actually observed to allow it.

## Runtime dependency and manual path

`scripts/ask_light.py` requires Python 3.9 or newer. The PowerShell launcher
detects that runtime and returns `BLOCKED` with an actionable gap when neither
`python3` nor `python` is available. A host without Python may execute Layer 0,
Layer A, and Layer B manually from this contract: use `light-skill-map.json`
for semantic routes and recipes, inspect declared first-party package roots for
availability and local pointer integrity, render the invocation for the active
host, derive description and invocation type from `SKILL.md` frontmatter,
return the result contract, and stop until the user approves execution.

## Result and approval

Next mode returns `status`, `skill`, first-party `source`, map-backed `reason`,
host invocation, confidence, at most one material alternative, gaps, read
counts, and candidates. Workflow mode adds `workflow`, `entryCondition`,
`steps`, `stoppingBoundary`, `missingDependency`, and `finalAuthority`.
Unavailable steps also explain the missing dependency in plain language.

Every recommendation result states that the recommendation phase was read-only.
After the user explicitly approves (`yes`, `可以`, `go ahead`, `do it`,
`用这个`), `ask-light` honors the accepted Skill's invocation type: it may
begin a model-invoked target where the host supports it, and it renders the
exact invocation for a user-invoked target instead of faking execution.
`ask-light` does not auto-execute before consent and does not auto-chain past
the accepted Skill.