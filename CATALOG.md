# First-Party Skill Catalog

This catalog is synchronized from the five admitted package directories under
skills/. It is a human-readable inventory, not a static workflow router and
not a record of what is currently installed on any particular Agent host.

## Collection status

| Field | Value |
| --- | --- |
| Collection | Personal Skills Collection |
| Package count | 5 admitted first-party Skills |
| Current state | Local release candidate |
| Stable release | Not yet published |
| Installation authority | [docs/INSTALLATION.md](docs/INSTALLATION.md) |
| Discovery check | [tests/collection-discovery-tests.ps1](tests/collection-discovery-tests.ps1) |

No package in this table is an unmodified upstream copy. Direct upstream
dependencies and modified third-party variants are documented separately.

## Admitted Skills

### review-loop

- **Purpose:** Run a generic final-acceptance and bounded-repair loop after the
  target and acceptance source are already defined.
- **Invocation:** Model-invoked, with a supported manual entry point.
- **Package:** [skills/review-loop/](skills/review-loop/)
- **Status:** Admitted first-party; five Profiles are included.
- **Evidence:** Package contract and Profile tests under
  [skills/review-loop/tests/](skills/review-loop/tests/).
- **Installation path:** skills/review-loop/ in a host-recognized Skills root.

### project-init

- **Purpose:** Initialize a confirmed project from a minimal preset while
  preserving existing instructions and validating resulting paths.
- **Invocation:** User-invoked only.
- **Package:** [skills/project-init/](skills/project-init/)
- **Status:** Admitted first-party.
- **Evidence:** Contract and behavior tests under
  [skills/project-init/tests/](skills/project-init/tests/).
- **Installation path:** skills/project-init/ in a host-recognized Skills root.

### ask-light

- **Purpose:** Inspect the active Agent host and recommend the single most
  appropriate next Skill from current context.
- **Invocation:** User-invoked only; it never executes the recommendation.
- **Package:** [skills/ask-light/](skills/ask-light/)
- **Status:** Admitted first-party.
- **Evidence:** Contract and behavior tests under
  [skills/ask-light/tests/](skills/ask-light/tests/).
- **Installation path:** skills/ask-light/ in a host-recognized Skills root.

### learn-anything

- **Purpose:** Turn sufficiently evidenced conversations, notes, workflows, or
  other source material into reusable Agent Skill methods.
- **Invocation:** User-invoked only.
- **Package:** [skills/learn-anything/](skills/learn-anything/)
- **Status:** Admitted first-party.
- **Evidence:** [package contract](skills/learn-anything/SKILL.md), 41-test
  suite, and method/behavior evidence are preserved in the accepted package
  record.
- **Installation path:** skills/learn-anything/ in a host-recognized Skills
  root.

### manuscript-ops

- **Purpose:** Route and govern manuscript engineering from small notes through
  large, multilingual, multi-format deliverables.
- **Invocation:** Model-invoked, with a supported manual entry point.
- **Package:** [skills/manuscript-ops/](skills/manuscript-ops/)
- **Status:** Admitted first-party; generic review mechanics delegate to
  review-loop.
- **Evidence:** Package contract, manuscript boundary tests, and referenced
  templates/scripts under [skills/manuscript-ops/](skills/manuscript-ops/).
- **Installation path:** skills/manuscript-ops/ in a host-recognized Skills
  root.

## Source-state boundaries

| State | Where it belongs | Catalog treatment |
| --- | --- | --- |
| First-party | This repository | Listed above when admitted. |
| Direct upstream | Original upstream repository | Mentioned as a dependency; never copied here. |
| Modified third-party | skills-3rdParty | Listed in that repository's source catalog only after fork admission. |
| Deprecated or archived | Released migration record | Listed with replacement and migration guidance. |

See [maintenance](docs/MAINTENANCE.md) for the synchronization procedure and
[admission](docs/SKILL_ADMISSION.md) for the ownership gate.
