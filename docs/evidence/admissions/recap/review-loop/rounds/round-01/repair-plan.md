# Repair Plan - Round 1

## F-001

Run the installed `code-review` capability with fixed point `origin/main` and
the frozen Charter as Spec source. Use separate read-only Standards and Spec
reviewers. Record their raw findings as `review` evidence; repair only a
confirmed script issue, if any.

## F-002

Change current-branch catalog/README/maintenance wording from final admission
to candidate/pending-review language. Preserve the six-package candidate tree
and five-package stable v0.1.1 boundary. Final admission wording is a closeout
step only after a `review-loop` `PASS`.

## Verification

Run focused recap tests, collection discovery, Python collection tests,
Markdown link checks, and a fresh round-2 Evaluator.

## Specialist additions

- F-003: rename the deterministic suite and PASS marker to output-contract terminology.
- F-004: make both suites fail when assertion count is zero.
- F-005: require prohibition-aware compaction/handoff language and add an opposite-polarity mutation fixture.
- F-008: reject generalized leading labels and add Status/Result/bold-label fixtures.
- F-009: assert the stable v0.1.1 five-package boundary in PowerShell and Python collection tests.
- F-006 and F-007: no Producer change; preserve the Core rejection rationale.
