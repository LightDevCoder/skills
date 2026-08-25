![Light Skills — composable agent workflows](Assets/header.png)

[中文说明](README.zh-CN.md)

# Light Skills — Composable Agent Workflows

`LightDevCoder/skills` is a **first-party, general-purpose, composable Agent workflow system** — 33 small, explicit, independently discoverable Skills that combine into a complete project flow or run standalone. Each package owns its `SKILL.md` contract; this README explains the repository.

> **About:** Light Skills — Drive your creativity. Small, composable, inspectable.

> **Release:** [v0.1.6](https://github.com/LightDevCoder/skills/releases/tag/v0.1.6) is published from commit `e8c3589` (tag `v0.1.6`) and is the last published stable (9 packages). The current branch contains **33 first-party Skills** (unreleased refactor — see [CHANGELOG.md](CHANGELOG.md)). Skills are still installed with `npx skills add LightDevCoder/skills`.

## What is Light Skills

A workflow system, not a monolithic orchestrator. The repository provides composable capabilities across:

- **Project Workflow** — from initialization to release
- **Clarification & Research** — decide before you build
- **Execution** — do bounded work with host-aware routing
- **Review** — from read-only findings to project acceptance
- **Specialized Workflows** — manuscript, knowledge base, learning, kanban
- **Router** — `ask-light` recommends the next step without executing it

Architecture decides *which capabilities exist and how they compose*; Skill-writing quality follows [Matt Pocock Skills](https://github.com/mattpocock/skills), and host-aware routing follows [Sol Advisor](https://github.com/DannyMac180/sol-advisor) — both as design references, not runtime dependencies.

## Installation

```text
npx skills add LightDevCoder/skills --yes --copy --agent '*'
```

One Skill at the same revision:

```text
npx skills add LightDevCoder/skills --skill project-review --yes --copy --agent '*'
npx skills add LightDevCoder/skills --skill research --yes --copy --agent '*'
```

For the last published tag:

```text
npx skills add LightDevCoder/skills#v0.1.6 --yes --copy --agent '*'
```

Refresh the host, then confirm discovery without the source checkout. See [Installation](docs/INSTALLATION.md) for revision semantics, manual fallback, and fresh-install evidence.

## Quick Start

```text
$ask-light next        # you don't know what's next — get one recommendation and stop
$project-init          # start a new project from a minimal preset
$clarify               # vague idea → lightweight decisions, no SPEC yet
$project-clarify       # real project → inspect repo, then decide
$implement             # one clear ticket in, one verified artifact out
$project-review        # final acceptance: PASS / FAIL / BLOCKED
```

## Main workflow

The recommended project flow (not a required pipeline — enter mid-stream when appropriate):

```text
project-init
      ↓
project-clarify
      ↓
project-spec
      ↓
project-tickets
      ↓
implement
      ↓
project-review
      ↓
release-workflow
```

- `project-init` — minimum initialization from a preset; no full clarification.
- `project-clarify → project-spec → project-tickets` — clarify decisions, freeze a SPEC, slice into tracer-bullet tickets.
- `implement` — general-purpose bounded executor (code, doc, config, Skill).
- `project-review` — project-level final acceptance; `review-loop` is its convergence engine.
- Any stage may enter directly when the task is already in that state.

Small-task paths:

```text
clarify                          # standalone idea triage → stop, no SPEC
implement                        # one ready ticket → verify → review-loop when useful
diagnosing-bugs → implement      # hard bug → tight loop → fix → review
release-workflow                 # publish only
$ask-light                       # unknown entry → one recommendation
```

Full composition is in [docs/workflows/](docs/workflows/). Each `SKILL.md` stays the authority.

## When you don't know what's next

```text
$ask-light next
$ask-light workflow
```

`ask-light` is the **Light Workflow Router** — user-invoked, read-only, built last after the full map exists. It inspects goal, artifacts, blockers, project type, task kind, availability, and invocation control across the 33 first-party Skills and returns *one* recommendation (or one bounded recipe) with source, reason, and host-appropriate invocation — then stops. It never installs, executes, or chains another user-invoked Skill.

See [ask-light](skills/ask-light/SKILL.md) and [docs/workflows/](docs/workflows/).

## Representative capabilities

| Group | Skills | Entry |
| --- | --- | --- |
| **Project** | `project-init`, `project-clarify`, `project-spec`, `project-tickets`, `implement`, `project-review`, `release-workflow` | [CATALOG.md](CATALOG.md) |
| **Clarification & Research** | `socratic` (engine), `clarify`, `project-clarify`, `decision-map`, `research`, `prototype`, `to-questionnaire` | [clarification-system](docs/workflows/clarification-system.md) |
| **Execution** | `implement`, `agent-config`, `tdd`, `diagnosing-bugs`, `resolving-merge-conflicts` | [execution](docs/workflows/execution.md) |
| **Review** | `review-loop` (engine), `generic-review`, `code-review`, `project-review` (acceptance) | [review-system](docs/workflows/review-system.md) |
| **Specialized** | `manuscript-ops`, `kb-init`, `learn-anything`, `language-learning`, `kanban-worker`, `eli5`, `recap` | [specialized-workflows](docs/workflows/specialized-workflows.md) |
| **Productivity** | `handoff`, `wizard`, `wait-what`, `writing-for-agents` | [CATALOG.md](CATALOG.md) |

Full inventory — purpose, when to use, invocation, and package path for all 33 — is in [CATALOG.md](CATALOG.md). Do not duplicate full Skill contracts here.

## First-party catalog (summary)

33 admitted first-party Skills under `skills/`. Package contracts are the behavior authority.

See [CATALOG.md](CATALOG.md) for the complete table.

## Ownership and upstream boundaries

| Source state | Authority | Treatment here |
| --- | --- | --- |
| First-party | This repository and its admitted package contracts | Included under `skills/`. |
| Approved Port (Matt) | Original upstream + `ATTRIBUTION.md` + Light integration | Self-contained here; no runtime install of Matt Skills required. |
| Direct upstream (other) | Original upstream repository | Install directly; do not copy unchanged Skill here. |
| Modified third-party | Private `LightDevCoder/skills-3rdParty` | Keep provenance, patches, licenses, sync locks, evidence. |
| Deprecated / archived | Released migration record | Keep history, point to current authority. |

Approved Matt PORTs in this repo (SPEC §14): `research`, `prototype`, `tdd`, `handoff`, `diagnosing-bugs`, `wizard`, `teach`, `wait-what`, `to-questionnaire`, `writing-for-agents`, `resolving-merge-conflicts`. Each has `ATTRIBUTION.md` and no upstream runtime dependency. Light main workflow does not require `mattpocock/skills` or `sol-advisor` at runtime.

## Governance and evidence

- [Maintenance contract](AGENTS.md)
- [Skill admission](docs/SKILL_ADMISSION.md)
- [Maintenance and synchronization](docs/MAINTENANCE.md)
- [Installation and fresh-install verification](docs/INSTALLATION.md)
- [Review policy](docs/REVIEW_POLICY.md) · [Reviewer contract](docs/REVIEWER_CONTRACT.md)
- [Catalog](CATALOG.md) · [Changelog](CHANGELOG.md)
- [Workflows](docs/workflows/) — project, clarification, execution, review, specialized
- [Release receipt](docs/evidence/releases/v0.1.6/RELEASE_RECEIPT.md)
- [Collection discovery](tests/test_collection_discovery.py) · [Composition checks](tests/test_composition.py)

## Hero asset

Header image: [Assets/header.png](Assets/header.png) (first line of this README). The editable legacy header remains at `skills/docs/assets/skills-header.svg` / `.png` with manifest `skills/docs/assets/skills-header.json` for package tests.
