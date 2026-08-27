# Ask-light discovery contract

`ask-light` resolves two independent questions in order.

## Layer A — Light Skill Map

[`light-skill-map.json`](light-skill-map.json) is the first-party routing source.
It records Light Skill names, intent patterns, task-kind aliases, and bounded
workflow recipes without duplicating package metadata or Skill workflows.
Logical ranking reads this map, not accidental words in installed `SKILL.md`
bodies. Category comes from each declared root record; description and
invocation type come from the package's `SKILL.md` frontmatter.

The caller supplies `goal`, `artifacts`, `blockers`, `projectType`, `taskKind`,
`availability`, and `invocationControl`. Missing `goal` and `taskKind` returns
`NEED-INPUT`. Workflow mode requires every context field because a recipe is a
stronger recommendation. Supported invocation controls are `explicit-only`,
`model-callable`, and `either`; a model-callable request is compatible only
with packages whose frontmatter permits model invocation.

## Layer B — Host availability and provenance

Root records must explicitly declare `category: first-party` or
`category: light-first-party`. That declaration means the root came from the
Light collection; a generic host Skill root is not trusted as provenance.
Packages whose names are absent from the Light Skill Map are ignored even when
installed beside Light Skills.

Availability checks only the required package contract: readable `SKILL.md`
frontmatter with `name` and `description`, host available/unavailable sets, and
readable-path boundaries. `agents/openai.yaml` is optional UI metadata and its
absence never hides a known Light Skill such as Frozen `eli5`.

After logical selection, the router verifies that the selected package is
available and that its local pointers resolve. Missing or unavailable packages
return `BLOCKED` without replacing the logical recommendation. Metadata, body,
and reference read counts remain observable.

## Invocation rendering

- Codex: `$<skill>`
- Claude Code: `/<skill>`
- Other hosts: `Skill: <skill>` as a generic supported representation

The router claims no host-specific behavior beyond these renderings.

## Runtime dependency and manual path

`scripts/ask_light.py` requires Python 3.9 or newer. The PowerShell launcher
detects that runtime and returns `BLOCKED` with an actionable gap when neither
`python3` nor `python` is available. A host without Python may execute Layer A
and Layer B manually from this contract: use `light-skill-map.json` only for
semantic routes and recipes, inspect declared first-party package roots for
availability and local pointer integrity, render the invocation for the active
host, derive description and invocation type from `SKILL.md` frontmatter,
return the result contract below, and stop without invoking it.

## Result and stop

Next mode returns `status`, `skill`, first-party `source`, map-backed `reason`,
host invocation, confidence, at most one material alternative, gaps, read
counts, and candidates. Workflow mode adds `workflow`, `entryCondition`,
`steps`, `stoppingBoundary`, `missingDependency`, and `finalAuthority`.
Unavailable steps also explain the missing dependency in plain language.

Every result states: `nothing was invoked, installed, or orchestrated`.
`ask-light` never executes the recommendation.
