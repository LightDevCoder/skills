# Changelog

[中文变更记录](CHANGELOG.zh-CN.md)

All notable changes are recorded here. A release entry must be tied to an
actual version or tag and must not be created merely because a document was
drafted.

## 0.1.6 — 2026-08-19

### Added

- First-party `kb-init` Skill: the formal knowledge-base initialization
  package replaces the earlier unreleased draft. It adds expanded core
  principles (decision provenance, open-decision surfacing, depth before
  settlement), readiness checks, human-navigation design, a research contract,
  connection setup/validation, backup/recovery semantics, and 38 regression
  eval cases. It remains user-invoked only per owner decision.
- Contract tests and bilingual user guides updated for the formal kb-init package.
- v0.1.6 publishes the nine-package collection: v0.1.1's five, `recap` and
  `language-learning` (v0.1.2), `kanban-worker` (renamed from
  `light-kanban-worker` in v0.1.6; first released in v0.1.4), and `kb-init`.

### Changed

- `light-kanban-worker` was renamed to `kanban-worker`. The package directory,
  `SKILL.md` name/frontmatter, `agents/openai.yaml`, tests, guides, catalog,
  README, and installation surfaces now use `kanban-worker`. Historical v0.1.4
  and v0.1.5 records retain the old name with a migration note.
- `kb-init` stays explicit-only: `disable-model-invocation: true` in
  `SKILL.md` and `allow_implicit_invocation: false` in `agents/openai.yaml`.
- README, catalog, installation guide, maintenance baseline, discovery tests,
  and bilingual guides updated from the v0.1.5 eight-package release boundary
  to the v0.1.6 nine-package release.

### Release evidence

- Release tag: `v0.1.6`, commit `41b6e7169a1c68bb017f9ff6c464b220185b02ff`.
- GitHub Actions `collection-quality`: PASS on the release commit (run `32230990952`).
- Fresh whole-collection and per-Skill installs: PASS with the documented CLI
  for both generic `latest` and pinned `#v0.1.6` forms; see
  [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.md).
- Host discovery:
  [DISCOVERY_VERIFICATION.md](docs/evidence/releases/v0.1.6/DISCOVERY_VERIFICATION.md).
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.6
- Final receipt:
  [RELEASE_RECEIPT.md](docs/evidence/releases/v0.1.6/RELEASE_RECEIPT.md).

## 0.1.5 — 2026-08-17

### Changed

- `light-kanban-worker` now explicitly forbids overlapping scheduled runs
  with the same `LIGHT_KANBAN_AGENT_ID`: at most one invocation per agent id
  may be active, a wake that fires while the previous run is still active
  must skip, and different agent ids may still run concurrently. The atomic
  claim boundary is documented accurately — atomic claim protects two
  different workers claiming the same To Do task and is not a concurrency
  lock for multiple invocations using the same agent identity; concurrency
  control stays with the scheduler / agent runtime (`max concurrent runs =
  1` or an equivalent skip-while-active setting), and the worker adds no
  lock process, heartbeat, or lease service.
- First registration now clearly requires ID + name + avatar. A local image
  is uploaded through `POST /api/avatars` and the returned
  `/api/avatars/...` path is used for the claim; an existing agent id reuses
  the server's stored name/avatar, so later wakes do not repeat the avatar.
  A new agent id without a name or avatar reports identity configuration
  missing, claims nothing, and mutates nothing.
- `agents/openai.yaml` default prompt updated to the first-run-capable
  one-shot form (Agent ID / Name / Avatar) so a fresh board can register a
  new agent identity.

### Tests

- Worker contract suite extended with the scheduling-boundary rules:
  same-agent non-overlap, different-agent concurrency, atomic-claim
  boundary, scheduler ownership of concurrency, no resident lock service,
  first-registration identity, identity reuse, missing-identity
  no-mutation, and the local avatar upload path.
- New adversarial negative fixtures `overlap-allowed-variant.md` and
  `avatar-optional-first-registration.md`; each violates exactly one rule
  and must be rejected.
- Behavior suite adds Scenario G (same-agent concurrent wake: the second run
  must not start while run #1 is active, verified through a scheduler-guard
  fixture — Light-Kanban itself provides no run lease) and Scenario H (fresh
  identity without avatar: no claim, no mutation, clear configuration
  failure; a legal avatar then makes registration and claim succeed).
  Scenarios A–F remain unchanged and passing.
- Release evidence workflow clarified: the receipt now separates the
  pre-release gate (candidate tests, admission, catalog sync — `READY FOR
  RELEASE`) from post-release verification (published tag identity, fresh
  install, host discovery, release CI), so a published tag no longer shows
  unexplained `PENDING` markers.

### Evidence

- Release tag: `v0.1.5`, commit `a56aa9d98de0b941ee2282144bc7e756ef5e48bd`.
- GitHub Actions `collection-quality`: `PASS` on the release commit
  (run `31985455493`).
- `review-loop agent-skill` acceptance for the contract change: PASS with
  full independence (findings F-001/F-002/F-003/G-001 repaired) —
  [AGENT_SKILL_REVIEW.md](docs/evidence/releases/v0.1.5/AGENT_SKILL_REVIEW.md).
- Fresh installs: whole-collection and per-Skill, generic `latest` and
  pinned `#v0.1.5` forms, CLI `1.5.22` — PASS; installed package
  byte-identical to the tag and its suites run standalone. See
  [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.md).
- Host discovery: [DISCOVERY_VERIFICATION.md](docs/evidence/releases/v0.1.5/DISCOVERY_VERIFICATION.md).
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.5
- Final receipt (pre-release gate + post-release verification):
  [RELEASE_RECEIPT.md](docs/evidence/releases/v0.1.5/RELEASE_RECEIPT.md).

## 0.1.4 — 2026-08-16

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
  negative fixtures (adversarial single-rule fixture files) and a frontmatter
  YAML-safety gate.
- A negative outside-readable-path scenario in the ask-light behavior suite.

### Changed

- Version documentation synchronized: v0.1.4 is the current stable release,
  v0.1.3 and earlier remain historical records. README, catalog, installation
  guide, maintenance baseline, discovery tests, and CI updated for the
  eight-package collection.
- Fixed the ask-light scanner's `Test-PathUnder` path comparison, which
  hardcoded Windows separators and made the collection-quality workflow fail
  on ubuntu-latest since the v0.1.3 Python port.

### Release evidence

- Release tag: `v0.1.4`, commit `a9cc8aa029c926fc80f6ddc0022793f79dfd85bd`.
- GitHub Actions `collection-quality`: `PASS` on the release commit
  (run `31962459531`).
- Fresh whole-collection and per-Skill installs: `PASS` with CLI `1.5.22`
  for both the generic `latest` and pinned `#v0.1.4` forms.
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.4
- Whole-collection and per-Skill fresh-install evidence:
  [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.4/INSTALLATION_VERIFICATION.md).
- Structural and package evidence:
  [TEST_SUMMARY.md](docs/evidence/releases/v0.1.4/TEST_SUMMARY.md).
- Admission: [light-kanban-worker evidence](docs/evidence/admissions/light-kanban-worker/README.md).
- Scanner code-review: [CODE_REVIEW.md](docs/evidence/releases/v0.1.4/CODE_REVIEW.md).
- Independent `review-loop agent-skill` acceptance for the original five
  packages remains `BLOCKED`; see the
  [release receipts](docs/evidence/releases/).

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
