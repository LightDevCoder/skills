# Producer Evidence - Round 1

Producer evidence only — final acceptance belongs to the Core with a fresh
independent Evaluator.

## Scope

- Charter revision: 1
- Profile: agent-skill
- In-scope work: `light-kanban-worker` v0.1.5 behavior contract change —
  same-agent non-overlap rule, atomic-claim boundary, scheduler ownership of
  concurrency, first-registration identity (ID + name + avatar),
  missing-identity no-mutation behavior; contract/behavior tests, negative
  fixtures, scenarios G/H; bilingual doc sync; v0.1.5 release evidence with
  the pre/post-release split.
- Out-of-scope check: no Light-Kanban repository, API, or UI changes; no
  publishing steps. Result: clean.

## Evidence

### E-001 - Worker contract suite (source checkout)
- Evidence label: behavioral
- Run: `python3 skills/light-kanban-worker/tests/test_light_kanban_worker_contract.py`
- Expected: PASS with non-zero assertions, including the new v0.1.5 rules.
- Observed: `OK` — 100 assertions, 0 failures. Includes same-agent
  non-overlap, different-agent concurrency, atomic-claim boundary, scheduler
  ownership, no resident lock service, first-registration identity, identity
  reuse, missing-identity no-mutation, local avatar upload path, plus the
  two new negative fixtures and mutation negatives.
- Outcome: PASS
- Validates: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-9, AC-13
- Environment and limitations: Python 3.9.6, macOS; deterministic text
  checks only (no live server) — labeled behavioral only in the
  fixture-execution sense; live-server evidence for A–F is cited separately.
- Artifact: skills/light-kanban-worker/tests/test_light_kanban_worker_contract.py

### E-002 - Worker behavior suite (source checkout)
- Evidence label: behavioral
- Run: `python3 skills/light-kanban-worker/tests/test_light_kanban_worker_behavior.py`
- Expected: PASS with non-zero assertions; scenarios G/H pinned.
- Observed: `OK` — 23 assertions, 0 failures. Scenario G fixture
  (run #1 active → run #2 scheduled → must not start; scheduler guard;
  records no server lease) and Scenario H fixture (missing avatar → identity
  configuration missing → no claim/no mutation → legal avatar → registration
  → claim succeeds) both asserted.
- Outcome: PASS
- Validates: AC-1, AC-7, AC-8, AC-10
- Environment and limitations: deterministic contract fixtures, not a live
  two-worker race — the verification boundary is recorded inside each
  fixture and in the behavioral evidence doc.
- Artifact: skills/light-kanban-worker/tests/test_light_kanban_worker_behavior.py

### E-003 - Negative fixtures flip exactly their target checker
- Evidence label: behavioral
- Run: contract suite fixture loop (part of E-001)
- Expected: `overlap-allowed-variant.md` rejected by
  `no_same_agent_overlap`; `avatar-optional-first-registration.md` rejected
  by `no_avatar_optional_first_registration`; each passes the other five
  rule checkers.
- Observed: exactly as expected; the pre-existing four fixtures still flip
  their own checkers.
- Outcome: PASS
- Validates: AC-9
- Artifact: skills/light-kanban-worker/tests/fixtures/

### E-004 - Scenarios A–F unchanged and passing
- Evidence label: behavioral
- Run: inspection of the v0.1.4 behavioral evidence (scenarios A–F, live
  server) plus unchanged checkers in both suites.
- Expected: A–F evidence retained, not weakened; behavior suite keeps all
  pre-existing assertions.
- Observed: `docs/evidence/admissions/light-kanban-worker/behavioral-evidence.md`
  retains A–F with their live-server results; the suites keep every v0.1.4
  assertion (golden flow order, review-feedback priority, one task per run,
  human-only boundary, workspace blocking, no daemon/polling, API 409/FIFO).
- Outcome: PASS
- Validates: AC-8
- Artifact: docs/evidence/admissions/light-kanban-worker/behavioral-evidence.md

