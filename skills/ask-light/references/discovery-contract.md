# Ask-light discovery and approval contract

`ask-light` separates deterministic facts from semantic judgment:

```text
Code establishes trustworthy facts.
Model understands the situation.
Model chooses the workflow action.
Code validates that choice.
```

`ask_light.py` is the deterministic evidence, catalog, recipe, and validation
helper. It never owns semantic routing and never emits a final Skill
recommendation. The final user-visible recommendation is assembled by the
`ask-light` model contract only after `validate_recommendation` accepts the
model's selection.

## Layer 0 — Project evidence (`--mode next`)

`next_evidence()` inspects a bounded set of real project evidence and returns
an evidence packet (`ask-light-evidence/1`) with `routingState:
needs-model-judgment`. The packet contains facts, not recommendations — it
has no Skill field anywhere:

```text
projectReadable:      whether the project root is readable
initialized:          docs/agents/light-project.md exists
projectContract:      goal/outputs/constraints status
currentEffort:        resolved effort name, resolution (current/ambiguous/
                      contradictory/none), gaps
spec:                 existence, active status, paths
tickets:              frontier classification (see below)
review:               durable review state at EVERY project stage (see below)
artifactSignals:      research candidates + classified clarification records
hardConstraints:      scoped hard facts (see below)
stage:                descriptive summary of where the current workflow sits
completed/missing:    what is already done / what is unresolved
```

The request's intent — current-workflow "what next?", explicit independent
task, new effort in an existing project, standalone task, workflow overview,
or collection navigation — is determined by the MODEL from natural language
and conversation context. No regex decides whether project evidence
participates in routing: the packet is the same for Chinese, English, and
Japanese requests.

Modes: `$ask-light next` (next-step advisor), `$ask-light workflow` (workflow
recipes), `$ask-light <category>` (collection navigation).

### Ticket frontier

Tickets are parsed with the producer contract (`project-tickets`
TICKET-CONTRACT): `Status:` and `Blocked by:` header fields.

- Buckets: `ready` (ready vocabulary — `ready-for-agent`, `open`, `ready`,
  `todo` — with every `Blocked by` reference resolved), `blocked` (declared
  blockers outstanding, or waiting statuses such as `blocked`,
  `awaiting-confirmation`, `needs-work`), `claimed` (`claimed`,
  `in-progress`), `resolved` (explicit resolved vocabulary only), and
  `unknown` (missing status, status outside the known vocabulary, or a
  `Blocked by` reference that cannot be resolved to a numbered sibling
  ticket — fail-closed).
- Convenience paths: `readyTicketPaths`, `blockedTicketPaths`,
  `claimedTicketPaths`, `resolvedTicketPaths`, `unknownTicketPaths`, plus
  `frontierReady` and `allResolved`.
- At least one ready frontier item is a strong current-workflow fact for
  `implement`; unresolved tickets with zero ready items never prove that
  implementation can proceed.

### Durable review state

Review evidence is inspected across project stages where durable review state exists.
The canonical software workflow runs `project-clarify → project-spec → project-tickets → implement → project-review`.
With an active SPEC and no tickets, the canonical next step is `project-tickets`. When an active review round,
stale review, or completed implementation acceptance exists, the review transaction provides factual evidence.

The record reports `ownership` (current/historical/unresolvable), lifecycle
`status` (INIT/READY/CRITIC/REPAIR/EVALUATE/PASS/FAIL/BLOCKED), terminal
`verdict`, `freshness` (current/stale/unknown), `profile`, `accepted`, and
`gaps`. What the review applies to (SPEC review vs implementation acceptance)
is determined by the model from the producer-owned review contract — code
does not guess it.

The durable contract — Charter, `state.md`, `verdict.md` — forms one coherent
durable review transaction owned by the producer Skill; this file does not
redefine it. `ask-light` reads the Charter `Source:` line to prove the review
belongs to the resolved current effort (a `.scratch/<current-effort>` SPEC
citation), checks that `state.md` is coherent with the Charter revision and
Profile, and determines the active or terminal review state:

- Active review state (`INIT`, `READY`, `CRITIC`, `REPAIR`, `EVALUATE`) →
  stage `project-review`; any previous verdict is non-authoritative.
- Missing, empty, or malformed `state.md`, missing/ambiguous/non-positive
  canonical fields (`Status:`, `Charter revision:`, `Profile:`, `Round:` where
  Round >= 1), Charter revision mismatch, or Profile mismatch → fail closed as
  `review-state-unknown`.
