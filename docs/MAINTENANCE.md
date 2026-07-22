# First-Party Maintenance and Documentation Synchronization

This document governs the lifecycle of admitted first-party Skills and the
repository documentation that makes them maintainable and installable.

## Authoritative records

Keep each fact in one authoritative location and link to it elsewhere:

| Fact | Authoritative location |
| --- | --- |
| Package behavior, trigger branches, invocation type, inputs, outputs, and resources | The package's `skills/<skill-name>/SKILL.md` |
| Provenance for a substantially transformed first-party package | The package's `skills/<skill-name>/ATTRIBUTION.md` |
| Human-readable collection inventory | `CATALOG.md`, synchronized from package metadata |
| Installation procedure and proof requirements | `docs/INSTALLATION.md` |
| Review trigger and verdict rules | `docs/REVIEW_POLICY.md` |
| Repository change history and release notes | `CHANGELOG.md` and the actual release record |

Do not maintain a second route table, duplicate package contract, or copied
upstream `SKILL.md` merely to make documentation convenient.

## Change workflow

For every add, update, rename, deprecation, or removal:

1. Classify the change and re-check the ownership boundary and reuse decision
   in [admission](SKILL_ADMISSION.md).
2. Update the package contract and justified resources together. Preserve or
   update `ATTRIBUTION.md` if a transformed upstream source is involved.
3. Collect the structural, fresh-install, behavioral, invocation, and script
   evidence required by admission. Run compatibility checks for affected hosts,
   dependencies, package resources, and documented installation paths.
4. Apply the review trigger in [review policy](REVIEW_POLICY.md). A Producer
   makes repairs; independent reviewers remain read-only.
5. Synchronize every affected documentation surface in the matrix below,
   regenerate catalog content from authoritative metadata when generation is
   available, and verify the resulting links and commands.
6. Prepare an unreleased changelog entry. Do not claim a version, tag, or
   verified release command until the actual release gate has passed.

## Synchronization matrix

| Change | Documentation and validation that must be reviewed |
| --- | --- |
| Add | Root README, catalog, installation guide, governance references, validated combination examples, `ask-light` discovery tests, changelog, attribution, and fresh-install evidence. |
| Update | Package description and behavior evidence; affected catalog, installation, attribution, examples, discovery tests, compatibility evidence, and changelog. |
| Rename | Old-to-new migration guidance; all links, catalog records, installer examples, discovery tests, examples, attribution references, and changelog. |
| Deprecate | Catalog status, README guidance, replacement or migration path, installation warning, examples, discovery tests, changelog, and release notes. |
| Remove | Confirm no supported consumer requires a compatibility shim; remove stale references, preserve migration guidance where applicable, update catalog and installation surfaces, and record the removal. |

A documented combination is an example and validation asset. It cannot become
a hidden prerequisite for admission, and it must be reviewed only when an
affected Skill or interaction changes.

## Catalog and installation maintenance

Catalog data should be generated from package metadata where practical, so
package names, purposes, invocation types, and installation paths are not
manually duplicated. If a generator is introduced later, its source metadata,
generation command, and output verification become part of the change evidence;
do not invent a generator command before one exists.

Every installation example must name an actual released source and match the
current catalog. Verify whole-repository and per-Skill installation against a
fresh environment, then preserve the exact command, released revision, host,
and observed discovery result. See [installation](INSTALLATION.md).

## Upstream attribution and compatibility

An upstream source may be recommended for direct use without being copied into
this repository. A substantially transformed first-party capability must retain
the attribution and applicable notice described in `ATTRIBUTION.md`; a package
that remains a third-party modification belongs in `skills-3rdParty`.

Before release, review upstream attribution, licenses or notices, dependency
availability, supported host locations, installation behavior, and any known
behavioral differences. If an upstream change removes the reason for a local
variant, evaluate migration or removal rather than preserving a convenience
fork.

## Deprecation, rollback, and release

Deprecation is explicit: mark the catalog and installation guidance, name a
replacement or state that none exists, retain migration information for the
released support period, and record it in the changelog.

If a release candidate fails verification, stop promotion and repair through
the applicable review process. Do not rewrite published history or erase
evidence. A rollback must identify the affected released revision, preserve the
audit trail, restore a previously verified state or publish a corrective
release, and update installation and migration guidance.

A stable release requires, at minimum:

- only admitted first-party packages;
- synchronized README, catalog, installation guide, governance links, examples,
  attribution, and release notes;
- verified installation commands against the actual remote release;
- required behavioral, script, and independent review evidence; and
- a real version or tag recorded with known limitations.

## Closeout record

At program or collection closeout, record the final repository location,
released versions or tags, verified installation commands, first-party catalog,
direct upstream dependencies, modified third-party distinctions, test and
review evidence, known limitations, and any migration or archive guidance.
No closeout statement may label structural or simulated evidence as runtime
proof.
