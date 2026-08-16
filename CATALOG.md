# First-Party Skill Catalog

[中文目录](CATALOG.zh-CN.md)

This catalog is synchronized from the eight admitted package directories under
`skills/`. It is an inventory, not a
static workflow router and not a record of what is installed on a particular
Agent host.

## Collection status

| Field | Value |
| --- | --- |
| Collection | Personal Skills Collection |
| Package count | 8 admitted first-party Skills |
| Current state | Released v0.1.3; `light-kanban-worker` admitted on the current branch, v0.1.4 release pending gates |
| Stable release | [v0.1.3](https://github.com/LightDevCoder/skills/releases/tag/v0.1.3) |
| Installation authority | [docs/INSTALLATION.md](docs/INSTALLATION.md) |
| Discovery check | [tests/test_collection_discovery.py](tests/test_collection_discovery.py) |
| Evidence | [v0.1.3 release evidence](docs/evidence/releases/v0.1.3/) |

Stable `v0.1.1` contained the original five packages; v0.1.2 added `recap` and
`language-learning` for seven admitted first-party Skills; v0.1.3 kept the
same seven and migrated the test toolchain. The current branch adds
`light-kanban-worker` as the eighth admitted package.

No package in this table is an unmodified upstream copy. Direct upstream
dependencies and modified third-party variants are documented separately.

## Admitted Skills

### ask-light

- **Purpose:** Inspect the active Agent host and recommend one next Skill or one bounded workflow recipe from the current context.
- **Invocation:** User-invoked only; it never executes the recommendation.
- **Package:** [skills/ask-light/](skills/ask-light/)
- **Status:** Admitted first-party; supports explicit `next` and `workflow` modes.
- **Evidence:** Contract, scanner, and behavior tests under [skills/ask-light/tests/](skills/ask-light/tests/); user guide at [docs/skills/ask-light.md](docs/skills/ask-light.md).
- **Installation path:** `skills/ask-light/` in a host-recognized Skills root.

### language-learning

- **Purpose:** Tutor for any target language through six study modes — daily lessons, flashcards, conversation practice, grammar decoding, progress quizzes, and immersion translation.
- **Invocation:** User-invoked only.
- **Package:** [skills/language-learning/](skills/language-learning/)
- **Status:** First-party admitted by prompt-only fast-track `PASS`; released in v0.1.2.
- **Evidence:** Contract tests under [skills/language-learning/tests/](skills/language-learning/tests/), [user guide](docs/skills/language-learning.md), and [admission evidence](docs/evidence/admissions/language-learning/README.md).
- **Installation path:** `skills/language-learning/` in a host-recognized Skills root.

### learn-anything

- **Purpose:** Turn sufficiently evidenced conversations, notes, workflows, or source material into reusable Agent Skill methods.
- **Invocation:** User-invoked only.
- **Package:** [skills/learn-anything/](skills/learn-anything/)
- **Status:** Admitted first-party; source sufficiency and deterministic package-build boundaries are preserved.
- **Evidence:** [package contract](skills/learn-anything/SKILL.md), hook evidence, and user guide at [docs/skills/learn-anything.md](docs/skills/learn-anything.md).
- **Installation path:** `skills/learn-anything/` in a host-recognized Skills root.

### light-kanban-worker

- **Purpose:** Pick up and execute one Light-Kanban task per scheduled agent run, then return it for human confirmation; resumes owned in-progress work and review feedback before claiming new tasks.
- **Invocation:** Model-invoked; manual entry point is supported.
- **Package:** [skills/light-kanban-worker/](skills/light-kanban-worker/)
- **Status:** Admitted first-party through the full admission path (`review-loop agent-skill`); released in v0.1.4.
- **Evidence:** Contract and behavior tests under [skills/light-kanban-worker/tests/](skills/light-kanban-worker/tests/), [user guide](docs/skills/light-kanban-worker.md), and [admission evidence](docs/evidence/admissions/light-kanban-worker/README.md).
- **Installation path:** `skills/light-kanban-worker/` in a host-recognized Skills root.

### manuscript-ops

- **Purpose:** Route and govern manuscript engineering from small notes through large, multilingual, multi-format deliverables.
- **Invocation:** Model-invoked, with a supported manual entry point.
- **Package:** [skills/manuscript-ops/](skills/manuscript-ops/)
- **Status:** Admitted first-party; generic review mechanics delegate to `review-loop`.
- **Evidence:** Package contract, referenced templates/scripts, and user guide at [docs/skills/manuscript-ops.md](docs/skills/manuscript-ops.md).
- **Installation path:** `skills/manuscript-ops/` in a host-recognized Skills root.

### project-init

- **Purpose:** Initialize a confirmed project from a minimal preset while preserving existing instructions and validating resulting paths.
- **Invocation:** User-invoked only.
- **Package:** [skills/project-init/](skills/project-init/)
- **Status:** Admitted first-party.
- **Evidence:** Contract and behavior tests under [skills/project-init/tests/](skills/project-init/tests/); user guide at [docs/skills/project-init.md](docs/skills/project-init.md).
- **Installation path:** `skills/project-init/` in a host-recognized Skills root.

### recap

- **Purpose:** Generate exactly one line summarizing the current Agent session without continuing work or changing conversation history.
- **Invocation:** User-invoked only; `$recap` is the sole entry point.
- **Package:** [skills/recap/](skills/recap/)
- **Status:** First-party admitted by prompt-only fast-track PASS; released in v0.1.2.
- **Evidence:** Contract and output-contract tests under [skills/recap/tests/](skills/recap/tests/), [user guide](docs/skills/recap.md), and [admission evidence](docs/evidence/admissions/recap/README.md).
- **Installation path:** `skills/recap/` in a host-recognized Skills root.

### review-loop

- **Purpose:** Run a generic final-acceptance and bounded-repair loop after the target and acceptance source are defined.
- **Invocation:** Model-invoked, with a supported manual entry point.
- **Package:** [skills/review-loop/](skills/review-loop/)
- **Status:** Admitted first-party; generic, software, specification, manuscript, and agent-skill Profiles are included.
- **Evidence:** Package and Profile tests under [skills/review-loop/tests/](skills/review-loop/tests/); user guide at [docs/skills/review-loop.md](docs/skills/review-loop.md).
- **Installation path:** `skills/review-loop/` in a host-recognized Skills root.

## Source-state boundaries

| State | Where it belongs | Catalog treatment |
| --- | --- | --- |
| First-party | This repository | Listed above when admitted. |
| Direct upstream | Original upstream repository | Mentioned as a dependency; never copied here. |
| Modified third-party | `skills-3rdParty` | Listed in that private repository's source catalog after fork admission. |
| Deprecated or archived | Released migration record | Listed with replacement and migration guidance. |

See [maintenance](docs/MAINTENANCE.md) for synchronization and
[admission](docs/SKILL_ADMISSION.md) for the ownership gate.
