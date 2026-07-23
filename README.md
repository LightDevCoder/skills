![Personal Skills Collection — composable first-party Agent Skills](skills/docs/assets/skills-header.png)

# Personal Skills Collection

This repository is the governed home for five first-party Agent Skills:
bounded capabilities that can be installed independently, inspected before
use, and composed dynamically for different tasks.

> **Release status:** Stable v0.1.0 is published at
> [LightDevCoder/skills](https://github.com/LightDevCoder/skills/releases/tag/v0.1.0).
> See [installation](docs/INSTALLATION.md) for the verified whole-collection
> and per-Skill commands.

## First-party catalog

| Skill | Purpose | Invocation | Package |
| --- | --- | --- | --- |
| [review-loop](skills/review-loop/SKILL.md) | Run bounded evidence, repair, and final-acceptance loops. | Model-invoked; manual entry point is also supported. | skills/review-loop/ |
| [project-init](skills/project-init/SKILL.md) | Initialize a confirmed software, manuscript, research, knowledge, data, or Skill-development project preset. | User-invoked only. | skills/project-init/ |
| [ask-light](skills/ask-light/SKILL.md) | Inspect the active host and recommend one appropriate next Skill without executing it. | User-invoked only. | skills/ask-light/ |
| [learn-anything](skills/learn-anything/SKILL.md) | Distill sufficiently evidenced source material into reusable Agent Skill methods. | User-invoked only. | skills/learn-anything/ |
| [manuscript-ops](skills/manuscript-ops/SKILL.md) | Govern reproducible manuscript engineering across formats, batches, reviews, and handoffs. | Model-invoked; manual entry point is also supported. | skills/manuscript-ops/ |

The human-readable inventory, including status and evidence links, is
maintained in [CATALOG.md](CATALOG.md). Package-level SKILL.md files remain
the source of truth for behavior, triggers, inputs, outputs, and resources.

## Installation and discovery

Read [Installation](docs/INSTALLATION.md) before copying or installing a
package. It distinguishes project-local, user/global, and per-Skill scopes,
documents the verified v0.1.0 commands, and retains the manual fallback.

The [collection discovery test](tests/collection-discovery-tests.ps1) checks
that package metadata, catalog entries, README links, and the retired-package
boundary stay synchronized. It is a structural/discovery check, not a
substitute for fresh host installation or behavioral evidence.

## Composition without a fixed workflow

The collection is intentionally composable rather than a canonical pipeline.
The [validated composition examples](docs/workflows/README.md) show useful
handoffs and stopping boundaries. They are documentation and validation
assets, not admission requirements and not automatic orchestration rules.

For example, ask-light can recommend project-init, learn-anything,
manuscript-ops, or review-loop from the current task state, but it never
invokes the recommendation. The user chooses the next explicit entry point.

## Ownership and upstream boundaries

| Source state | Authority | Treatment here |
| --- | --- | --- |
| First-party | This repository and the admitted package contract | Included under skills/. |
| Direct upstream | The original upstream repository | Install directly; do not copy an unchanged Skill here. |
| Modified third-party | The separate skills-3rdParty repository | Requires a concrete fork reason, provenance, license, patch, and installation records. |
| Deprecated or archived | The released migration record | Keep only with explicit replacement and migration guidance. |

Direct-use Matt Pocock Skills remain upstream at
[mattpocock/skills](https://github.com/mattpocock/skills). This repository does
not copy them for convenience. project-workflow is retired and excluded; it
is not a package or compatibility dependency here.

## Governance

- [Maintenance contract for agents](AGENTS.md)
- [First-party Skill admission](docs/SKILL_ADMISSION.md)
- [Maintenance and documentation synchronization](docs/MAINTENANCE.md)
- [Installation and fresh-install verification](docs/INSTALLATION.md)
- [Review policy](docs/REVIEW_POLICY.md)
- [Catalog](CATALOG.md)
- [Validated composition examples](docs/workflows/README.md)
- [Changelog](CHANGELOG.md)
