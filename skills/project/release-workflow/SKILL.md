---
name: release-workflow
description: >-
  Run a first-party Agent Skills collection through a governance-gated release:
  prepare the candidate commit with an immutable release manifest, verify CI
  on main, create the annotated tag, verify fresh installation, publish the
  GitHub release, and attest publication facts in a post-release receipt. Use
  when the user asks to make a new version tag, do a fresh-install verification,
  or publish release evidence for a Skills repository. When a release request
  (new version tag, fresh-install verification, or release evidence publishing)
  is recognized, this Skill may trigger automatically.
---

# Skills Collection Release Workflow

Governance-gated release workflow for a first-party Agent Skills collection.
The release follows a six-stage lifecycle separating immutable pre-release
manifests from post-publication attestation receipts:

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

## Release Artifact Architecture

The release workflow maintains three distinct artifacts across cleanly separated lifecycles:

1. **Release Notes (`RELEASE_NOTES.md` / `RELEASE_NOTES.zh-CN.md`):**
   User-facing summary of new capabilities, architectural changes, breaking
   changes, and migration guidance. Created during `PREPARED` and frozen inside the tag.
2. **Release Manifest (`RELEASE_MANIFEST.md` / `RELEASE_MANIFEST.zh-CN.md`):**
   Immutable pre-publication release snapshot committed directly into the
   candidate commit and frozen inside the tag. Records version, scope, package
   count, policy status, expected tag identity (`refs/tags/vX.Y.Z^{commit}`),
   compatibility baselines, and local verification evidence. Avoids circular
   commit-hash self-references and does not link relatively to uncreated receipts;
   notes that post-publication verification is attested on `main` in `RELEASE_RECEIPT.md`.
3. **Release Receipt (`RELEASE_RECEIPT.md` / `RELEASE_RECEIPT.zh-CN.md`):**
   Post-publication attestation recording verified facts: tag object SHA, peeled
   commit SHA, exact GitHub Actions CI run ID and conclusion, pinned and generic
   fresh install outcomes, GitHub Release URL, and publication timestamp.
   **Created for the first time on `main` during `ATTESTED`** (directly with
   `Status: VERIFIED` or documented failure). Receipts never exist inside tag
   snapshots or candidate preparation commits.

---

## Release Lifecycle Stages

### 1. Stage PREPARED (Candidate Preparation — Manifest + Notes Only)

Prepare the candidate commit carrying code, documentation, and the immutable
release manifest:

1. Update `CHANGELOG.md` (and `.zh-CN.md`) with target version entries.
2. Maintain `README` / `CATALOG` / `INSTALLATION` in candidate framing, naming
   the target release candidate and keeping the current stable release explicit.
3. Create `RELEASE_MANIFEST.md` and `RELEASE_MANIFEST.zh-CN.md` under
   `docs/evidence/releases/vX.Y.Z/` recording pre-tag facts (version, scope,
   package count, policy status, tag ref). Manifest must not include relative
   links to uncreated receipts.
4. Create candidate `RELEASE_NOTES.md` and `RELEASE_NOTES.zh-CN.md`.
5. **Do NOT create `RELEASE_RECEIPT*.md`** in `PREPARED`. No candidate receipts
   may enter candidate commits or tag snapshots.
6. Execute local verification gates:
   ```bash
   python3 scripts/verify_release_integrity.py --tag vX.Y.Z --release-commit HEAD --stage prepared
   python3 scripts/check_public_docs.py
   python3 -m pytest -q
   python3 -m unittest discover -s tests
   python3 -m compileall -q skills tests
   git diff --check
   git status --short
   ```
7. Commit candidate changes: `release: prepare vX.Y.Z`.
8. **Transition:** Transition lifecycle state to `PREPARED`.

### 2. Stage CI_VERIFIED (Remote CI Verification on Main)

Ensure the exact candidate commit is verified by remote CI:

1. Push candidate commit to `origin/main`.
2. Await remote GitHub Actions `collection-quality` execution on the exact candidate commit SHA:
   ```bash
   gh run list --commit <candidate-sha> -L 1
   gh run watch <run-id>
   ```
