# LightDevCoder/skills v0.2.3 Release Manifest

[中文清单](RELEASE_MANIFEST.zh-CN.md) · [Release Notes](RELEASE_NOTES.md) · [Release Receipt](RELEASE_RECEIPT.md)

This release manifest represents the immutable pre-publication specification of release `v0.2.3`. It is committed into the candidate release commit and permanently frozen inside the annotated tag.

---

## 1. Release Specification

| Field | Value |
| :--- | :--- |
| **Release Version** | `v0.2.3` |
| **Expected Tag** | `refs/tags/v0.2.3` |
| **Release Identity** | `refs/tags/v0.2.3^{commit}` (resolved upon tag creation) |
| **Release Scope** | 36 admitted first-party Skills across 7 purpose-based categories; release evidence lifecycle redesign separating immutable Release Manifest from publication Release Receipt; v0.2.2 post-release historical attestation; project-retro positive instruction refactoring and state transitions (`AWAITING_SELECTION` $\to$ `APPROVED_ACTION`); automated manifest integrity verification. |
| **Collection Package Count** | 36 admitted packages |
| **Policy Status** | `PROVISIONAL` |
| **Working-Tree Baseline** | Clean, zero untracked modifications in tracked scopes |
| **Tag Immutability** | Permanently immutable upon publication |

---

## 2. Release Lifecycle Model

This release enforces the formalized six-stage lifecycle:

```text
PREPARED
    ↓
CI_VERIFIED
    ↓
TAGGED
    ↓
INSTALL_VERIFIED
    ↓
PUBLISHED
    ↓
ATTESTED
```

- **Manifest Responsibility:** Pre-publication identity and scope frozen inside the release tag commit.
- **Receipt Responsibility:** Post-publication attestation of remote CI conclusion, fresh install counts, and GitHub Release publication facts on `main`.

---

## 3. Pre-Tag Local Verification Evidence

| Gate | Status | Evidence |
| :--- | :--- | :--- |
| **Local Test Suite** | `PASS` | 413 passed (standalone full test suite); unittest suites clean |
| **Bytecode Compilation** | `PASS` | `python -m compileall -q skills tests` clean |
| **Release Integrity Preflight** | `PASS` | `scripts/verify_release_integrity.py` clean |
| **Git Cleanliness** | `PASS` | `git diff --check` clean, zero whitespace violations |
| **Package Contracts** | `PASS` | All 36 packages conform to contract and discovery specifications |

---

## 4. Compatibility Baseline

- **Python Runtime:** Python >= 3.9 (tested on 3.9, 3.11)
- **Node.js Runtime:** Node.js >= 18 (tested on 20)
- **Official Skills CLI:** Compatible with `vercel-labs/skills` v1.7.0 CLI conventions
- **Harness Integration:** Flat installation (`<skills-root>/<name>/`), dual global/project scopes
