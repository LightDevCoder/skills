# Test Summary — v0.1.3

Date: 2026-08-10. Environments: macOS 15 (local, Python 3.9) and GitHub
Actions `ubuntu-latest` (CI, Python 3.11). No PowerShell test files remain.

| Suite | Command | Local | CI |
| --- | --- | --- | --- |
| Collection discovery (incl. recap + language-learning composition) | `python3 -m unittest discover -s tests -p "test_*.py"` | PASS | PASS |
| Header assets | same discovery | PASS | PASS |
| Quick start smoke | same discovery | PASS | PASS |
| Collection contract (python) | same discovery | PASS | PASS |
| Learn-anything hooks (python) | same discovery | PASS | PASS |
| ask-light contract | `python3 skills/ask-light/tests/test_ask_light_contract.py` | PASS | PASS |
| ask-light behavior (real scanner via pwsh) | `python3 skills/ask-light/tests/test_ask_light_behavior.py` | SKIPPED (no pwsh) | PASS |
| project-init contract + behavior | `python3 skills/project-init/tests/test_project_init_*.py` | PASS | PASS |
| recap contract + output contract | `python3 skills/recap/tests/test_recap_*.py` | PASS | PASS |
| language-learning contract | `python3 skills/language-learning/tests/test_language_learning_contract.py` | PASS | PASS |
| review-loop ×5 profile contract + behavior | `python3 skills/review-loop/tests/test_*_profile_*.py` | PASS (10 suites) | PASS |
| compileall | `python3 -m compileall -q skills/learn-anything skills/manuscript-ops tests/test_collection_contract.py` | PASS | PASS |
| Retired package boundary | `grep -rn -E "project-workflow|to-manuscript-spec" skills/` | PASS (no hits) | PASS |
| No PowerShell test files | `find . -path "*/tests/*.ps1"` | PASS (0) | PASS |

Assertion counts preserved from the PowerShell suites: recap contract (14),
recap output contract (5), language-learning contract (33), collection
discovery (1064+), review-loop per-profile contract/behavior scenarios
unchanged.

Structural checks do not replace fresh installation, discovery, or manual
review evidence.
