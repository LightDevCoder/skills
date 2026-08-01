# First-Party Skill Catalog

[中文目录](CATALOG.zh-CN.md)

This catalog is synchronized from the six admitted package directories under
`skills/`. It is an inventory, not a
static workflow router and not a record of what is installed on a particular
Agent host.

## Collection status

| Field | Value |
| --- | --- |
| Collection | Personal Skills Collection |
| Package count | 6 admitted first-party Skills on this branch; 5 admitted first-party Skills in stable v0.1.1 |
| Current state | `recap` passed the low-risk prompt-only fast track but remains unreleased; v0.1.1 remains installable |
| Stable release | [v0.1.1](https://github.com/LightDevCoder/skills/releases/tag/v0.1.1) |
| Installation authority | [docs/INSTALLATION.md](docs/INSTALLATION.md) |
| Discovery check | [tests/collection-discovery-tests.ps1](tests/collection-discovery-tests.ps1) |
| Evidence | [v0.1.1 release evidence](docs/evidence/releases/v0.1.1/) |

No package in this table is an unmodified upstream copy. Direct upstream
dependencies and modified third-party variants are documented separately.

## Admitted Skills

### review-loop

- **Purpose:** Run a generic final-acceptance and bounded-repair loop after the target and acceptance source are defined.
- **Invocation:** Model-invoked, with a supported manual entry point.
- **Package:** [skills/review-loop/](skills/review-loop/)
- **Status:** Admitted first-party; generic, software, specification, manuscript, and agent-skill Profiles are included.
- **Evidence:** Package and Profile tests under [skills/review-loop/tests/](skills/review-loop/tests/); user guide at [docs/skills/review-loop.md](docs/skills/review-loop.md).
- **Installation path:** `skills/review-loop/` in a host-recognized Skills root.

### project-init

- **Purpose:** Initialize a confirmed project from a minimal preset while preserving existing instructions and validating resulting paths.
- **Invocation:** User-invoked only.
- **Package:** [skills/project-init/](skills/project-init/)
- **Status:** Admitted first-party.
- **Evidence:** Contract and behavior tests under [skills/project-init/tests/](skills/project-init/tests/); user guide at [docs/skills/project-init.md](docs/skills/project-init.md).
- **Installation path:** `skills/project-init/` in a host-recognized Skills root.

### ask-light

- **Purpose:** Inspect the active Agent host and recommend one next Skill or one bounded workflow recipe from the current context.
- **Invocation:** User-invoked only; it never executes the recommendation.
- **Package:** [skills/ask-light/](skills/ask-light/)
- **Status:** Admitted first-party; supports explicit `next` and `workflow` modes.
- **Evidence:** Contract, scanner, and behavior tests under [skills/ask-light/tests/](skills/ask-light/tests/); user guide at [docs/skills/ask-light.md](docs/skills/ask-light.md).
- **Installation path:** `skills/ask-light/` in a host-recognized Skills root.

## Newly admitted Skill

### recap

- **Purpose:** Generate exactly one line summarizing the current Agent session without continuing work or changing conversation history.
- **Invocation:** User-invoked only; `$recap` is the sole entry point.
- **Package:** [skills/recap/](skills/recap/)
- **Status:** First-party admitted by prompt-only fast-track PASS; unreleased and not present in v0.1.1.
- **Evidence:** Contract and output-contract tests under [skills/recap/tests/](skills/recap/tests/), [user guide](docs/skills/recap.md), and [admission evidence](docs/evidence/admissions/recap/README.md).
- **Installation path:** `skills/recap/` in a host-recognized Skills root.

## Remaining admitted Skills

### learn-anything

- **Purpose:** Turn sufficiently evidenced conversations, notes, workflows, or source material into reusable Agent Skill methods.
- **Invocation:** User-invoked only.
- **Package:** [skills/learn-anything/](skills/learn-anything/)
- **Status:** Admitted first-party; source sufficiency and deterministic package-build boundaries are preserved.
- **Evidence:** [package contract](skills/learn-anything/SKILL.md), hook evidence, and user guide at [docs/skills/learn-anything.md](docs/skills/learn-anything.md).
- **Installation path:** `skills/learn-anything/` in a host-recognized Skills root.

### manuscript-ops

- **Purpose:** Route and govern manuscript engineering from small notes through large, multilingual, multi-format deliverables.
- **Invocation:** Model-invoked, with a supported manual entry point.
- **Package:** [skills/manuscript-ops/](skills/manuscript-ops/)
- **Status:** Admitted first-party; generic review mechanics delegate to `review-loop`.
- **Evidence:** Package contract, referenced templates/scripts, and user guide at [docs/skills/manuscript-ops.md](docs/skills/manuscript-ops.md).
- **Installation path:** `skills/manuscript-ops/` in a host-recognized Skills root.

## Source-state boundaries

| State | Where it belongs | Catalog treatment |
| --- | --- | --- |
| First-party | This repository | Listed above when admitted. |
| Direct upstream | Original upstream repository | Mentioned as a dependency; never copied here. |
| Modified third-party | `skills-3rdParty` | Listed in that private repository's source catalog after fork admission. |
| Deprecated or archived | Released migration record | Listed with replacement and migration guidance. |

See [maintenance](docs/MAINTENANCE.md) for synchronization and
[admission](docs/SKILL_ADMISSION.md) for the ownership gate.
