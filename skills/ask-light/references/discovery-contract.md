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

- A SPEC counts as active only when it is not superseded, obsolete, archived,
  deprecated, or otherwise retired (including specs under obvious archive/old
  path segments).
- Ticket completion is established only from explicit resolved statuses.
  Missing statuses or statuses outside the known unresolved/resolved
  vocabulary do **not** count as resolved.
- Acceptance counts only when the repository evidence explicitly records a
  PASS verdict. FAIL, BLOCKED, incomplete, pending, or unreadable verdicts do
  **not** count as accepted.

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