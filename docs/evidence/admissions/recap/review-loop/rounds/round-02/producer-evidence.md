# Producer Evidence - Round 2

## Scope
- Charter revision: 1
- Profile: agent-skill
- Repair scope: F-001 through F-005, F-008, and F-009 only
- Frozen behavior: manual `$recap`, exactly one plain-text line, no tools or state mutation

This is repair evidence for fresh evaluation, not final acceptance.

## Repairs

### R-001 - Specialist review requirement
- Finding: F-001
- Change: separate fresh, read-only Standards and Spec reviewers inspected fixed point `origin/main` at `178b2970140b6cd3dc1264d2072ca1ee20ee58f0` versus candidate commit `7cd3a60`.
- Evidence: `round-01/code-review-standards.md`, `round-01/code-review-spec.md`, and Core disposition in `findings.md`.
- Result: both required specialist perspectives now exist; confirmed findings were repaired and rejected findings retain rationale.

### R-002 - Admission wording
- Finding: F-002
- Change: catalog and current-branch documentation use candidate/pending language until the review-loop returns PASS; stable v0.1.1 remains explicitly five packages.
- Result: no current-branch surface prematurely claims final admission.

### R-003 - Accurate deterministic-test labeling
- Finding: F-003
- Change: `recap-behavior-tests.ps1` was replaced with `recap-output-contract-tests.ps1`; CI and evidence use output-contract terminology.
- Result: deterministic fixtures are no longer presented as Agent/runtime behavioral proof; E-005 through E-007 remain the separate fresh-Agent evidence.

### R-004 - Non-zero assertion guards
- Finding: F-004
- Change: both recap PowerShell suites throw unless at least one assertion executed.
- Result: contract suite reports 12 assertions and output-contract suite reports 8 assertions.

### R-005 - Prohibition-aware safety checks
- Finding: F-005
- Change: contract validation requires prohibitions against compaction and implicit handoffs, and tests an unsafe opposite-polarity mutation.
- Result: the declared safety boundary cannot pass through bare keyword presence.

### R-006 - Generalized leading-label rejection
- Finding: F-008
- Change: output validation rejects a leading label pattern rather than a short hard-coded list; fixtures cover `Recap:`, `Status:`, `Result:`, and `**Recap:**`.
- Result: all adversarial label fixtures are rejected and the one-line positive fixtures pass.

### R-007 - Stable release boundary
- Finding: F-009
- Change: PowerShell and Python collection tests explicitly assert that stable v0.1.1 has exactly five packages and excludes `recap`, while the candidate tree has six.
- Result: both suites pass.

## Verification

### E-010 - Focused repaired package tests
- Evidence label: structural
- Run: `skills/recap/tests/recap-contract-tests.ps1`; `skills/recap/tests/recap-output-contract-tests.ps1`
- Observed: `RECAP_CONTRACT_ASSERTIONS=12`, `RECAP_CONTRACT=PASS`, `RECAP_OUTPUT_CONTRACT_ASSERTIONS=8`, `RECAP_OUTPUT_CONTRACT=PASS`.
- Outcome: PASS
- Validates: AC-2, AC-3, AC-4, AC-7, VS-4

### E-011 - Repaired collection boundary
- Evidence label: structural
- Run: PowerShell collection discovery and Python collection contract suites.
- Observed: `COLLECTION_DISCOVERY_ASSERTIONS=782`, `COLLECTION_DISCOVERY=PASS`, `COLLECTION_PYTHON_ASSERTIONS=62`; Python unit suite returned four tests OK.
- Outcome: PASS
- Validates: AC-6, AC-7, VS-6

### E-012 - Fresh-copy installation after repairs
- Evidence label: installation
- Run: isolated per-Skill copy into an empty destination, followed by package listing, no-checkout check, file-set/hash comparison, and installed package tests.
- Observed: only `recap` installed; no source checkout; source and destination file sets matched; zero hash mismatches; installed 12 + 8 assertion suites passed.
- Outcome: PASS
- Validates: AC-5, VS-5
- Limitation: current local candidate, not a published tag.
- Artifact: `D:/Documents/Coding/CodexMaintenance/.recap-fresh-install-round2-20260801`

### E-013 - Full local quality suite
- Evidence label: structural
- Run: every command represented in `.github/workflows/quality.yml` plus Python compile validation.
- Observed: header 11, Quick Start 8, collection discovery 782, ask-light contract and behavior 54, project-init contract and behavior, recap contract 12, recap output contract 8, all review-loop Profile suites, Python collection 62, learn-anything hooks 7, four Python tests OK, and compileall all passed; final marker `FULL_QUALITY=PASS`.
- Outcome: PASS
- Validates: AC-1, AC-6, AC-7, VS-6

## Carried behavioral evidence

Round-1 E-005, E-006, and E-007 remain valid because repairs changed only test accuracy, documentation status, and release-boundary guards; the Skill behavior contract did not change.
