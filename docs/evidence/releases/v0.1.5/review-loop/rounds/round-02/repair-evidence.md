# Repair Evidence - Round 2

Producer repair for the round-1 Evaluator finding G-001 (confirmed, in
scope, bounded).

## G-001 — residual pre-tag "published" claim

- README.md line 87: "The published v0.1.5 collection contains eight
  first-party packages" → "The v0.1.5 release candidate collection contains
  eight first-party packages".
- README.zh-CN.md line 66: "已发布的 v0.1.5 集合包含八个第一方包" →
  "v0.1.5 release candidate 集合包含八个第一方包".
- Gate hardening (per the Evaluator's recommendation):
  tests/test_collection_discovery.py now also asserts the README does NOT
  contain "published v0.1.5" before the tag exists.
- Full quality re-run: 12 discovery tests OK (92 + 7 assertions), all
  package suites OK — green on the repaired tree.

Note: the post-release commit (after the tag) flips README/CATALOG/
INSTALLATION and this discovery expectation to the published framing
together with the finalized receipt.
