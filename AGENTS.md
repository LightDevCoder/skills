# First-Party Skills Repository Maintenance Contract

This file routes maintenance work in this repository. Detailed requirements
live in the linked governance documents; do not duplicate their rules into
individual Skill packages or project instructions.

## Ownership boundary

The repository may contain only:

- Skills authored by the collection owner; or
- Skills substantially transformed into an owned first-party capability, with
  clear attribution and any required notice or license preservation.

Do not import an unmodified upstream or other third-party Skill for
convenience. Recommend direct upstream installation when it already satisfies
the need. If local modification, compatibility work, repackaging, deliberate
version stabilization, or a behaviorally different variant is genuinely
needed, evaluate it for the separate `skills-3rdParty` repository instead.

`project-workflow` is excluded from this repository. Do not add a compatibility
shim, dependency, or package bearing that name unless a separately approved
change establishes a real external-consumer need.

## Repository shape and sources of truth

Future admitted packages live at `skills/<skill-name>/`. Each package owns its
`SKILL.md` behavior contract and may include only justified resources, scripts,
templates, or assets. Do not create empty resource directories or placeholder
content.

For a substantially transformed first-party Skill, `skills/<skill-name>/ATTRIBUTION.md`
is the single provenance record. It must identify the original source, path,
pinned revision or tag, relevant license or notice, and the substantive local
transformation. Do not claim original authorship for unmodified material.

Repository-level responsibilities are owned by these documents:

- [Admission and evidence](docs/SKILL_ADMISSION.md)
- [Maintenance, catalog, documentation, release, and closeout](docs/MAINTENANCE.md)
- [Installation and fresh-install verification](docs/INSTALLATION.md)
- [Review triggers, profiles, evidence, and verdict ownership](docs/REVIEW_POLICY.md)

`CATALOG.md` is the human-readable inventory, derived from admitted package
metadata. `CHANGELOG.md` records unreleased and released repository changes.
Validated workflow documents are examples and test assets only; they are never
admission gates or a required orchestration architecture.

## Invocation direction

Every package must declare and test one invocation type:

- **User-invoked:** a manually selected entry point or orchestration boundary.
- **Model-invoked:** a reusable capability that can be called by the model or
  another Skill.

A user-invoked Skill must not automatically invoke another user-invoked Skill.
It may recommend the next user-invoked Skill and stop, and it may call a
model-invoked capability when the package contract permits it.

## Lifecycle work

For a create, update, rename, deprecation, or removal request:

1. Apply the reuse-before-invention decision order in
   [Skill admission](docs/SKILL_ADMISSION.md).
2. Preserve the package boundary, invocation direction, and required source
   attribution.
3. Collect the evidence appropriate to the change; structure alone is never
   behavioral or installation proof.
4. Follow the review trigger and final-verdict rules in
   [Review policy](docs/REVIEW_POLICY.md).
5. Perform every affected documentation and catalog update in the maintenance
   synchronization matrix before release.

Do not silently rename, remove, or deprecate a Skill. Preserve a migration
path, update discovery and installation surfaces, and record the change in the
changelog and release notes.

## Validation and review

Classify each Skill admission under [Skill admission](docs/SKILL_ADMISSION.md).
An eligible low-risk prompt-only Skill uses the documented fast track: bounded
structural/install/contract/invocation evidence and one fresh independent
Evaluator, without a separate Critic or Standards/Spec `code-review`. All
other new or significant Skill changes use the full evidence path. New or
changed runtime executable scripts additionally require focused automated and
negative tests, adversarial or mutation fixtures where appropriate, and
`code-review` evidence. A zero-assertion or no-op test run is not a passing
result.

Use one fresh Evaluator for an eligible fast-track Skill. Use `review-loop`
with the `agent-skill` Profile when the full policy requires it;
`review-loop` then owns the final `PASS`, `FAIL`, or `BLOCKED` verdict.
Specialist reviewers provide evidence and findings, not a competing acceptance
decision.

## Installation, release, and closeout

Do not publish an installation command as verified until it has succeeded
against the actual released repository in a fresh environment. Keep a manual
fallback and record host discovery results as required by
[Installation](docs/INSTALLATION.md).

Before a stable release, synchronize the README, catalog, installation guide,
governance references, validated examples, discovery tests, changelog, and
attribution records. The release and closeout record must distinguish
first-party, direct upstream, modified third-party, and deprecated or archived
sources; include actual release identifiers, verified commands, evidence,
limitations, and migration state. Follow the full sequence in
[Maintenance](docs/MAINTENANCE.md).
