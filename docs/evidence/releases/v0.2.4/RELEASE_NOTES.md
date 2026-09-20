# v0.2.4 — Release Integrity Hardening & Git-Object Verification

[中文发布说明](RELEASE_NOTES.zh-CN.md) · [Release Manifest](RELEASE_MANIFEST.md)

Light Skills v0.2.4 hardens the release integrity guardrails by strictly binding release evidence to immutable Git tree objects, isolating post-publication attestation receipts from inventory drift, enforcing unidirectional fail-closed tag preflight, and establishing public documentation quality standards across bilingual surfaces. Post-publication verification facts are attested on main in RELEASE_RECEIPT.md.

---

## What's new in v0.2.4

### 1. Git-Object Release Artifact Binding
Release evidence verification now binds directly to Git tree objects:
- `RELEASE_MANIFEST.md` and `RELEASE_NOTES.md` are verified from candidate commit trees and tag snapshots (`refs/tags/v0.2.4^{commit}`), guaranteeing uncommitted or untracked filesystem working-tree artifacts cannot satisfy release gates.
- Tag preflight detects and strictly rejects untracked release evidence under `docs/evidence/releases/vX.Y.Z/`.

### 2. Post-Publication Receipt Snapshot Isolation
- In stage `ATTESTED`, collection package count verification is bound to the immutable candidate release snapshot (`release_revision`), preventing post-publication inventory drift on `main` from corrupting published release facts.
- Re-auditing stage `TAGGED` after post-publication attestation strictly inspects the tag snapshot without filesystem receipt leakage.

### 3. Fail-Closed Unidirectional Tag Preflight & Tag Protection
- Remote tag preflight checks `origin` by default and treats query or network failures as `BLOCKED` (fail-closed).
- Enforces unidirectional tag creation where pre-existing local or remote tags unconditionally block tag creation.
- Enforces active GitHub ruleset tag protection with deletion and update restrictions, zero bypass actors, and `current_user_can_bypass='never'`.

### 4. Annotated Tag Enforcement
- Enforces annotated tag objects for all release tags (`git cat-file -t` must return `tag`). Lightweight tags are strictly rejected across all release stages.

### 5. Traceback-Free Structured Failure Reporting
- All validation error paths use canonical relative logical paths, guaranteeing zero Python tracebacks and clean structured `VerificationResult` outcomes across both revision and filesystem modes.

### 6. Public Documentation Quality Gate
- Automated checks verify bilingual terminology across `README.md`, `CATALOG.md`, and `INSTALLATION.md`, eliminating internal implementation anti-patterns and ensuring semantic parity between English and Chinese catalogs.

---

## Installation

### Stable Pinned Snapshot (v0.2.4)
To install the immutable, reproducible v0.2.4 release snapshot:

```bash
# Entire 36-skill collection:
npx skills add LightDevCoder/skills#v0.2.4 -y

# Individual skills:
npx skills add LightDevCoder/skills#v0.2.4 --skill agent-config -y
npx skills add LightDevCoder/skills#v0.2.4 --skill project-review -y
```

### Generic Latest Installation
To install the latest stable version:

```bash
npx skills add LightDevCoder/skills -y
```
