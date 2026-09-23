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
6. Execute pre-commit content and quality verification:
   ```bash
   python3 -m pytest -q
   python3 -m unittest discover -s tests
   python3 -m compileall -q skills tests scripts
   python3 scripts/check_public_docs.py
   git diff --check
   ```
7. Commit candidate changes:
   ```bash
   git add <candidate-files>
   git commit -m "release: prepare vX.Y.Z"
   CANDIDATE_SHA="$(git rev-parse HEAD)"
   ```
8. On the clean working tree, validate the `PREPARED` state:
   ```bash
   python3 scripts/verify_release_integrity.py \
     --tag vX.Y.Z \
     --release-commit "$CANDIDATE_SHA" \
     --stage prepared
   ```
9. **Transition:** Transition lifecycle state to `PREPARED`.

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
   both `deletion` and `update` restrictions are present, `bypass_actors` is empty `[]`,
   and `current_user_can_bypass` is `never`. If missing or inactive, report `BLOCKED` and halt tag publication.
2. Verify tag creation preconditions (tag preflight):
   ```bash
   python3 scripts/check_release_tag_preflight.py \
     --tag vX.Y.Z \
     --release-commit "$CANDIDATE_SHA"
   ```
   Requires: candidate commit exists, working tree is clean, remote ruleset PASS,
   and target tag does not exist locally or on origin.
3. Create annotated tag pointing to CI-verified candidate commit (tag snapshot contains Manifest + Notes; Receipt does NOT exist):
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z — <title>"
   ```
4. Validate `TAGGED` state:
   ```bash
   python3 scripts/verify_release_integrity.py \
     --tag vX.Y.Z \
     --release-commit "$CANDIDATE_SHA" \
     --stage tagged
   ```
   If `stage=tagged` verification fails, pushing the tag is strictly forbidden.
   Delete the erroneous unpushed local tag immediately (`git tag -d vX.Y.Z`) and fix the cause.
5. Push the verified annotated tag to origin:
   ```bash
   git push origin vX.Y.Z
   ```
6. Confirm tag resolution:
   ```bash
   git rev-parse refs/tags/vX.Y.Z
   git rev-parse refs/tags/vX.Y.Z^{commit}
   git cat-file -t refs/tags/vX.Y.Z
   ```
   Must confirm object type is `tag` (annotated tag object), not `commit`.
   Re-run `verify_release_integrity.py --tag vX.Y.Z --release-commit "$CANDIDATE_SHA" --stage tagged --check-remote` after the push; this must bind the remote annotated tag object and peeled commit to the local candidate.
7. **Transition:** Transition lifecycle state to `TAGGED`.

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

> **Important — Link Context on GitHub Releases:** GitHub Releases renders Markdown
> with the repository root (`/`) as its base path, not `docs/evidence/releases/vX.Y.Z/`.
> Sibling relative links in `RELEASE_NOTES.md` (such as links pointing to `RELEASE_NOTES.zh-CN.md`)
> will 404 if uploaded directly. Always expand them into canonical repository URLs
> using `scripts/prepare_release_body.py` before publication.

1. Prepare release body expanding sibling relative links to full canonical repository URLs:
   ```bash
   python3 scripts/prepare_release_body.py \
     --tag vX.Y.Z \
     --output /tmp/release_body_vX.Y.Z.md
   ```
2. Publish release using the prepared release body:
   ```bash
   gh release create vX.Y.Z \
     --title "vX.Y.Z — <title>" \
     --notes-file /tmp/release_body_vX.Y.Z.md
   ```
3. Verify release status and public URL, confirming all navigation links resolve cleanly:
   ```bash
   gh release view vX.Y.Z
   ```
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
     --stage attested \
     --check-remote
   ```
5. Only after `verify_release_integrity.py` passes, push the attestation commit to `origin/main`.
6. **Transition:** Transition lifecycle state to `ATTESTED`.
