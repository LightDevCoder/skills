# v0.2.3 — Release Integrity Lifecycle & Project-Retro Refactor

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md) · [Release Receipt](RELEASE_RECEIPT.md)

Light Skills v0.2.3 establishes a formalized six-stage release lifecycle separating immutable pre-release manifests from post-publication receipts, provides historical post-release attestation for v0.2.2, refactors `project-retro` into positive state-driven engineering instructions, and enhances automated release integrity verification.

---

## What's new in v0.2.3

### 1. Formalized Release Evidence Lifecycle
Release artifacts now separate pre-publication scope definitions from post-publication verification proofs:
- **`RELEASE_MANIFEST.md`:** Frozen directly inside the release candidate commit and tag. Records version, scope, package count, policy status, and expected tag identity (`refs/tags/v0.2.3^{commit}`), preventing circular commit-hash self-references.
- **`RELEASE_RECEIPT.md`:** Published on `main` following tag creation, CI verification, fresh install testing, and GitHub Release publication. Records verified publication facts: tag object SHA, peeled commit SHA, exact CI run ID, and fresh-install outcomes.
- **Six-Stage Lifecycle:** Formally models release transitions:
  ```text
  PREPARED → CI_VERIFIED → TAGGED → INSTALL_VERIFIED → PUBLISHED → ATTESTED
  ```

### 2. Historical v0.2.2 Post-Release Attestation
Documents historical facts following the v0.2.2 release:
- v0.2.2 tag snapshot (`90095743...`) remains an immutable historical snapshot.
- Documents root cause of initial shallow-checkout CI failure on v0.2.2 (`fetch-depth: 1` in GitHub Actions).
- Records subsequent corrective commit on `main` (`0862a19...`) with hermetic tests and passing CI (run `35502071190`).
- Clarifies embedded candidate receipt status as a historical artifact predecessor.

### 3. `project-retro` Positive Instruction Refactor
Refactors agent-facing instructions into goal-, responsibility-, process-, and state-driven positive expressions:
- **Recommendation Lifecycle States:** Explicit state modeling transitioning retrospective findings to `AWAITING_SELECTION`, and transitioning the human-chosen recommendation to `APPROVED_ACTION` for bounded execution.
- **Audit Communication:** Grounds findings in verified repository evidence, current state, and test outcomes, focusing on systems, workflows, information architecture, guardrails, and tool behavior.
- **Durable Closure Distinction:** Clarifies that `[CLOSED]` findings document durable lessons already protected by code, tests, CI, references, or workflow, keeping them outside Suggested Actions.
- **Smooth Session Handling:** Clarifies that routine sessions with no reusable systemic friction complete through existing workflows without opening a retrospective.

### 4. Automated Release Integrity Guard Enhancements
- **Manifest Verification:** `scripts/verify_release_integrity.py` validates `RELEASE_MANIFEST.md` existence, package counts, policy status, and tag references for v0.2.3+.
- **Receipt Verification:** Validates post-publication receipts against actual peeled tag commit SHAs and release URLs.
- **Hermetic Test Architecture:** Expanded `tests/test_release_integrity.py` with hermetic temporary repository tests verifying manifest validation and target mismatch detection.

---

## Installation

### Stable Pinned Snapshot (v0.2.3)
To install the immutable, reproducible v0.2.3 release snapshot:

```bash
# Entire 36-skill collection:
npx skills add LightDevCoder/skills#v0.2.3 -y

# Individual skills:
npx skills add LightDevCoder/skills#v0.2.3 --skill project-retro -y
npx skills add LightDevCoder/skills#v0.2.3 --skill agent-config -y
npx skills add LightDevCoder/skills#v0.2.3 --skill ask-light -y
npx skills add LightDevCoder/skills#v0.2.3 --skill project-init -y
```

### Latest Default (main)
To install the latest development state from the default branch:

```bash
npx skills add LightDevCoder/skills -y
```
