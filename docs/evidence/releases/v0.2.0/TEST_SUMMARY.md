# v0.2.0 test summary

[中文记录](TEST_SUMMARY.zh-CN.md)

Status: `CANDIDATE` — Local candidate test gates pass; CI and post-install regression pending publication.

## Local candidate validation results

| Suite / Gate | Command | Status | Result / Assertions |
| --- | --- | --- | --- |
| Pytest suite | `python3 -m pytest -q` | `PASS` | 309 passed |
| Unittest suite | `python3 -m unittest discover -s tests` | `PASS` | 27 tests (245 collection + 7 hook assertions) |
| Python compileall | `python3 -m compileall -q skills tests` | `PASS` | Clean (zero errors) |
| Git diff check | `git diff --check` | `PASS` | Clean (zero whitespace/diff errors) |
| Package-local: ask-light contract | `python3 skills/ask-light/tests/test_ask_light_contract.py` | `PASS` | Pass |
| Package-local: ask-light behavior | `python3 skills/ask-light/tests/test_ask_light_behavior.py` | `PASS` | Pass |
| Package-local: kb-init | `python3 skills/kb-init/tests/test_kb_init_contract.py` | `PASS` | Pass |
| Package-local: kanban-worker contract | `python3 skills/kanban-worker/tests/test_kanban_worker_contract.py` | `PASS` | Pass |
| Package-local: kanban-worker behavior | `python3 skills/kanban-worker/tests/test_kanban_worker_behavior.py` | `PASS` | Pass |
| Package-local: language-learning | `python3 skills/language-learning/tests/test_language_learning_contract.py` | `PASS` | Pass |
| Package-local: project-init | `python3 skills/project-init/tests/test_project_init_contract.py` | `PASS` | Pass |
| Package-local: project-review profiles | `python3 -m unittest discover -s skills/project-review/tests` | `PASS` | Pass |

## CI & Post-publication gates

| Gate | Status | Observed |
| --- | --- | --- |
| GitHub Actions `collection-quality` | `NOT TESTED` | Pending push to main |
| Post-install source tree regression | `NOT TESTED` | Pending fresh-install matrix execution |
