# Repair Evidence - Round 1

Producer repairs for the confirmed findings F-001, F-002, F-003. Bounded
changes only; the frozen Charter and earlier evidence are unchanged.

## F-001 — candidate framing until the tag exists

- README.md / README.zh-CN.md: the Release block now says v0.1.5 "is the
  prepared release candidate — the pre-release gate is `READY FOR RELEASE`"
  and notes post-release verification is recorded on main.
- CATALOG.md / CATALOG.zh-CN.md: "Current state" now says "v0.1.5 release
  candidate (`READY FOR RELEASE`, tag pending)"; "Stable release" points to
  v0.1.4 with v0.1.5 as the prepared candidate.
- docs/INSTALLATION.md / INSTALLATION.zh-CN.md: v0.1.4 remains the current
  stable release; the v0.1.5 section is now "v0.1.5 candidate commands"
  with the pinned `#v0.1.5` form verified only after the tag is published.
- tests/test_collection_discovery.py and tests/test_collection_contract.py:
  expectations now assert the candidate framing ("release candidate") and
  the v0.1.5 candidate catalog state.
- Post-release commit (after the tag) will flip these to the published
  framing together with the finalized receipt.

## F-002 — intra-package version drift

- skills/light-kanban-worker/references/api.md line 4 now reads:
  "Compatible with Light-Kanban v1.0.4+; v0.1.5 adds no REST API
  requirement. The recommended integration version is Light-Kanban v1.0.6,
  which vendors the v0.1.5 snapshot." — identical claim to SKILL.md.
- Re-run the worker contract + behavior suites from source and from a fresh
  installed copy: both `OK` (behavioral, VS-1/VS-3).

## F-003 — gate row honesty

- RELEASE_RECEIPT.md / RELEASE_RECEIPT.zh-CN.md "Collection tests PASS"
  row now reads: "PASS — final green run on the candidate commit after the
  review-loop record files were written (see TEST_SUMMARY.md)".

## Verification

- `python3 skills/light-kanban-worker/tests/test_light_kanban_worker_contract.py` → OK (100 assertions)
- `python3 skills/light-kanban-worker/tests/test_light_kanban_worker_behavior.py` → OK (23 assertions)
- Fresh installed copy (`cp -R` to a new /tmp destination): both suites OK.
- Full collection suite: run after the review-record files exist (the
  AGENT_SKILL_REVIEW links must resolve); recorded in the final quality
  run attached to the candidate commit.

Remaining limitation: the published-tag `npx skills add` verification stays
post-release by Charter scope.
