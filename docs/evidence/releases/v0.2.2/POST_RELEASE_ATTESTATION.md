# Post-Release Attestation — v0.2.2

[中文说明](POST_RELEASE_ATTESTATION.zh-CN.md) · [Release Receipt](RELEASE_RECEIPT.md) · [Release Notes](RELEASE_NOTES.md)

This attestation records the historical publication facts, CI findings, and post-release corrections for release `v0.2.2`.

---

## 1. Historical Release Facts

| Item | Value |
| :--- | :--- |
| **Release Tag** | `v0.2.2` |
| **Annotated Tag Object** | `e3a6775838a16f27a7e07abbc5187585ce871151` |
| **Tag Target Commit** | `90095743cde38c3513e141838c988adcdaf8a4eb` |
| **GitHub Release Published** | `2026-09-20T09:17:42Z` |
| **GitHub Release URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.2 |
| **Tag Immutability Status** | Permanently immutable historical snapshot |

---

## 2. Tag-Associated CI Status & Root Cause

| Pipeline | Run ID | Conclusion | Notes |
| :--- | :--- | :--- | :--- |
| GitHub Actions `collection-quality` | `35501872550` | `FAILURE` | Run on target commit `90095743...` |

### Failure Root Cause
The initial CI execution for commit `90095743cde38c3513e141838c988adcdaf8a4eb` failed because GitHub Actions workflow `actions/checkout` was configured with default shallow checkout (`fetch-depth: 1`, `fetch-tags: false`). The release integrity unit tests at that time depended on querying actual repository git history and tags, which were absent in the shallow CI workspace.

---

## 3. Corrective Development & Verified State

Following the v0.2.2 publication, immediate corrective engineering was performed directly on `main`:

| Item | Value |
| :--- | :--- |
| **Corrective Commit** | `0862a19617aa9f9161575fe9c8b882fd1c3eb134` |
| **Corrective Action 1** | Configured CI checkout to fetch full history (`fetch-depth: 0`). |
| **Corrective Action 2** | Refactored `tests/test_release_integrity.py` to use hermetic temporary git repositories for unit tests, removing runtime dependencies on external git tags. |
| **Corrective CI Run ID** | `35502071190` |
| **Corrective CI Conclusion** | `SUCCESS` (29s, all suites passing) |

---

## 4. Embedded Receipt State Clarification

The release snapshot embedded in tag `v0.2.2` contains `docs/evidence/releases/v0.2.2/RELEASE_RECEIPT.md` with:

```text
Status: CANDIDATE
Human approval: PENDING
CI: PENDING
Fresh install: PENDING
```

This reflects a historical artifact lifecycle design where candidate receipts were committed prior to publication rather than separated into an immutable pre-release manifest and a post-publication attestation receipt.

---

## 5. Architectural Boundary

- **`v0.2.2` Tag Snapshot (`90095743...`):** Remains an immutable, published historical snapshot. The tag is not retargeted, force-moved, or rewritten.
- **Post-Release Development (`0862a196+`):** Carries the CI fix, this historical attestation, and the release lifecycle improvements formalized in `v0.2.3`.
