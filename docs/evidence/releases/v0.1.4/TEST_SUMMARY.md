# v0.1.4 test summary

[中文记录](TEST_SUMMARY.zh-CN.md)

## Status

`PASS` — local cross-platform Python suite on main at the release commit.

## Suites and counts

| Suite | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p "test_*.py"` | 12 tests OK; `COLLECTION_PYTHON_ASSERTIONS=90`; `LEARN_ANYTHING_HOOK_ASSERTIONS=7` |
| Package suites (ask-light contract; project-init contract + behavior; recap contract + output; language-learning contract; light-kanban-worker contract + behavior; review-loop five-profile contract + behavior; protocol helpers) | 19 suites PASS |
| `python3 -m compileall -q skills/learn-anything skills/manuscript-ops skills/light-kanban-worker/tests tests/test_collection_contract.py` | OK |
| Retired package boundary (project-workflow / to-manuscript-spec) | clean |
| No PowerShell test files remain | clean |
| ask-light scanner behavior (pwsh) | PASS locally with PowerShell 7.4.6 — includes the cross-platform `Test-PathUnder` separator fix and the new outside-readable-path negative scenario (see [CODE_REVIEW.md](CODE_REVIEW.md)) |

## Package evidence

- `light-kanban-worker` contract suite: metadata, invocation type, required
  workflow sections, rule checkers, mutation negatives, and four adversarial
  single-rule fixture files.
- `light-kanban-worker` behavior suite: golden-flow ordering, review-feedback
  priority, one-task rule, human-only boundary, workspace block, no-daemon,
  failure semantics, API reference details.
- Admission: `review-loop agent-skill` `PASS` (see
  [admission evidence](../../admissions/light-kanban-worker/README.md)).
- Behavioral scenarios A–F against a real Light-Kanban server: all `PASS`
  (see [behavioral evidence](../../admissions/light-kanban-worker/behavioral-evidence.md)).
