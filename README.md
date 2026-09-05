![Light Skills — composable agent workflows](Assets/header.png)

[中文说明](README.zh-CN.md)

# Light Skills — Composable Agent Workflows

`LightDevCoder/skills` provides 34 first-party Agent Skills designed to work together across project planning, coding, and review, or run individually on demand. Each package lives in `skills/<name>/` and defines its own behavior in `SKILL.md`.

> **Release:** [v0.2.0](https://github.com/LightDevCoder/skills/releases/tag/v0.2.0) is published from the `v0.2.0` tag — the release line carries the full 34 first-party Skills (the 33-package architecture plus `humanizer`) — and is the current stable release. The exact commit is recorded in the [release receipt](docs/evidence/releases/v0.2.0/RELEASE_RECEIPT.md).

## Overview

The repository organizes capabilities into focused areas:

- **Project Workflow:** end-to-end delivery from project bootstrap to release.
- **Clarification & Research:** structured questions and primary-source investigation before building.
- **Execution:** bounded implementation tasks with profile-driven execution configuration.
- **Review:** read-only specialist checks and final project acceptance.
- **Specialized Workflows:** dedicated tooling for manuscripts, knowledge bases, language learning, and kanban boards.
- **Router:** `ask-light` inspects workspace state to suggest next steps.

Skills follow the progressive disclosure patterns of Matt Pocock Skills and the host-evidence inspection approach of Sol Advisor as design references without adding runtime dependencies.

## Installation

### Current main / latest (includes updated Agent Config)

Install the latest collection from the default branch `main`:

```bash
npx skills add LightDevCoder/skills
```

Install a single Skill from `main` (for example, the updated `agent-config` Skill):

```bash
npx skills add LightDevCoder/skills --skill agent-config
npx skills add LightDevCoder/skills --skill project-review
npx skills add LightDevCoder/skills --skill research
```

> **Note:** An unqualified repository source (`LightDevCoder/skills`) follows the default branch `main`, delivering the latest admitted features and integrations.

### Stable release snapshot (v0.2.0)

To install the reproducible historical stable release snapshot, pin the `#v0.2.0` tag:

```bash
npx skills add LightDevCoder/skills#v0.2.0
npx skills add LightDevCoder/skills#v0.2.0 --skill project-review
```

> **Note:** The `#v0.2.0` tag remains an immutable, reproducible snapshot of the v0.2.0 release line and is not modified by subsequent work on `main`.

### Target a specific Agent directly

```bash
npx skills add LightDevCoder/skills --agent claude-code
```

### Companion MCP runtime

The `agent-config` Skill uses an optional companion MCP server for host inspection and profile persistence, maintained in [LightDevCoder/agent-config](https://github.com/LightDevCoder/agent-config):

```bash
git clone https://github.com/LightDevCoder/agent-config.git
cd agent-config && npm ci && npm run build && npm install -g .
agent-config setup --check
```

See [Installation](docs/INSTALLATION.md) for advanced options (explicit agent targets, copy mode, non-interactive CI flags), manual file copying, and verification notes.

## Quick Start

```text
$ask-light next        # Suggest the next appropriate Skill from current context
$project-init          # Bootstrap project structure and tracker contracts
$clarify               # Clarify requirements through targeted questions
$project-clarify       # Clarify project decisions using repository context
$implement             # Execute a ready ticket with verification
$project-review        # Run final acceptance checks: PASS / FAIL / BLOCKED
```

## Main Workflow

A typical project progresses through these stages, though you can start directly at any stage:

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

- `project-init`: sets up tracker contracts and initial configuration.
- `project-clarify → project-spec → project-tickets`: clarifies requirements, writes the specification, and splits work into executable tickets.
- `implement`: implements one ticket at a time with automated checks.
- `project-review`: verifies quality against frozen baselines; `review-loop` handles iterative fixes.
- `release-workflow`: runs release validation, tagging, and publication.

Direct paths for common tasks:

```text
clarify                          # Standalone brainstorming and clarification
implement                        # Implement a well-defined ticket directly
diagnosing-bugs → implement      # Diagnose an issue, then apply the fix
release-workflow                 # Publish an approved release
$ask-light                       # Route unclear tasks to the right Skill
```

See [docs/workflows/](docs/workflows/) for full workflow guides.

## Finding the Right Skill

```text
$ask-light next
$ask-light workflow
```

`ask-light` is the Light workflow advisor, navigator, and router. It inspects project and workflow evidence, reasons about the best next Skill, explains why, and waits for approval before a validated host-aware transition (model-invoked targets may begin where supported; user-invoked targets fall back to rendering the exact invocation when direct Host transition is unavailable).

See [ask-light](skills/ask-light/SKILL.md) and [docs/workflows/](docs/workflows/).

## Skills Overview

| Group | Skills | Details |
| --- | --- | --- |
| **Project** | `project-init`, `project-clarify`, `project-spec`, `project-tickets`, `implement`, `project-review`, `release-workflow` | [CATALOG.md](CATALOG.md) |
| **Clarification & Research** | `socratic` (engine), `clarify`, `project-clarify`, `decision-map`, `research`, `prototype`, `to-questionnaire` | [clarification-system](docs/workflows/clarification-system.md) |
| **Execution** | `implement`, `agent-config` (primary harnesses: 9 native adapters + fallback), `tdd`, `diagnosing-bugs`, `resolving-merge-conflicts` | [execution](docs/workflows/execution.md) |
| **Review** | `review-loop` (engine), `generic-review`, `code-review`, `project-review` (acceptance) | [review-system](docs/workflows/review-system.md) |
| **Specialized** | `manuscript-ops`, `kb-init`, `learn-anything`, `language-learning`, `kanban-worker`, `eli5`, `recap` | [specialized-workflows](docs/workflows/specialized-workflows.md) |
| **Productivity** | `handoff`, `humanizer`, `wizard`, `wait-what`, `writing-for-agents` | [CATALOG.md](CATALOG.md) |

See [CATALOG.md](CATALOG.md) for full descriptions, invocation modes, and package paths.

## Provenance and Attribution

| Origin | Policy | Repository Treatment |
| --- | --- | --- |
| First-party | Collection owner authored | Maintained in `skills/<name>/`. |
| Approved Port (Matt Pocock) | Upstream behavior preserved with `ATTRIBUTION.md` | Self-contained in `skills/<name>/` without upstream runtime dependencies. |
| Third-party unmodified | External upstream | Recommended for direct installation; not duplicated here. |
| Modified third-party | Managed in private `LightDevCoder/skills-3rdParty` | Retains full patches, licenses, and sync locks. |
| Retired standalone | Consolidated into collection | Documented with migration history in release records. |

Approved Matt Ports (11 packages): `research`, `prototype`, `tdd`, `handoff`, `diagnosing-bugs`, `wizard`, `teach`, `wait-what`, `to-questionnaire`, `writing-for-agents`, `resolving-merge-conflicts`. Each package contains `ATTRIBUTION.md` and runs without external runtime dependencies.

Adapted origin (1 package): `humanizer` is a substantially transformed first-party capability based on blader/humanizer (2.11.2) with a thin Chinese adaptation layer informed by op7418/Humanizer-zh; both MIT licenses are preserved in its [ATTRIBUTION.md](skills/humanizer/ATTRIBUTION.md).

## Documentation

- [Maintenance Contract](AGENTS.md)
- [Skill Admission Policy](docs/SKILL_ADMISSION.md)
- [Maintenance and Synchronization](docs/MAINTENANCE.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Review Policy](docs/REVIEW_POLICY.md) · [Reviewer Contract](docs/REVIEWER_CONTRACT.md)
- [Catalog](CATALOG.md) · [Changelog](CHANGELOG.md)
- [Workflow Guides](docs/workflows/)
- [Release Receipt](docs/evidence/releases/v0.2.0/RELEASE_RECEIPT.md)
- [Collection Discovery Tests](tests/test_collection_discovery.py) · [Composition Tests](tests/test_composition.py)
