# First-Party Maintenance and Documentation Synchronization

[中文维护说明](MAINTENANCE.zh-CN.md)

This document governs the lifecycle of admitted first-party Skills and the
documentation that makes them maintainable and installable.

## Authoritative records

Keep each fact in one authoritative location and link to it elsewhere:

| Fact | Authoritative location |
| --- | --- |
| Package behavior, triggers, invocation, inputs, outputs, and resources | The package's skills/<skill-name>/SKILL.md |
| Provenance for a substantially transformed package | The package's skills/<skill-name>/ATTRIBUTION.md |
| Human-readable collection inventory | CATALOG.md, synchronized from package metadata |
| Installation procedure and proof requirements | docs/INSTALLATION.md |
| Review trigger and verdict rules | docs/REVIEW_POLICY.md |
| Repository change history and release notes | CHANGELOG.md and the actual release record |
| Composition validation assets | docs/workflows/ and their linked evidence |

## Current synchronization baseline

The admitted collection on this branch contains exactly review-loop,
project-init, ask-light, learn-anything, manuscript-ops, recap,
language-learning, and light-kanban-worker. recap and language-learning were
admitted through the prompt-only fast track and released in v0.1.2.
light-kanban-worker is a model-invoked package with network, filesystem, and
board-state side effects, so it follows the full admission path
(`review-loop agent-skill`) and is released in v0.1.4; its v0.1.5
scheduling-boundary and first-registration identity change carries a second
`review-loop agent-skill` `PASS`. Stable v0.1.1
contained the original five admitted packages; v0.1.3 kept the v0.1.2
package set and migrated the test toolchain. The check at
[tests/test_collection_discovery.py](../tests/test_collection_discovery.py)
guards package names, metadata, catalog entries, README links, header assets,
required governance paths, and the retired orchestration boundary.

The check is structural/discovery evidence. It does not claim fresh host
installation, runtime behavior, or a public release.

## Change workflow

For every add, update, rename, deprecation, or removal:

1. Re-check the ownership boundary and reuse decision in
   [Skill admission](SKILL_ADMISSION.md).
2. Preserve the package boundary, invocation direction, and required
   attribution.
3. Classify the change as an eligible low-risk prompt-only fast track or the
   full path, then collect only the evidence required by that route.
4. Apply the review trigger in [review policy](REVIEW_POLICY.md).
5. Synchronize the README, catalog, installation guide, governance links,
   affected composition examples, discovery tests, attribution records, and
   changelog together.
6. Prepare an unreleased changelog entry. Do not claim a version, tag, or
   verified release command until the actual release gate has passed.

## Synchronization matrix

| Change | Documentation and validation that must be reviewed |
| --- | --- |
| Add | Root README, catalog, installation guide, governance references, affected validated composition examples, discovery tests, changelog, applicable attribution, fresh-install evidence, and the selected fast-track or full-path verdict. |
| Update | Package description and behavior evidence; affected catalog, installation, attribution, examples, discovery tests, compatibility evidence, and changelog. |
| Rename | Old-to-new migration guidance; all links, catalog records, installer examples, discovery tests, examples, attribution references, and changelog. |
| Deprecate | Catalog status, README guidance, replacement or migration path, installation warning, examples, discovery tests, changelog, and release notes. |
| Remove | Confirm no supported consumer requires a compatibility shim; remove stale references, preserve migration guidance where applicable, update catalog and installation surfaces, and record the removal. |

## Catalog and installation maintenance

Catalog entries must name the package's purpose, invocation type, package path,
status, installation scope, and applicable evidence. Package metadata remains
the source of truth; do not create a second static routing table.

Every release installation example must name an actual released source and
match the current catalog. Verify whole-repository and per-Skill installation
against a fresh environment, then preserve the exact command, released
revision, host, and observed discovery result in the release evidence.
Until that exists, keep command forms explicitly marked as templates.

## Upstream attribution and compatibility

An upstream source may be recommended for direct use without being copied into
this repository. A substantially transformed first-party capability must retain
the attribution and applicable notice required by the admission contract. A
package that remains a third-party modification belongs in skills-3rdParty.

Before release, review upstream attribution, licenses or notices, dependency
availability, supported host locations, installation behavior, and known
behavioral differences.

## Composition examples

Documents in docs/workflows/ are validation assets. They may demonstrate a
useful interaction or stopping boundary, but they cannot become a hidden
admission prerequisite or an automatic workflow.

## Deprecation, rollback, and release

Deprecation is explicit: mark the catalog and installation guidance, name a
replacement or state that none exists, retain migration information for the
released support period, and record it in the changelog.

If a release candidate fails verification, stop promotion and repair through
the applicable review process. Do not rewrite published history or erase
evidence. A stable release requires only admitted packages, synchronized
documentation, verified release installation commands, required review
evidence, and a real version or tag.

## Closeout record

At collection closeout, record the final repository location, released
versions/tags, verified commands, first-party catalog, direct upstream
dependencies, modified third-party distinctions, evidence, limitations, and
migration/archive guidance. Do not label structural or simulated evidence as
runtime proof.
