# Local Jujutsu gates

## Selection

Inherit an existing project version system. For a new Project route, prefer
non-colocated local Jujutsu:

```text
jj git init --no-colocate <project-root>
```

Probe `jj --version` and command help first. The end-to-end tested baseline is
`0.43.0`; do not upgrade or downgrade automatically. Configure a neutral local
identity if the repository lacks one. Never add a remote for a manuscript
project unless the user separately authorizes it.

## Changes

Give every meaningful working change a description. Before pausing, inspect:

```text
jj status
jj log
jj bookmark list
jj git remote list
```

Use the safest read-only or `--ignore-working-copy` form available when merely
auditing state.

## Date versions

Use `YYYY.MM.DD`. If any gate receipt or bookmark already uses that date, select
`YYYY.MM.DD-02`, then `-03`, and so on. `scripts/next_version.py` calculates the
next unused value without writing.

## Gate bookmarks

Create stable names such as:

```text
brief-approved-2026.07.18
baseline-2026.07.18
framework-approved-2026.07.18
source-locked-2026.07.18
final-approved-2026.07.18
publish-approved-2026.07.18
```

Maintain mutable aliases `current-brief`, `current-baseline`,
`current-framework`, `current-source-locked`, `current-final`, and
`current-publish`.

At Jujutsu `0.43.0`, configure repository immutability so dated gate bookmark
targets are included in `immutable_heads()` while `current-*` aliases are not.
Probe the current configuration syntax before writing it. A representative
revset is:

```text
builtin_immutable_heads()
| bookmarks(glob:"brief-approved-*")
| bookmarks(glob:"baseline-*")
| bookmarks(glob:"framework-approved-*")
| bookmarks(glob:"source-locked-*")
| bookmarks(glob:"final-approved-*")
| bookmarks(glob:"publish-approved-*")
```

Verify immutability by attempting only a safe disposable-repository test. Never
use `--ignore-immutable` in a manuscript project.

## Receipt sequence

1. Freeze the artifact and review evidence in a content revision.
2. Calculate file hashes, then start a child revision without changing those
   files.
3. Record the parent content revision's change and commit IDs in a new
   GateReceipt and write the receipt in that child.
4. Create the dated bookmark at the child receipt-seal revision.
5. Move the corresponding `current-*` alias to the dated bookmark.
6. Verify that the bookmark contains the exact current GateReceipt bytes, that
   its parent IDs equal the receipt's Jujutsu IDs, and that every receipt-listed
   file at that parent matches its recorded SHA-256.

A `publish-approved` receipt also records a structured publication target
(kind, identifier, action, visibility, and evidence) and a path/hash reference
to the active `final-approved` receipt. Its confirmation cannot precede that
final receipt's confirmation or creation. Publication authority cannot be
reused for another remote, release, deployment, installation, or distribution
target.
7. Start a new working change.

If a receipt must change, create a successor version. Do not rewrite a gated
receipt or dated bookmark.

## Recovery

Use Jujutsu's operation log and project receipts to identify the last consistent
state. Inspect before restoring. Record the chosen operation, reason, and hashes.
Recovery must not silently discard a user's manual manuscript edits.
