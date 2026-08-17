# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-08-17 (session UTC+8)

## Acceptance baseline
- Source: v1.0.5/Skills v0.1.4 Maintenance SPEC provided by the user in the
  implementation session (sections 3–26, Part A), dated 2026-08-17.
- Source revision or identity: user-approved specification; the frozen
  candidate scope is the `LightDevCoder/skills` working tree on `main` at
  commit `d526ef3` plus the v0.1.5 candidate changes under
  `skills/light-kanban-worker/`, `docs/`, `tests/`, `README.md`,
  `README.zh-CN.md`, `CATALOG.md`, `CATALOG.zh-CN.md`, `CHANGELOG.md`,
  `CHANGELOG.zh-CN.md` (see round-01 producer evidence for the exact file
  list).
- Approval state: approved
- Approval evidence: the user directed this maintenance release and supplied
  the SPEC as the acceptance source.

## Review Profile
- Profile: agent-skill
- Selection reason: the target is an installable model-invoked Agent Skill
  package (`light-kanban-worker`) whose behavior contract, scheduling
  boundary, and first-registration identity rules changed; the repo's
  REVIEW_POLICY requires `review-loop agent-skill` for a material Skill
  behavior/boundary change. Record location follows the repository evidence
  convention (`docs/evidence/releases/v0.1.5/review-loop/`) instead of the
  default `.review-loop/` root.

## Original goal
Maintain the first-party `light-kanban-worker` Skill for release v0.1.5:
forbid overlapping scheduled runs with the same agentId, document the atomic
claim boundary accurately, require ID + name + avatar on first registration
with clear no-mutation failure behavior, keep scenarios A–F intact, add
tested scenarios G and H with honest verification boundaries, and clarify
the pre-release/post-release evidence model.

## User-visible outcome
An agent reading the installed v0.1.5 Skill cannot start two overlapping
runs with one agentId, knows that a first registration needs an avatar and
that later wakes reuse it, and cannot mutate tasks on a missing identity.
Release evidence no longer shows unexplained `PENDING` markers.

## In scope
- `skills/light-kanban-worker/SKILL.md`, `agents/openai.yaml`,
  `references/api.md`, `tests/` (checkers, suites, fixtures).
- The bilingual docs, catalog, changelog, discovery tests, and v0.1.5
  release evidence synchronized for this change.

## Out of scope
- Light-Kanban repository changes (v1.0.6) — reviewed separately there.
- Publishing the v0.1.5 tag, GitHub Release body, and post-release fresh
  install from the published tag (post-release verification, recorded on
  main after the tag exists).
- Any REST API, UI, or Light-Kanban state-machine change.
- Scenarios A–F themselves: unchanged, must keep passing.

## Acceptance criteria
- AC-1: SKILL.md explicitly forbids overlapping same-agent runs — at most
  one invocation per agent id active, a same-agent wake must skip (contract
  test asserts `must not overlap` / `must skip`).
- AC-2: atomic claim is not described as a same-agent concurrency lock; the
  canonical boundary sentence is present.
- AC-3: concurrency control belongs to the scheduler / agent runtime
  (`max concurrent runs = 1` or equivalent); the worker adds no lock
  process, heartbeat, lease service, daemon, or resident polling.
- AC-4: different agent ids may run concurrently (explicitly stated).
- AC-5: first registration requires ID + name + avatar; local avatar upload
  path stays `POST /api/avatars` → `/api/avatars/...`.
- AC-6: an existing agent id reuses the server's stored name/avatar —
  avatar required for first registration, not every wake.
- AC-7: a new agent id missing name/avatar → identity configuration
  missing, no claim, no mutation, run ends; no placeholder avatar or
  guessed identity.
- AC-8: one-task-per-run behavior unchanged; scenarios A–F unchanged and
  passing.
- AC-9: contract suite covers the new rules with non-zero assertions;
  negative fixtures `overlap-allowed-variant.md` and
  `avatar-optional-first-registration.md` each violate exactly one rule and
  must be rejected.
- AC-10: Scenario G (same-agent concurrent wake must skip; scheduler guard,
  no fake server lease) and Scenario H (fresh identity without avatar → no
  mutation; legal avatar → registration → claim) verified with the real
  verification boundary recorded.
- AC-11: bilingual docs synchronized (worker guides, README, CATALOG,
  INSTALLATION, CHANGELOG, MAINTENANCE baseline, discovery tests).
- AC-12: release receipt separates pre-release gate (`READY FOR RELEASE`)
  from post-release verification; no unexplained `PENDING` in the tag
  snapshot.
- AC-13: no new REST API requirement claimed; compatibility stays
  Light-Kanban v1.0.4+.

## Required evidence
- `structural`: SKILL.md / openai.yaml / api.md inspection and link
  resolution.
- `behavioral`: worker contract + behavior suites green with non-zero
  assertions; negative fixtures flip their target checkers.
- `installation`: clean-copy installation and discovery observation in a
  fresh destination (published-tag installer verification is post-release
  and out of this review's scope).
- `invocation`: model-invoked metadata + no automatic invocation of another
  user-invoked Skill.
- `review`: fresh Critic candidates and a fresh Evaluator verdict.

## Required validation scenarios
- VS-1: run `python3 skills/light-kanban-worker/tests/test_light_kanban_worker_contract.py`
  and the behavior suite — PASS with non-zero assertions.
- VS-2: adversarial fixtures rejected by exactly their target checker.
- VS-3: copy the package to a fresh destination; SKILL.md + metadata +
  references discoverable there; package tests still run from the copy.
- VS-4: collection discovery suite green once the review record files exist.

## Constraints, assumptions, and risks
- Python 3.9 locally; CI uses Python 3.11 on ubuntu.
- The published-tag fresh install (`npx skills add
  LightDevCoder/skills#v0.1.5 …`) is post-release evidence only.
- Risk: doc-sync drift between EN and zh-CN — mitigated by the collection
  discovery parity checks.

## Approved exceptions
- None
