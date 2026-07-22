# Skills

This repository is the governed home for first-party Agent Skills owned by the
collection maintainer. It is currently a foundation: no Skill package has yet
passed admission or been published from this repository.

The collection is intentionally composable. A useful Skill does not need to be
part of a fixed or canonical workflow to be admitted; it needs an independent,
bounded capability and trustworthy evidence.

## What belongs here

| Category | Treatment |
| --- | --- |
| First-party Skill | Authored by the owner, or substantially transformed into an owned capability with clear attribution. It may be admitted here. |
| Direct upstream Skill | Installed from its upstream source when it works without local modification. It is not copied here. |
| Modified third-party Skill | Kept in the separate source-organized `skills-3rdParty` repository only when a documented fork necessity exists. |
| Deprecated or archived source | Retained only with clear migration guidance; it is not a current installation authority. |

In particular, an unmodified third-party Skill is rejected from this repository.
For example, usable Matt Pocock Skills remain direct upstream dependencies at
[mattpocock/skills](https://github.com/mattpocock/skills), rather than local
convenience copies.

`project-workflow` is not a first-party Hub package and must not be imported.

## Repository governance

- [Maintenance contract for agents](AGENTS.md)
- [First-party Skill admission](docs/SKILL_ADMISSION.md)
- [Maintenance and documentation synchronization](docs/MAINTENANCE.md)
- [Installation policy and verification](docs/INSTALLATION.md)
- [Review policy](docs/REVIEW_POLICY.md)
- [Catalog](CATALOG.md)
- [Validated combination-example policy](docs/workflows/README.md)
- [Changelog](CHANGELOG.md)

The documents above define the repository rules. The package-level `SKILL.md`
is the authoritative behavior contract for an admitted Skill, and a required
`ATTRIBUTION.md` is the authoritative provenance record for a substantially
transformed first-party Skill.

## Installation status

No release installation command is published yet. The command forms in
[Installation](docs/INSTALLATION.md) are explicitly marked as templates until
they have been verified against a released repository and fresh installation
environment. Do not present a structural check or a template command as
runtime installation evidence.
