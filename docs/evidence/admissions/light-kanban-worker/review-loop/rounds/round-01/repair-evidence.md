# Repair Evidence - Round 1

Confirmed in-scope repairs authorized by the Core for F-001, F-002, F-003.
Producer-only edits; no Charter change; no scope expansion.

## F-001 - canonical review-boundary assertion
- Files changed: `skills/light-kanban-worker/tests/worker_checks.py`
- Change: `human_only_review` now requires the full canonical sentence
  ("never archives … never accepts … never deletes … never recycles … never
  unblocks", whitespace-tolerant) AND keeps the bounded per-verb gates.
- Focused check: `python3 skills/light-kanban-worker/tests/test_light_kanban_worker_contract.py` → OK;
  the archive mutation (`never archives` → `archives the task when done`) is still rejected;
  `archive-variant.md` is still rejected.
- Evidence label: structural
- Remaining limitation: text-presence checks cannot prove runtime behavior;
  runtime behavior is covered by behavioral evidence E-005.

## F-002 - adversarial single-rule fixtures
- Files changed: all four files in `skills/light-kanban-worker/tests/fixtures/`;
  `skills/light-kanban-worker/tests/test_light_kanban_worker_contract.py`
- Change: every fixture is now a complete worker protocol document (identity,
  in-progress before todo, reviewFeedback priority, one-task rule, review
  boundary, no-work exit) that violates exactly its target rule; the contract
  suite asserts the target checker fails AND the other three rule checkers
  pass for each fixture (single-rule precision).
- Focused check: `python3 skills/light-kanban-worker/tests/test_light_kanban_worker_contract.py` → OK;
  `python3 skills/light-kanban-worker/tests/test_light_kanban_worker_behavior.py` → OK;
  full collection suite → OK (COLLECTION_PYTHON_ASSERTIONS=90).
- Evidence label: structural
- Remaining limitation: fixtures are static adversarial documents, not live
  runtime misuse; live misuse paths are bounded by SKILL.md rules and E-005.

## F-003 - legal identity sources
- Files changed: `skills/light-kanban-worker/SKILL.md` (Configuration section)
- Change: names the only legal agent-id sources (current invocation /
  scheduled task instruction, or `LIGHT_KANBAN_AGENT_ID`); a per-run invented
  id is a guessed identity and forbidden; missing id → report and end without
  touching tasks.
- Focused check: contract suite OK (required sections and metadata unchanged);
  behavior suite OK (golden-flow order unchanged).
- Evidence label: structural
- Remaining limitation: document-level rule; enforcement depends on the
  executing agent following SKILL.md.

## Re-run summary
- `python3 -m unittest discover -s tests -p "test_*.py"` → OK (12 tests)
- package suites → OK
- `python3 -m compileall -q skills/learn-anything skills/manuscript-ops skills/light-kanban-worker/tests tests/test_collection_contract.py` → OK