- Terminal review state (`PASS`, `FAIL`, `BLOCKED`) requires an agreeing
  `verdict.md` with complete singleton transaction identity (`Verdict:`,
  `Charter revision:`, `Profile:`, `Round:`, and software `Reviewed implementation revision:`).
  Canonical `Verdict:` is the only authoritative terminal conclusion field in durable
  `verdict.md`; aliases such as `Result:`, `Outcome:`, `Acceptance:`, `Status:`, or `State:`
  are not accepted substitutes. Accepted terminal verdict grammar is strictly closed to
  `PASS | FAIL | BLOCKED` (semantic aliases fail closed). State/Verdict conflicts,
  missing/duplicate/malformed fields, or non-canonical values fail closed as `acceptance-unknown`.
- Proven ownership + coherent PASS + fresh baseline → `accepted`.
- Proven ownership + coherent FAIL/BLOCKED + fresh baseline → `acceptance-not-passed`.
- Verdicts citing another effort → ignored for current acceptance.
- A record whose ownership cannot be established from the Charter
  `Source:` fails closed as `review-ownership-unknown`; `ask-light` never
  infers PASS from an unowned verdict.

A verdict applies only to the baseline revision it reviewed. After ownership
and state coherence are proven, `ask-light` also verifies the Charter's frozen
`Source revision or identity` against the cited source paths before trusting
any conclusion (definitions remain producer-owned):

- Canonical durable fields are singleton fields: `Charter revision:`,
  `Source:`, `Source revision or identity:`, and `Profile:` in the Charter,
  `Status:`, `Charter revision:`, `Profile:`, and `Round:` (Round >= 1) in `state.md`,
  plus `Verdict:` (strict `PASS | FAIL | BLOCKED`), `Charter revision:`, `Profile:`,
  and `Round:` (Round >= 1) in `verdict.md`, and the software-only
  `Fixed point:` / `Implementation scope:` (Charter) and `Reviewed implementation revision:`
  (Verdict). Each must appear exactly once — a missing, malformed, or duplicated field
  (even identically duplicated, in either field order) is invalid durable state and
  fails closed as `review-ownership-unknown`, `review-state-unknown`, or
  `acceptance-unknown` / `review-freshness-unknown`; `ask-light` never reads "first value wins"
  from an authoritative field.
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
  non-authoritative: stage `review-stale`. A stale FAIL does not keep
  contaminating a baseline it no longer describes.
- Freshness checks are scoped to exactly the reviewed source paths. Changes
  to unrelated files elsewhere in the repository never invalidate a review.
- A missing, blank, or non-Git-resolvable identity cannot prove freshness
  and fails closed as `review-freshness-unknown`; such a record is never
  treated as accepted.

A `software`-Profile review binds its verdict to the producer-frozen
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
  `review-stale`; changes outside the frozen scope are
  unrelated and never invalidate it. Legacy records frozen before these
  fields existed (e.g. two-value fixed points) are an intentional break:
  they never accept and require a fresh `project-review`.

- Legacy human-facing files (`docs/agents/acceptance.md`,
  `docs/agents/review-verdict.md`, and similar) are produced by no runtime
  contract here and are **not** authoritative acceptance evidence; they cannot
  contaminate or complete the current workflow result.

### Effort resolution and other fail-closed facts

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
- A SPEC with no clarification record is `initialized` stage evidence — the
  model reasons about requirement readiness; code does not pick the Skill.

### Hard constraints are scoped, not global

Deterministic problems are exposed as scoped constraints, never as global
early returns that hijack every request:

```json
{
  "type": "ambiguous-current-effort",
  "appliesTo": "current-workflow",
  "ownerSkill": "",
  "blocking": true,
  "detail": "..."
}
```

Known constraint types and their deterministic owners:

```text
uninitialized-project        owner project-init
ambiguous-current-effort     blocking, no owner (must be resolved)
contradictory-current-effort blocking, no owner (must be resolved)
active-review                owner project-review
stale-review                 owner project-review
review-state-unknown         owner project-review
review-freshness-unknown     owner project-review
review-ownership-unknown     owner project-review
acceptance-unknown           owner project-review
review-verdict-not-passed    owner project-review
ticket-state-unknown         blocking, no owner (must be resolved)
acceptance-pending           owner project-review
current-effort-accepted      non-blocking terminal fact about the current effort
```

