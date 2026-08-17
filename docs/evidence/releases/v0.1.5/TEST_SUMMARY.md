# v0.1.5 test summary

[中文记录](TEST_SUMMARY.zh-CN.md)

## Status

`PASS` — local cross-platform Python suite on main at the v0.1.5 candidate
commit. Pre-release gate evidence; post-release CI is recorded on main after
the tag is published.

## Suites and counts

| Suite | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p "test_*.py"` | 12 tests OK |
| `light-kanban-worker` contract suite | PASS — 100 assertions |
| `light-kanban-worker` behavior suite | PASS — 23 assertions |
| Collection discovery suite | PASS — 1309 assertions |
| Package suites (ask-light contract; project-init contract + behavior; recap contract + output; language-learning contract; review-loop five-profile contract + behavior; protocol helpers) | PASS |
| `python3 -m compileall -q skills/learn-anything skills/manuscript-ops skills/light-kanban-worker/tests tests/test_collection_contract.py` | OK |
| Retired package boundary (project-workflow / to-manuscript-spec) | clean |
| No PowerShell test files remain | clean |
| ask-light scanner behavior (pwsh) | skipped locally (pwsh absent; CI runs it) |

## New worker coverage (v0.1.5)

- Contract rules: same-agent non-overlap (`must not overlap` / `must skip`),
  different-agent concurrency, atomic-claim-not-a-concurrency-lock boundary,
  scheduler ownership of concurrency (`max concurrent runs = 1`), no
  resident lock/heartbeat/lease service, first registration requires ID +
  name + avatar, existing-agent identity reuse, missing-identity
  no-mutation, and the local avatar upload path.
- Negative fixtures: `overlap-allowed-variant.md` (violates only the
  non-overlap rule) and `avatar-optional-first-registration.md` (violates
  only the first-registration avatar rule). Each must fail its target
  checker and pass the other five rule checkers; mutation negatives cover
  both rules on the real `SKILL.md`.
- Behavior scenarios:
  - Scenario G — same-agent concurrent wake, verified through the
    scheduler-guard fixture `scenario-g-scheduler-guard.md`: run #1 active →
    run #2 scheduled → must not start. The fixture records the verification
    boundary: Light-Kanban itself provides no run lease.
  - Scenario H — fresh identity without avatar, verified through
    `scenario-h-fresh-identity-no-avatar.md`: missing avatar → identity
    configuration missing → no claim, no mutation; a legal avatar →
    registration → claim succeeds.
  - Scenarios A–F remain unchanged and passing; live-server evidence in
    [behavioral-evidence.md](../../admissions/light-kanban-worker/behavioral-evidence.md).