### E-005 - Clean-copy installation and discovery
- Evidence label: installation
- Run: `cp -R skills/light-kanban-worker <fresh-dest>/skills-root/light-kanban-worker`
  into a disposable destination; listing the fresh skills root shows the
  package; the package's own contract + behavior suites run from the copy.
- Expected: complete package (SKILL.md, agents/openai.yaml,
  references/api.md, tests), discoverable without the source checkout, tests
  run from the installed copy.
- Observed: PASS. Fresh destination
  `/tmp/lk-worker-install-2FAMqH/skills-root/light-kanban-worker`; 14 files;
  frontmatter name `light-kanban-worker`; metadata display_name /
  short_description / `allow_implicit_invocation: true`; both suites `OK`
  from the copy after a pre-collection repair (see E-006).
- Outcome: PASS
- Validates: AC-5, AC-11 (package completeness)
- Environment and limitations: manual-copy fallback form, not the
  `npx skills add …#v0.1.5` installer — that published-tag run is
  post-release verification and out of this review's scope.
- Artifact: /tmp/lk-worker-install-2FAMqH/skills-root/light-kanban-worker

### E-006 - Pre-collection repair: package tests self-contained
- Evidence label: structural
- Run: before the repair, running the package suites from an installed copy
  failed with `ModuleNotFoundError: No module named 'check_helpers'` (the
  repo-root harness). The Producer added a self-contained `Checks`/`read`
  fallback in `worker_checks.py` and a try/except import in both test
  modules; both suites then pass from source and from the installed copy.
- Expected: installed copies must not depend on undeclared repository files.
- Observed: resolved; E-005 now passes.
- Outcome: PASS
- Validates: AC-5, AC-11
- Artifact: skills/light-kanban-worker/tests/worker_checks.py,
  test_light_kanban_worker_contract.py, test_light_kanban_worker_behavior.py

### E-007 - Invocation boundary
- Evidence label: invocation
- Run: metadata inspection.
- Expected: model-invoked with implicit invocation allowed; never invokes
  another user-invoked Skill.
- Observed: `allow_implicit_invocation: true`, no
  `disable-model-invocation`; the Skill uses the agent's HTTP and shell
  tools against the Light-Kanban REST API and the project workspace — no
  Skill-to-Skill handoffs, no automatic invocation of another package.
- Outcome: PASS
- Validates: AC-4 (interaction seams), profile invocation axis
- Artifact: skills/light-kanban-worker/agents/openai.yaml, SKILL.md

### E-008 - Structural sync: docs, catalog, changelog, discovery tests
- Evidence label: structural
- Run: collection discovery suite and contract suite over the synchronized
  docs (run after the review record files exist — see note).
- Expected: v0.1.5 presented as the current release; bilingual parity; all
  Markdown links resolve; v0.1.5 evidence paths exist.
- Observed: worker suites green; discovery suite will be re-run once the
  review-record files are written (the CHANGELOG/README link to
  AGENT_SKILL_REVIEW.md produced by this review). The receipt separates the
  pre-release gate (`READY FOR RELEASE`) from post-release verification; the
  tag snapshot will carry no unexplained `PENDING`.
- Outcome: pending final run (blocked only by the self-referential review
  record links)
- Validates: AC-11, AC-12
- Artifact: docs/evidence/releases/v0.1.5/RELEASE_RECEIPT.md

## Limitations

- Deterministic text-level contract/behavior verification; live-server
  A–F evidence is carried over from v0.1.4 (unchanged); G/H are
  contract fixtures with recorded boundaries.
- No `npx skills add` published-tag install here — post-release.
- ask-light scanner behavior suite skipped locally (no pwsh); CI runs it.

## Self-reported producer finding

- Package tests initially depended on the repository-level
  `tests/check_helpers.py` when run from an installed copy. Fixed in E-006
  with a bounded self-containment change (no behavior change to the Skill).
  Recorded here for transparency; the Critic should verify independently.