Constraints apply ONLY to current-workflow reasoning. They never
block an explicit independent task or a standalone request (an ambiguous
effort does not block `eli5`; an uninitialized repository does not block a
standalone explanation; an accepted current effort does not block routing new
work — the accepted fact is non-blocking).

### Artifact signals are candidates, not conclusions

- `artifactSignals.research` lists `docs/research/*` document paths. Presence
  proves only that a research artifact exists — never that it is relevant,
  complete, or that requirements are clarified. The model reads relevant
  research documents when they materially affect the recommendation.
- `artifactSignals.clarification` contains classified persisted handoff
  records. A record counts only when its CONTENT resembles the
  `project-clarify` producer contract (the `Project clarification handoff`
  marker, or a recognized handoff `Status` together with a `Recommended next
  explicit invocation` field). A filename containing "clarif" alone is not
  evidence. Recognized statuses: `ready-for-next-stage`, `waiting-for-user`,
  `blocked`; anything else classifies as `unknown` and is never ready.
- `project-clarify` returns its handoff in the conversation by default and
  writes files only when the user names a destination. Absence of a persisted
  record means clarification readiness cannot be proven from filesystem
  evidence — not that clarification never happened. The current conversation
  is first-class evidence: a completed handoff in context counts; a
  user-stated clarification without a usable handoff is reported as a gap.

Relevant evidence, when present:

```text
Git repository state
docs/agents/light-project.md
docs/agents/issue-tracker.md
AGENTS.md / CLAUDE.md
current ACTIVE SPEC
.scratch/* effort state
current tickets and their frontier state
existing implementation changes
durable review transaction state
```

Do not read the entire repository blindly. If the request is clearly
standalone (ELI5, language practice, recap, bug investigation, manuscript
setup, teach), route from the catalog and conversation without deep project
inspection.

## Layer A — Skill catalog and recipes

### Catalog

`next_evidence()` embeds a compact catalog of available first-party Skills
for model candidate selection — the model never reads all 33 `SKILL.md`
files to route:

```json
{
  "name": "project-clarify",
  "description": "...",
  "family": "clarification",
  "invocationType": "user-invoked",
  "availability": "available",
  "packagePath": "..."
}
```

Frontmatter remains authoritative for `name`, `description`, and invocation
type. [`light-skill-map.json`](light-skill-map.json) remains authoritative for
collection membership, families, workflow relationships, and canonical
recipes. Its `patterns`, `precedencePatterns`, and `taskKindRoutes` are
documented candidate hints only (`routingAuthority` in the map); no final
recommendation branch may simply take the highest pattern score. Regex
ranking is not the routing authority — the map describes the collection, the
model selects.

The caller may supply `projectRoot`/`cwd` and `availability`. There is no
required `goal`/`taskKind`/`projectType` context: the model interprets the
request.

### Workflow recipes (`--mode workflow`)

`recipes_result()` publishes every canonical recipe with per-step
`expectedInput`/`expectedOutput`/`handoffArtifact`/`stopCondition`/`optional`
fields, step `availability`, `invocationType`, per-step `missingDependency`,
plus each recipe's `entryCondition`, `stoppingBoundary`, and
`finalAuthority`. The helper does NOT determine the winning recipe — that was
deterministic regex matching and is removed. The model selects the relevant
recipe semantically, anchors its entry point at the user's actual current
state (a project with an accepted SPEC is shown the remaining flow from that
state, never the full chain from `project-init`), explains optional branches,
and preserves each Skill's stopping boundary.

## Layer B — Root discovery, availability, and provenance

`ask-light` must not rely on the caller already knowing and injecting the Light
Skill installation root. Explicit roots may be supplied, and when they are,
they are validated rather than blindly trusted. When no roots are supplied, use
the supported discovery order:

1. `LIGHT_SKILL_ROOTS` environment variable — JSON array of `{category, path}`
   records, or a path-separated list of directories.
2. Source-checkout discovery — if the current working directory or the helper's
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

## Post-model selection validation (`--mode validate --skill <name> --scope <scope>`)

After the model selects one primary Skill, the choice is validated
deterministically before any user-visible `RECOMMEND` result exists:

- the selected Skill is in the Light map;
- exactly one first-party available copy exists;
- `SKILL.md` is readable and frontmatter is valid;
- host availability permits it;
- invocation metadata is compatible with `invocationControl`
  (`explicit-only`, `model-callable`, or `either`);
