---
name: release-workflow
description: >-
  Run a first-party Agent Skills collection through a governance-gated release:
  prepare the candidate commit, create the annotated tag and GitHub release,
  fresh-install verify against the published tag with both the generic latest
  and pinned forms, then publish the verified evidence and flip the docs from
  release-candidate to released. Use when the user asks to make a new version
  tag, do a fresh-install verification, or publish release evidence for a
  Skills repository.
disable-model-invocation: true
---

# Skills Collection Release Workflow

Governance-gated release for a first-party Agent Skills collection. The
release is a two-commit topology: a **candidate commit** carries the docs and
tests in release-candidate framing and is what the tag points at; a later
**publish commit** flips everything to released framing after fresh-install
verification passes. Never claim a version, tag, or verified install command
until the actual release gate has passed.

## Phase 1 — Prepare the candidate commit

Working tree carries the new package(s) and docs in candidate framing. Before
tagging, verify the candidate is internally consistent:

1. `CHANGELOG.md` (and `.zh-CN.md`) has an `## Unreleased — target vX.Y.Z`
   entry with `NOT TESTED` release evidence.
2. `README` / `CATALOG` / `INSTALLATION` present the target as a **release
   candidate** and keep the current stable release named explicitly.
3. Evidence docs under `docs/evidence/releases/vX.Y.Z/` say `NOT TESTED` where
   a gate has not run.
4. Tests assert the candidate markers (release-evidence `NOT TESTED`,
   stable-boundary wording, semantic-pair parity).
5. Run the full suite (below). All green.

Completion criterion: the suite passes with the candidate framing, and no doc
or test claims a verified install or a PASS where a gate has not run.

Commit as the candidate (e.g. `release: prepare vX.Y.Z first-party collection
candidate`).

## Phase 2 — Tag and GitHub release

Tag the candidate commit, not a later commit:

```bash
git tag -a vX.Y.Z -m "vX.Y.Z first-party Skills collection / Release candidate: ..."
git push origin vX.Y.Z
gh release create vX.Y.Z --title "vX.Y.Z — ..." --notes-file release-body.md
```

The release body uses candidate framing: the fresh installs are `NOT TESTED`
until the verification record is published.

Completion criterion: `git rev-parse vX.Y.Z^{}` resolves to the candidate
commit, the release is public, and CI passes on the tag commit.

## Phase 3 — Fresh-install verification

Verify against the **published** tag in disposable destinations, never against
the source checkout. See [references/VERIFICATION.md](references/VERIFICATION.md)
for the full procedure, command matrix, and evidence fields.

Verify all four variants — whole collection and per-Skill, each for both the
generic `latest` form and the pinned `#vX.Y.Z` form:

```bash
npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'
npx --yes skills add LightDevCoder/skills --skill <name> --yes --copy --agent '*'
npx --yes skills add LightDevCoder/skills#vX.Y.Z --yes --copy --agent '*'
npx --yes skills add LightDevCoder/skills#vX.Y.Z --skill <name> --yes --copy --agent '*'
```

Record for each: CLI version, released commit, fresh destination, install exit
code, discovery without source checkout, success/boundary/missing-dependency
smoke, and repeat-install behavior. Record evidence classes accurately:
structural/discovery evidence is not runtime proof.

Completion criterion: all four variants PASS with a recorded CLI version, and
the results are written into the release evidence docs.

## Phase 4 — Publish the evidence commit

Flip the whole tree from candidate to released:

1. Fill the evidence docs: `RELEASE_RECEIPT` → `VERIFIED` with release commit
   and URL; `TEST_SUMMARY` / `INSTALLATION_VERIFICATION` /
   `DISCOVERY_VERIFICATION` / `LIMITATIONS` → `PASS` with the real observed
   values (CLI version, assertion counts, CI run number, limitations).
2. Flip `CHANGELOG` to `## vX.Y.Z — <date>` with `Release evidence` and the
   verified results.
3. Flip `README` / `CATALOG` / `INSTALLATION` / `MAINTENANCE` / skill guides
   (EN + zh-CN) to released framing: the target is now the current stable
   release; `recap`-style "not present in stable v0.1.1" lines become
   "released in vX.Y.Z, install with…".
4. Flip the test assertions: release-evidence marker loop to `VERIFIED` /
   `PASS`, boundary wording to the new stable, semantic parity to the
   published phrases. Install-command guidance uses the generic `latest` form
   (`--agent '*'`, no version) with the pinned form retained for reproducibility.
5. Run the full suite again.

Full suite:
```bash
pwsh -File tests/collection-discovery-tests.ps1
pwsh -File tests/quick-start-smoke-tests.ps1
pwsh -File tests/header-asset-tests.ps1
python -m unittest discover -s tests -p "test*.py"
python -m compileall -q skills tests/test_collection_contract.py
```

Completion criterion: the suite passes with released framing, the publish
commit is pushed, CI passes on it, and the GitHub release body is updated to
the verified released framing.

## Guardrails

- Do not rewrite the tag once created; the publish commit follows it.
- Do not call structural evidence runtime proof, or the receipt an independent
  acceptance record while the evaluator row is `BLOCKED`.
- Keep the candidate commit on history; do not amend or rewrite published
  evidence.
