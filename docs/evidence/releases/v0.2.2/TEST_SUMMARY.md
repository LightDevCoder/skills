# Test Summary — v0.2.2

[中文记录](TEST_SUMMARY.zh-CN.md)

## Automated Test Results

| Suite | Status | Details |
| --- | --- | --- |
| Pytest Collection Suite | `PASS` | 395 passed (hermetic environment without external companion repo: 394 passed, 1 skipped: `test_layer1_deterministic_schemas_via_companion_ajv` safely skipped) |
| Python Unittest Suite | `PASS` | 32 tests, 268 assertions passing (`COLLECTION_PYTHON_ASSERTIONS=268`, `LEARN_ANYTHING_HOOK_ASSERTIONS=7`) |
| Package Compilation | `PASS` | `python3 -m compileall -q skills tests` clean |
| Git Diff & Whitespace | `PASS` | `git diff --check` clean |
| Collection Contract | `PASS` | Exactly 36 admitted package directories verified across 7 categories |
| Collection Discovery | `PASS` | Dual-language documentation, links, and metadata synchronized |
| Package-Local Suites | `PASS` | `ask-light` (103), `agent-config` (61), `project-init` (64), `implement` (17), `review-loop` (19), `project-review` (20), `socratic` (18), `project-retro` (13), `generic-review` (8), `decision-map` (9), `clarify` (5), `project-clarify` (9), `integrated-workflow` (3) |
