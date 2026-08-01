# Producer Evidence - Round 1

## Scope
- Charter revision: 1
- Profile: agent-skill
- In-scope work: `recap` package, synchronized collection surfaces, tests, installation/discovery, and invocation observations
- Out-of-scope check: no automatic recap trigger, release tag, or published install claim was added

This is Producer evidence, not final acceptance.

## Evidence

### E-001 - Approved behavior source
- Evidence label: source
- Run or observation: user request plus Anthropic `commands`, `interactive-mode`, and `prompt-caching` documentation reviewed on 2026-08-01
- Expected: on-demand recap is one line and does not replace history; local variant is manual-only
- Observed: `/recap` is documented as an on-demand one-line current-session summary; prompt-caching documentation distinguishes recap output from compaction
- Outcome: PASS
- Validates: AC-1, AC-3
- Environment and limitations: observable product boundary only; no Anthropic code or proprietary prompt text was inspected or copied
- Artifact: `docs/skills/recap.md`

### E-002 - Package structure and metadata
- Evidence label: structural
- Run or observation: `skills/recap/tests/recap-contract-tests.ps1`
- Expected: valid package name, explicit-only metadata on both hosts, one-line/no-tool contract, declared handoff boundary
- Observed: `RECAP_CONTRACT_ASSERTIONS=11`; `RECAP_CONTRACT=PASS`
- Outcome: PASS
- Validates: AC-1, AC-2, AC-7
- Environment and limitations: deterministic contract test; not runtime behavior
- Artifact: `skills/recap/`

### E-003 - Deterministic output contract
- Evidence label: structural
- Run or observation: `skills/recap/tests/recap-output-contract-tests.ps1`
- Expected: positive and no-context one-line fixtures pass; multiline and labeled fixtures fail validation
- Observed before bounded repair: `RECAP_BEHAVIOR_ASSERTIONS=5`; `RECAP_BEHAVIOR=PASS`; superseded by round-1 repair evidence with accurate output-contract labeling
- Outcome: PASS
- Validates: AC-3, AC-4, AC-7
- Environment and limitations: deterministic fixture check; fresh Agent observations are recorded separately
- Artifact: `skills/recap/tests/recap-output-contract-tests.ps1`

### E-004 - Fresh-copy installation and discovery
- Evidence label: installation
- Run or observation: from an empty destination, `npx skills add <local-branch-checkout> --skill recap --yes --copy --agent codex`, followed by package listing, source-checkout absence check, installed tests, and SHA-256 comparisons
- Expected: destination contains exactly `recap`; no `skills/` checkout; all four package files present; installed tests pass; contract/metadata hashes match source
- Observed: `installed_skills=recap`; `source_checkout_present=False`; four files listed; 11 contract and 5 behavior assertions passed; `skill_hash_match=True`; `metadata_hash_match=True`
- Outcome: PASS
- Validates: AC-5
- Environment and limitations: Windows, Codex Skills CLI 1.5.21, local-source candidate; this is not released-repository proof
- Artifact: isolated destination `D:/Documents/Coding/CodexMaintenance/.recap-fresh-install-20260801`

### E-005 - Explicit success observation
- Evidence label: behavioral
- Run or observation: fresh read-only agent loaded `skills/recap/SKILL.md`; simulated completed retry implementation and explicit `$recap`
- Expected: exactly one line with latest result and current state
- Observed: `Retry handling was added to client.ts with two passing focused tests, and the changes remain uncommitted.`
- Outcome: PASS
- Validates: AC-3, VS-1
- Environment and limitations: simulated session content supplied to a fresh agent; no repository mutation
- Artifact: fresh agent task `recap_success_observation`

### E-006 - Empty-session boundary observation
- Evidence label: behavioral
- Run or observation: separate fresh read-only agent loaded `skills/recap/SKILL.md`; no completed work or prior tools; explicit `$recap`
- Expected: exactly one safe line without invented progress
- Observed: `This session has just begun, with no completed work or material progress to report.`
- Outcome: PASS
- Validates: AC-4, VS-2
- Environment and limitations: simulated empty session; no repository mutation
- Artifact: fresh agent task `recap_boundary_observation`

### E-007 - Non-trigger invocation observation
- Evidence label: invocation
- Run or observation: separate fresh read-only agent loaded `skills/recap/SKILL.md`; user said `continue implementing the remaining tests` without `$recap`
- Expected: Skill is not invoked
- Observed: `RESULT: NOT_INVOKED`; reason states the Skill requires explicit `$recap` and never triggers automatically
- Outcome: PASS
- Validates: AC-2, AC-4, VS-3
- Environment and limitations: invocation-boundary evaluation, not host telemetry
- Artifact: fresh agent task `recap_nontrigger_observation`

### E-008 - Executable applicability
- Evidence label: structural
- Run or observation: inspect `skills/recap/` resource tree
- Expected: no runtime scripts or executable dependency; tests have non-zero assertions and negative output fixtures
- Observed: runtime package consists of `SKILL.md` and `agents/openai.yaml`; PowerShell files exist only under `tests/` and report 11 + 5 assertions, including multiline/labeled negative cases
- Outcome: PASS
- Validates: AC-7
- Environment and limitations: package tests are executable validation assets, not runtime resources
- Artifact: `skills/recap/`

### E-009 - Collection and package quality
- Evidence label: structural
- Run or observation: run the repository quality commands from `.github/workflows/quality.yml`, including collection discovery, ask-light/project-init/recap package tests, all review-loop Profile suites, and Python unit tests
- Expected: all required checks pass with non-zero assertions
- Observed: header 11, Quick Start 8, collection discovery 771, ask-light behavior 54, recap contract 11, recap behavior 5, review-loop Profile contract/behavior suites PASS, Python collection 60, learn-anything hooks 7, 4 Python tests OK
- Outcome: PASS
- Validates: AC-6, VS-6
- Environment and limitations: local Windows PowerShell/Python run; GitHub Actions remains pending until PR push
- Artifact: `.github/workflows/quality.yml` and local command output
