# First-Party Skills Repository Maintenance Contract

> Local workspace tracker: `.scratch/light-skills-lean-refactor/` — see `docs/agents/issue-tracker.md`. This note is local-only and does not alter the maintenance contract below.

This file routes maintenance work in this repository. Detailed requirements live in the linked governance documents; do not duplicate their rules into individual Skill packages or project instructions.

## Ownership boundary

The repository may contain only:

- Skills authored by the collection owner; or
- Skills substantially transformed into an owned first-party capability, with clear attribution and any required notice or license preservation.

Do not import an unmodified upstream or other third-party Skill for convenience. Recommend direct upstream installation when it already satisfies the need. If local modification, compatibility work, repackaging, deliberate version stabilization, or a behaviorally different variant is genuinely needed, evaluate it for the separate `skills-3rdParty` repository instead.

Approved architecture-level PORTs (SPEC §14/§16 — `research`, `prototype`, `tdd`, `handoff`, `diagnosing-bugs`, `wizard`, `teach`, `wait-what`, `to-questionnaire`, `writing-for-agents`, `resolving-merge-conflicts`) are the exception: they are self-contained first-party packages with `ATTRIBUTION.md` and no upstream runtime dependency.

`project-workflow` is excluded. Do not add a compatibility shim, dependency, or package bearing that name unless a separately approved change establishes a real external-consumer need.

## Repository shape and sources of truth

Future admitted packages live at `skills/<skill-name>/`. Each package owns its `SKILL.md` behavior contract and may include only justified resources, scripts, templates, or assets. Do not create empty resource directories or placeholder content.

For a substantially transformed Port, `skills/<skill-name>/ATTRIBUTION.md` is the single provenance record (source, path, pinned revision/tag, license/notice, Light-specific changes). Do not claim original authorship for unmodified material.

Repository-level responsibilities are owned by these documents:

- [Admission and evidence](docs/SKILL_ADMISSION.md)
- [Maintenance, catalog, documentation, release, and closeout](docs/MAINTENANCE.md)
- [Installation and fresh-install verification](docs/INSTALLATION.md)
- [Review triggers, profiles, evidence, and verdict ownership](docs/REVIEW_POLICY.md) · [Reviewer contract](docs/REVIEWER_CONTRACT.md)

`CATALOG.md` is the human-readable inventory, derived from admitted package metadata. `CHANGELOG.md` records unreleased and released changes. Validated workflow documents are examples and test assets only; never admission gates or a required orchestration architecture.

## Authoritative references and maintenance rules

Long-lived rules for every Agent maintaining this repository:

1. **Matt Pocock Skills** is the primary Skill-writing reference (concise entry, supporting-file progressive disclosure, composition).
2. **Sol Advisor** is the primary design reference for `agent-config` (separates setup from runtime planning; uses setup only for companion/bootstrap/Profile preparation or repair; uses normal `agent-config` for execution planning; does not silently enter setup or mutate Host configuration; treats single-model and multi-model as peer first-class modes; uses user-confirmed Profiles; does not infer model intelligence from model names; relies on real Host evidence; treats unknown capability as unconfirmed; resolves abstract reasoning policies to actual Host-supported values; preserves unrelated Host configuration; uses optional companion MCP for persistence and Host mutation while remaining usable in plan-only mode; does not own formal ticket decomposition, implementation, review convergence, or final acceptance; requires explicit approval before configuration mutation).
3. Inspect the relevant upstream/reference Skill before modifying a derived Skill.
4. Do not rewrite mature Light Skills (`manuscript-ops`, `kb-init`, `learn-anything`, `language-learning`, `kanban-worker`, `recap`, `eli5`, `release-workflow`) unless their actual responsibility must change.
5. Do not redesign direct Matt PORT Skills (`research`, `prototype`, `tdd`, `handoff`, `diagnosing-bugs`, `wizard`, `teach`, `wait-what`, `to-questionnaire`, `writing-for-agents`, `resolving-merge-conflicts`) — Port, then only minimal Light-handoff adaptation.
6. Keep new/refactored `SKILL.md` files concise (when, what, how, where to read more, handoff/stop).
7. Put detailed workflows, examples, formats, and reusable guidance in supporting files (`references/`, `templates/`, `scripts/`), not in `SKILL.md`.
8. Do not impose one Skill package shape — each package decides its own structure.
9. Prefer composition over duplicated instructions (`clarify → socratic`, `implement → review-loop`, etc.).
10. Do not duplicate repository architecture into Skill packages.
11. Update only repository documents actually affected by a change.
12. Tests protect behavior and composition, not prose layout — do not re-add prose to satisfy prose tests.
13. Preserve required upstream attribution (`ATTRIBUTION.md`).
14. Do not guess Agent host capabilities — inspect host evidence first (`agent-config`).

Do not bloat this file into SPEC — governance details live in the linked docs.

## Invocation direction

Every package must declare and test one invocation type:

- **User-invoked:** manually selected entry point. Silent or implicit chaining into another user-invoked Skill is forbidden; an advisor may recommend a next user-invoked Skill and, upon explicit user approval and verified host support, transition into that exact target without auto-chaining past it. It may call a model-invoked capability.
- **Model-invoked:** reusable capability callable by the model or another Skill.

## Lifecycle work

For a create, update, rename, deprecation, removal, port, or adapt:

1. Apply the reuse-before-invention decision order in [Skill admission](docs/SKILL_ADMISSION.md).
2. Preserve package boundary, invocation direction, and required attribution.
3. Collect evidence appropriate to the change; structure alone is never behavioral proof.
4. Follow the review trigger and final-verdict rules in [Review policy](docs/REVIEW_POLICY.md).
5. Perform every affected documentation and catalog update in the maintenance synchronization matrix before release.

Do not silently rename, remove, or deprecate. Preserve a migration path, update discovery/installation surfaces, and record the change in the changelog and release notes.

## Validation and review

Classify each Skill admission under [Skill admission](docs/SKILL_ADMISSION.md). An eligible low-risk prompt-only Skill uses the fast track: bounded structural/install/contract/invocation evidence + one fresh independent Evaluator (no separate Critic or `code-review`). All other new or significant Skill changes use the full evidence path; executable scripts additionally require focused automated + negative tests, adversarial fixtures where appropriate, and `code-review` evidence. Zero-assertion or no-op test is not PASS.

For the full path, `review-loop` with the appropriate Profile (`agent-skill`, `generic`, `software`, `manuscript`, `specification`) is the convergence engine; `project-review` owns the frozen baseline and final `PASS`/`FAIL`/`BLOCKED`. Specialist reviewers (`generic-review`, `code-review`, domain) provide findings only (see [Reviewer contract](docs/REVIEWER_CONTRACT.md)) — not a competing verdict.

## Installation, release, and closeout

Do not publish an installation command as verified until it has succeeded against the actual released repository in a fresh environment. Keep a manual fallback and record host discovery as required by [Installation](docs/INSTALLATION.md).

Before a stable release, synchronize the README, catalog, installation guide, governance references, validated examples, discovery tests, changelog, and attribution records. The release and closeout record must distinguish first-party, approved Port, direct upstream, modified third-party, and deprecated/archived sources; include actual release identifiers, verified commands, evidence, limitations, and migration state. Follow the sequence in [Maintenance](docs/MAINTENANCE.md).