- package provenance is first-party;
- local pointers resolve;
- for `--scope current-workflow`, no blocking hard constraint is silently
  violated (a constraint with an `ownerSkill` different from the selection,
  or a blocking constraint without an owner, blocks the selection).

The validator never substitutes another Skill. If the model selects
`project-clarify` but it is unavailable, the result is
`status: BLOCKED`, `logicalRecommendation: project-clarify`, reason
"selected Skill unavailable" — never a silent replacement with another Skill.
Scopes `independent` and `standalone` skip the hard-constraint check (scoped
constraints bind current-workflow reasoning only).

## Implement and agent-config relationship

- `implement` = bounded executor; `agent-config` = optional execution-planning enhancement.
- When the current project has a ready implementation item, `$ask-light next` routes to `implement` (even for complex tasks; `implement` decides whether to offer `agent-config`, and the user decides whether to accept).
- Route directly to `agent-config` only when execution planning itself is the user's explicit goal (“帮我规划这个任务怎么拆 Agent”, “不同模型怎么分工”).
- `implement` remains usable when `agent-config`, model selectors, or multi-agent routing are unavailable or declined. Selection validation never blocks `implement` for lack of routing enhancements.

## Model candidate selection procedure

For semantic routing the `ask-light` contract instructs the model to:

1. Understand what the user actually wants (request scope included).
2. Read deterministic project evidence.
3. Identify 2–4 plausible Skills from compact catalog metadata.
4. Read the `SKILL.md` for those candidates.
5. Read only relevant references when needed.
6. Compare candidate preconditions against project/conversation evidence.
7. Pick one primary Skill.
8. Keep at most one meaningful alternative.
9. Send the selected Skill to deterministic validation.
10. Render the final recommendation.

Do not select a Skill before reading its contract when neighboring Skills are
materially close.

## Invocation rendering and approval transition

- Codex: `$<skill>`.
- Claude Code: `/<skill>`.
- Other hosts: `Skill: <skill>` as a generic supported representation.

After the user explicitly approves (`yes`, `可以`, `go ahead`, `do it`,
`用这个`), `ask-light` revalidates before transitioning (stale advice is never
executed): it re-runs validation against the current package state and, for
current-project recommendations, rechecks material hard project state. If
the recommendation became stale, it reports the changed state instead of
executing.

The transition itself is host-aware:

- A **model-invoked** accepted Skill may begin in the current conversation
  where the host supports that.
- A **user-invoked** accepted Skill begins itself only where genuine trusted host
  channel evidence proves explicit approved transitions are supported. The user's explicit approval
  constitutes the required authorization for that exact target, without auto-chaining past it.
  Ordinary caller- or model-supplied context data (including fields like `trustedHostChannel`,
  `_trusted_host_channel`, or `hostCapabilities`) and unproven environment variables cannot grant transition authority.
- Otherwise `ask-light` renders the exact invocation (`$<skill>` on Codex, `/<skill>` on Claude
  Code) and asks the user to start it. It does **not** fake execution, does not assume every host
  supports recursive Skill invocation, and never treats user prose, context flags, or model inference as proof of host capability.

`ask-light` does not auto-execute before consent and does not auto-chain past
the accepted Skill.

## Runtime dependency and manual path

`scripts/ask_light.py` requires Python 3.9 or newer. The PowerShell launcher
detects that runtime and returns `BLOCKED` with an actionable gap when neither
`python3` nor `python` is available. A host without Python may execute Layer 0,
Layer A, Layer B, and the validation step manually from this contract: use
`light-skill-map.json` for collection facts and recipes (candidate hints
only), inspect declared first-party package roots for availability and local
pointer integrity, reason over the evidence packet semantics, validate the
selection, render the invocation for the active host, return the result
contract, and stop until the user approves execution.

## Result and approval

The final user-visible record is assembled by the model per the `SKILL.md`
result contract: the model fills `Skill`, `Scope` (`current-workflow` | `independent` | `standalone`),
`Reason`, `Alternative`, and `Assessment` from its own reasoning over evidence and candidate contracts;
deterministic validation fills/validates `Source`, `Invocation`, availability,
invocation type, and provenance. A `RECOMMEND` result must always contain a
real recommended Skill unless the project is legitimately terminal — an empty
`Skill:` inside `RECOMMEND` is a contract violation. Unavailable steps in
workflow mode explain the missing dependency in plain language.

Every recommendation result states that the recommendation phase was
read-only. After approval the host-aware, revalidating transition above
applies.