3. Verify CI conclusion is `SUCCESS`.
4. **Transition:** Transition lifecycle state to `CI_VERIFIED`.

### 3. Stage TAGGED (Remote Tag Protection Gate & Immutable Tag Creation)

> **Publication Gate — User Authorization:** Creating the public tag and
> publishing the release are externally visible actions. Present the candidate
> commit SHA, target tag `vX.Y.Z`, package count, and the exact actions to
> occur. Obtain affirmative confirmation before pushing the tag:
> `Publish candidate to origin/main, create tag vX.Y.Z, and publish GitHub Release? YES / NO`

Create the annotated tag pointing to the exact CI-verified commit:

1. Verify remote GitHub tag ruleset protection:
   ```bash
   python3 scripts/check_release_tag_protection.py
   ```
   Requires: target is `tag`, enforcement is `active`, pattern covers `refs/tags/v*`,
   and both `deletion` and `update` restrictions are present. If missing or inactive,
   report `BLOCKED` and halt tag publication.
2. Verify tag immutability guard:
   ```bash
   python3 scripts/verify_release_integrity.py --tag vX.Y.Z --release-commit <candidate-sha> --stage tagged
   ```
3. Create annotated tag (tag snapshot contains Manifest + Notes; Receipt does NOT exist):
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z — <title>"
   git push origin vX.Y.Z
   ```
4. Confirm tag resolution:
   ```bash
   git rev-parse refs/tags/vX.Y.Z
   git rev-parse refs/tags/vX.Y.Z^{commit}
   ```
5. **Transition:** Transition lifecycle state to `TAGGED`.

### 4. Stage INSTALL_VERIFIED (Fresh Install Verification)

Verify installation against the published tag in disposable directories,
independent of the source checkout:

1. **Pinned Whole Collection:**
   ```bash
   npx --yes skills add LightDevCoder/skills#vX.Y.Z --yes --copy --agent '*'
   ```
2. **Generic Latest Whole Collection:**
   ```bash
   npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'
   ```
3. Verify installed package count matches the 36 admitted packages and contracts
   discover cleanly.
4. Record CLI version, package counts, discovery results, and destination paths.
5. **Transition:** Transition lifecycle state to `INSTALL_VERIFIED`.

### 5. Stage PUBLISHED (GitHub Release Publication)

Create the formal GitHub Release:

1. Prepare release body linking English Release Notes, Chinese Release Notes,
   and Release Manifest. Note in the body that post-publication verification facts
   are attested on `main` in `RELEASE_RECEIPT.md` during stage `ATTESTED` (do not link
   uncreated receipts).
2. Publish release:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z — <title>" --notes-file <notes.md>
   ```
3. Verify release status and public URL.
4. **Transition:** Transition lifecycle state to `PUBLISHED`.

### 6. Stage ATTESTED (Post-Release Attestation — Receipt Created on Main)

Record verified publication facts into `RELEASE_RECEIPT.md`:

1. Create `docs/evidence/releases/vX.Y.Z/RELEASE_RECEIPT.md` and `.zh-CN.md` for
   the first time on `main` (with `Status: VERIFIED` or documented failure), recording:
   - Tag object SHA and peel target commit SHA
   - Exact CI run ID and conclusion
   - Pinned and generic fresh install verification counts
   - GitHub Release URL and publication timestamp
   Receipts may link back to `RELEASE_MANIFEST.md` and `RELEASE_NOTES.md`.
2. Update documentation and catalog to reflect the new stable release.
3. Commit attestation to `main`: `docs(release): attest vX.Y.Z publication`.
4. On the clean working tree on `main`, run the full ATTESTED integrity gate:
   ```bash
   python3 scripts/verify_release_integrity.py \
     --tag vX.Y.Z \
     --release-commit <candidate-sha> \
     --stage attested
   ```
5. Only after `verify_release_integrity.py` passes, push the attestation commit to `origin/main`.
6. **Transition:** Transition lifecycle state to `ATTESTED`.
