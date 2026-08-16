# Changelog

[中文变更记录](CHANGELOG.zh-CN.md)

All notable changes are recorded here. A release entry must be tied to an
actual version or tag and must not be created merely because a document was
drafted.

## Unreleased — v0.1.4 candidate

### Added

- New first-party, model-invoked `light-kanban-worker` Skill: each scheduled
  agent run processes at most one Light-Kanban task — stable agent identity,
  owned in-progress work and `reviewFeedback` checked before new claims,
  atomic claim with bounded conflict retry, workspace validation (an
  inaccessible workspace becomes `block` with a meaningful reason), and
  `complete` back to human confirmation. The worker never archives, accepts,
  deletes, recycles, or unblocks tasks, and never loops or starts a resident
  process. Network/filesystem/state side effects place it on the full
  admission path (`review-loop agent-skill`), not the prompt-only fast track.
- Contract and behavior test suites for the worker package with positive and
  negative fixtures (mutation and adversarial fixture files).

### Changed

- Version documentation synchronized: v0.1.3 is the current stable release,
  v0.1.2 and earlier remain historical records, and the v0.1.4 candidate is
  marked unreleased until the release gates pass. README, catalog,
  installation guide, maintenance baseline, discovery tests, and CI updated
  for the eight-package collection.

### Evidence

- Admission: [docs/evidence/admissions/light-kanban-worker/](docs/evidence/admissions/light-kanban-worker/)
- Release evidence is recorded in
  [docs/evidence/releases/v0.1.4/](docs/evidence/releases/v0.1.4/) once the
  release gates pass.

## 0.1.3 — 2026-08-10

### Changed

- Test toolchain migrated from Windows PowerShell to cross-platform Python:
  21 PowerShell test files replaced by 18 Python suites (collection
  discovery, header assets, quick start, ask-light contract, project-init
  contract and behavior, recap contracts, language-learning contract, and
  review-loop five-profile contract and behavior suites plus protocol
  helpers), preserving the assertion sets.
- The ask-light scanner behavior suite still executes the real
  `scripts/ask-light.ps1` through `pwsh` and skips gracefully when pwsh is
  absent; CI (ubuntu-latest) ships pwsh and runs it.
- CI moved to `ubuntu-latest` (bash + python); retired-boundary and
  no-PowerShell-test checks added.
- Documentation updated for the new test file names and the cross-platform
  manual-fallback snippet; governance wording unchanged.

### Evidence

- [docs/evidence/releases/v0.1.3/](docs/evidence/releases/v0.1.3/)

## 0.1.2 — 2026-08-10

### Added

- Prepared the first-party, user-invoked `recap` Skill for v0.1.2. Explicit
  `$recap` invocation returns exactly one line about the current session, never
  runs tools, continues work, changes files, compacts history, or invokes
  another Skill.
- Prepared the first-party, user-invoked `language-learning` Skill for v0.1.2.
  It tutors any target language through six study modes — daily lessons,
  flashcards, conversation practice, grammar decoding, progress quizzes, and
  immersion translation — reusing session context and previously learned
  vocabulary across invocations instead of re-asking.
- Added a low-risk prompt-only admission fast track for owner-authored,
  manual-only, text-output Skills with no tools, side effects, runtime
  executables, or external dependencies. It uses one fresh Evaluator and does
  not require separate Critic or Standards/Spec review.
- Published the generic `latest` install command
  (`npx skills add LightDevCoder/skills --yes --copy --agent '*'`) as the
  standard install path, with the pinned `#v0.1.2` form retained for
  reproducible installs. `recap` and `language-learning` were both admitted by
  a fresh independent prompt-only fast-track Evaluator `PASS`; see their
  [admission evidence](docs/evidence/admissions/).

### Release evidence

- Release tag: `v0.1.2`, commit `8de5ec1a453b0e93f71dcda160e17ea7b42c3997`.
- GitHub Actions `collection-quality`: `PASS` on the merged release commit.
- Fresh whole-collection and per-Skill installs: `PASS` with CLI `1.5.22` for
  both the generic `latest` and pinned `#v0.1.2` forms.
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.2
- Whole-collection and per-Skill fresh-install evidence:
  [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.md).
- Structural and package evidence:
  [TEST_SUMMARY.md](docs/evidence/releases/v0.1.2/TEST_SUMMARY.md).
- Independent `review-loop agent-skill` acceptance for the original five
  packages remains `BLOCKED`; see the
  [release receipt](docs/evidence/releases/v0.1.2/RELEASE_RECEIPT.md).

## 0.1.1 — 2026-07-26

### Added

- Bilingual user guides for all five first-party Skills, validated workflow
  recipes, and a runnable-sized Quick Start example.
- A release evidence tree under
  `docs/evidence/releases/v0.1.1/` and CI checks for structure, metadata,
  links, bilingual pairs, package tests, retired references, and header assets.
- Explicit `$ask-light next` and `$ask-light workflow` modes with bounded
  recipe output, availability gaps, handoff fields, and non-execution tests.
- A redesigned editable SVG and 1600 × 480 PNG header with a flat layered
  `LightDevCoder` / `/skills` wordmark and serif slogan.

### Fixed

- Added `policy.allow_implicit_invocation: false` and matching frontmatter to
  the user-invoked `learn-anything`, `ask-light`, and `project-init` packages.
- Corrected installation language: an unqualified repository source follows
  the CLI's default revision, while `#v0.1.1` will pin the target tag once
  published.

### Release evidence

- Release tag: `v0.1.1`, commit `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`.
- GitHub Actions `collection-quality`: `PASS` on the merged release commit.
- Fresh whole-collection and per-Skill installs: `PASS` with CLI `1.5.20`.
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.1
- Whole-collection and per-Skill fresh-install target evidence:
  [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md).
- Structural and package evidence:
  [TEST_SUMMARY.md](docs/evidence/releases/v0.1.1/TEST_SUMMARY.md).
- The five-package collection remains installable and its collection-quality
  checks passed. Independent evaluator evidence for the `review-loop
  agent-skill` acceptance gate remains `BLOCKED`; this does not block ordinary
  installation or use. See the [release receipt](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.md)
  for the exact evidence boundary.

## 0.1.0 — 2026-07-23

- Established the first-party governance foundation and admitted the five
  first-party Skills.
- Published at https://github.com/LightDevCoder/skills.
- Stable tag: v0.1.0.
- The v0.1.0 whole-collection and per-Skill installer commands were verified
  against a fresh destination and the published package content; this
  historical evidence is retained alongside the v0.1.1 release.
- Historical commands: `npx skills add LightDevCoder/skills` and
  `npx skills add LightDevCoder/skills --skill review-loop`.
- Historical installation details:
  [v0.1.0 summary](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md#historical-v0.1.0-summary).
