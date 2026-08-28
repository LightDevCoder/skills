---
name: release-workflow
description: >-
  Run a first-party Agent Skills collection through a governance-gated release:
  prepare the candidate commit, create the annotated tag and GitHub release,
  fresh-install verify against the published tag with both the generic latest
  and pinned forms, then publish the verified evidence and flip the docs from
  release-candidate to released. Use when the user asks to make a new version
  tag, do a fresh-install verification, or publish release evidence for a
  Skills repository. When a release request (new version tag, fresh-install verification, or release evidence publishing) is recognized, this Skill may trigger automatically.
---

# Skills Collection Release Workflow

Governance-gated release for a first-party Agent Skills collection. The
release is a two-commit topology: a **candidate commit** carries the docs and
tests in release-candidate framing and is what the tag points at; a later
**publish commit** flips everything to released framing after fresh-install
verification passes. Never claim a version, tag, or verified install command
until the actual release gate has passed, and never create a public tag or
GitHub release without an explicit affirmative answer from the human user.

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
5. Run the full validation suite (below) and all package-local suites. All green.

Validation gates:
```bash
python3 -m pytest -q
python3 -m unittest discover -s tests
python3 -m compileall -q skills tests
git diff --check
git status --short
```
Package-local validation suites to run: `ask-light`, `project-review`, `socratic`, `clarify`, `project-clarify`, `project-init`, `review-loop`, `kb-init`, `kanban-worker`, `language-learning`.

Completion criterion: the suite passes with the candidate framing, and no doc
or test claims a verified install or a PASS where a gate has not run.

Commit as the candidate (e.g. `release: prepare vX.Y.Z first-party collection
candidate`).

## Phase 2 — Tag, push main, and create GitHub release

> **Gate — explicit human approval before publication.** Pushing `main`, creating
> the annotated tag, and publishing the GitHub release are public, externally visible
> actions and are **not** covered by the original release request itself. Generic
> installation (`npx skills add LightDevCoder/skills ...`) resolves the repository's
> default revision, so remote `main` must point to the candidate commit for generic
> `latest` verification to succeed. Before running any command in this phase you
> MUST stop and obtain explicit human approval:
>
> 1. Present the candidate commit hash, the target tag `vX.Y.Z`, a summary of what
>    the release publishes (33 first-party packages / architecture additions), and
>    the exact public actions about to occur (`push candidate main` + `push tag` +
>    `create GitHub Release`).
> 2. Ask the user to confirm with a clear yes/no choice:
>    `Publish this candidate to origin/main, create tag vX.Y.Z, and create the GitHub Release? YES / NO`
>    Do not treat the original release request, or any earlier conversational agreement
>    or version choice, as proxy consent.
> 3. Tag and publish only after a clear affirmative answer. If the user declines
>    or requests changes, return to Phase 1 and revise the candidate; do not publish anything.
>
> This checkpoint approves publishing the **candidate only**: the fresh-install
> verification in Phase 3 still runs afterwards, and nothing is declared
> `released` / `VERIFIED` until Phase 4.

Tag the candidate commit and publish `main` and the tag together (preferring atomic push):

```bash
git tag -a vX.Y.Z -m "vX.Y.Z — <title>"
git push --atomic origin main vX.Y.Z
# If the remote does not support atomic push, record that fact and use safe sequential pushes:
# git push origin main && git push origin vX.Y.Z

gh release create vX.Y.Z --title "vX.Y.Z — ..." --notes-file release-body.md
```

Verify identity across references:
```bash
git rev-parse HEAD
git rev-parse vX.Y.Z^{}
git ls-remote origin refs/heads/main refs/tags/vX.Y.Z
```
Required identity: candidate commit == origin/main == vX.Y.Z peeled commit.

CI semantics: GitHub Actions `collection-quality` runs on `push to main`, `pull_request`, and `workflow_dispatch`. Release evidence confirms `collection-quality PASS on the candidate commit` on `main`, and separately proves `vX.Y.Z` resolves to that same candidate commit.

The release body uses candidate framing: fresh installs are `NOT TESTED` until the verification record is published.

Completion criterion: explicit human approval was recorded for publishing the candidate, `git rev-parse vX.Y.Z^{}` resolves to the candidate commit, origin/main matches candidate commit, the release is public, and CI passes on the candidate commit on main.

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
5. Run the full validation suite again.

Validation gates:
```bash
python3 -m pytest -q
python3 -m unittest discover -s tests
python3 -m compileall -q skills tests
git diff --check
git status --short
```
Package-local validation suites to run: `ask-light`, `project-review`, `socratic`, `clarify`, `project-clarify`, `project-init`, `review-loop`, `kb-init`, `kanban-worker`, `language-learning`.

Completion criterion: the suite passes with released framing, the publish
commit is pushed, CI passes on it, and the GitHub release body is updated to
the verified released framing.

## Guardrails

- Phase 2 is a hard publication gate: never create the public tag or GitHub
  release without an explicit affirmative answer from the user recorded in the
  conversation.
- Do not rewrite the tag once created; the publish commit follows it.
- Do not call structural evidence runtime proof, or the receipt an independent
  acceptance record while the evaluator row is `BLOCKED`.
- Keep the candidate commit on history; do not amend or rewrite published
  evidence.
