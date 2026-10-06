# Final artifacts and CI closeout

Use before pushing a candidate, a post-publication attestation or any repair
commit, and before reporting the release complete. Local checks, published
tag identity and the final main CI are separate evidence.

## Verify final artifacts

1. Finish generated files, copies, renames and raw-log archives. Update every
   link to the path that will actually be committed, including both receipt
   languages. Keep raw bytes intact; an archive may preserve logs whose
   terminal whitespace cannot pass repository checks.
2. Inspect all current release authorities: README, catalog, installation,
   maintenance and migration guidance. Their current stable/candidate state
   must agree. Preserve historical release snapshots and historical claims.
3. Stage the intended files and check `git diff --exit-code` so tests inspect
   the same tracked content as the index. Record
   `VERIFIED_TREE="$(git write-tree)"`, then run `git diff --cached --check`,
   full collection tests, compilation and public-doc checks from PREPARED.
   Also export the recorded tree to a fresh directory and run the existing
   collection-discovery checker there. Working-directory files can include
   untracked or ignored targets that will be absent from the commit:

   ```bash
   VERIFY_DIR="$(mktemp -d)"
   git archive --output="$VERIFY_DIR/tree.tar" "$VERIFIED_TREE"
   tar -xf "$VERIFY_DIR/tree.tar" -C "$VERIFY_DIR"
   (cd "$VERIFY_DIR" && python3 -m pytest -q tests/test_collection_discovery.py)
   ```

   Retain the result/tree identity, then clean the disposable snapshot with
   `trash`. This checker resolves final Markdown links, including receipts,
   against committed files. The tree export and checker must both succeed;
   a clean integrity result or a workspace-only test does not replace them.
4. Before committing, require no unstaged tracked changes and the same
   `git write-tree` value. After committing, require
   `git rev-parse HEAD^{tree}` to match `VERIFIED_TREE`. Later edits or path
   changes invalidate the affected checks: stage the final state and repeat
   verification before pushing. A hook changing the committed tree also
   requires verification of that new tree.

A passing run before an archive or link edit is not evidence for the files
pushed afterward. Stop before the push when any required check fails; perform
the smallest authorized repair and recheck. Keep test logs and staged-tree
identity in the local task record.

## Wait for the exact commit

After each push, record its full SHA and locate its required
`collection-quality` run, not merely the newest green run on the repository:

```bash
gh run list --commit <pushed-sha> --workflow collection-quality --json databaseId,headSha,status,conclusion --limit 1
gh run watch <run-id> --exit-status
gh run view <run-id> --json headSha,status,conclusion
```

Require matching `headSha`, `status: completed` and `conclusion: success`.
Queued, running, failed, cancelled, missing or unreadable results do not
complete the stage. Retry a transient read failure without inventing a CI
result. If CI fails, inspect its actual log, preserve the failed commit/run,
repair within the existing authorization, and repeat final-artifact checks
and CI on the new commit. Do not mark the old run successful or let an earlier
candidate success stand in for final attestation success.

The receipt records already observed publication facts. Store the final
attestation SHA/run externally in the local closeout record and final report;
adding a receipt's own commit SHA/run to itself creates another commit that
needs its own checks. If publication already occurred but attestation is not
verified, report that precise partial state and keep working within scope.

## Report the whole release

Report the version/tag and immutable candidate, actual installation/publication
results, and final main commit with its successful CI link. If an attempt
failed, also give its commit/run, cause, repair and the replacement success.
The user should learn about a failure and its resolution from the task, not
only from a GitHub email. Preserve the failed history and notification settings.

A GitHub file page can show the checks for that file's last modifying commit.
Compare that SHA with the current branch and its CI before calling it a current
failure. An old red badge may remain when a later repair touched another file;
explain the two identities. Do not rerun unchanged bad content, rewrite a tag,
skip checks or make a cosmetic commit to manufacture a green badge.

Completion requires correct finalized links and current stable docs, all local
checks, exact candidate CI, immutable remote tag, fresh actual-source installs,
public release/navigation, and exact final attestation CI. A successful push or
a published Release alone is not completion.
