---
name: ask-light
description: Inspect the first-party Skills available to the active Agent host and recommend either one appropriate next Skill or one bounded workflow recipe from the current goal, artifacts, blockers, project type, task kind, availability, and invocation control. Use only when the user explicitly invokes $ask-light; it reports a recommendation and never executes, installs, or orchestrates it.
disable-model-invocation: true
---

# Ask Light

`ask-light` is the **Light Workflow Router** — a user-invoked, read-only
router built last, after the first-party Skill map exists. It answers "which
installed first-party Skill is the best next fit?" from the active host and
project state. It does not replace project discovery, specification,
implementation, or final acceptance. It never reimplements the capabilities it
routes to.

## Invocation and safety boundary

Run only after an explicit `$ask-light` request. Do not run a recommended
Skill, call a Skill, launch a sub-agent, install a package, edit a project, or
create workflow state. Print the host-appropriate invocation and stop.

The deterministic scanner in [ask-light.ps1](scripts/ask-light.ps1) is an
optional read-only aid for hosts that can run PowerShell. Use `$ask-light next`
for one next Skill, or `$ask-light workflow` for one bounded recipe. On hosts
that cannot run the script, follow [discovery-contract.md](references/discovery-contract.md)
manually.

## Required input context

Understand current intent, project context, existing artifacts, available
first-party Skills, current project stage, specialized workflow, and host
capabilities before routing. Collect what is known; do not invent missing
facts. The context fields are defined in
[discovery-contract.md](references/discovery-contract.md).

## Typical routing

`ask-light` routes; it does not reimplement. Apply this map and the project's
actual stage:

```text
vague idea                                    → clarify
existing project + unclear requirements       → project-clarify
large / foggy / multi-session project         → decision-map
missing external fact                         → research
need experiment to decide                     → prototype
information held by another person            → to-questionnaire
SPEC exists (needs slicing)                   → project-tickets
ticket is ready (and unblocked)               → implement
hard bug / regression / performance issue     → diagnosing-bugs
implementation complete (needs acceptance)    → project-review (via review-loop)
ready to publish / release                    → release-workflow
previous explanation did not land             → wait-what
```

Specialized workflows (`manuscript-ops`, `kb-init`, `learn-anything`,
`kanban-worker`) and reusable capabilities (`socratic`, `agent-config`,
`generic-review`, `code-review`, `tdd`, `handoff`, `wizard`, `teach`,
`writing-for-agents`, `resolving-merge-conflicts`) remain independent. Route
to them when their entry condition is the best fit.

## Workflow mode

`$ask-light workflow` returns one bounded recipe recommendation, not an
orchestration engine. It includes each step's Skill, invocation type, expected
input/output, handoff artifact, stop condition, optional flag, and missing
dependency. It never invokes, installs, edits, creates a permanent state
machine, or silently chains user-invoked Skills. Recipe details are in
[discovery-contract.md](references/discovery-contract.md).

When no reliable recipe exists, return `NEED-INPUT`; when a required first-party
Skill is not visible/readable, return `BLOCKED` with an accurate availability
gap.

## Source and host rules

Route only among real first-party Light Skills visible to the active host.
Project/global installation roots are locations where first-party Skills live,
not competing capability sources. Upstream, modified third-party, and private
`skills-3rdParty` packages are not eligible for recommendation. A missing or
unreadable candidate gets a manual-install fallback: restore a readable
first-party package containing `SKILL.md`, refresh the host, and re-run
`$ask-light`.

## Result contract

Return a compact record with these fields:

```text
Mode: next | workflow
Status: RECOMMEND | NEED-INPUT | BLOCKED
Skill: <one name, or none>
Source: first-party: <resolved package path>
Reason: <context-specific evidence, not a generic description>
Invocation: <host-specific command or picker action>
Confidence: high | medium | low
Alternative: <at most one, only for a material tie>
Gaps: <missing/unreadable metadata and actionable guidance>
Reads: metadata=<count>; bodies=<count>; references=<count>
Execution: recommendation only; nothing was invoked or installed
```

Workflow mode additionally returns `workflow`, `entryCondition`, `steps`,
`stoppingBoundary`, and `finalAuthority`. For a recipe that reaches acceptance,
`finalAuthority` is `project-review`; `ask-light` only reports the recipe and
stops.

## Verification

Run the package contract and behavior tests. They exercise fresh disposable
first-party catalogs, duplicate names, large catalogs with shortlist-bounded
body reads, unavailable metadata, context-based ranking, workflow recipes,
explicit-only `learn-anything`, genuine ambiguity, installation guidance, and
the no-execution boundary.