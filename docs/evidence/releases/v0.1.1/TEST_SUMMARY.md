# v0.1.1 test summary

[中文摘要](TEST_SUMMARY.zh-CN.md)

This file records real commands and assertion counts. A command not yet run is
marked `NOT TESTED`; a zero-assertion or source-only scan is not a pass.

## Current results

| Area | Command | Result |
| --- | --- | --- |
| ask-light contract | `powershell -File skills/ask-light/tests/ask-light-contract-tests.ps1` | `PASS` — zero failures; this script reports a pass marker but does not emit a numeric count. |
| ask-light behavior | `powershell -File skills/ask-light/tests/ask-light-behavior-tests.ps1` | `PASS` — 52 assertions in local branch run, including duplicate source-category, complete workflow context, invalid availability/invocation-control context, and workflow read-count fixtures. |
| project-init | package contract and behavior scripts | `PASS` — contract and behavior suites passed; scripts do not emit a numeric count. |
| review-loop Profiles | all contract/behavior scripts under `skills/review-loop/tests/` | `PASS` — 5 contract suites and 105 behavior assertions across Agent-Skill, generic, manuscript, software, and specification profiles. |
| learn-anything hooks | `python -m unittest discover -s tests -p "test*.py"` | `PASS` — 4 tests; 54 collection assertions and 7 learn-anything hook assertions. |
| manuscript-ops | `python skills/manuscript-ops/scripts/{assess_project,check_dependencies,validate_state}.py --help` | `PASS` — all three read-only CLI help checks returned successfully. |
| collection discovery | `powershell -File tests/collection-discovery-tests.ps1` | `PASS` — 668 assertions, including Skill-guide, workflow, release-evidence, and bilingual semantic-pair parity. |
| header asset | `powershell -File tests/header-asset-tests.ps1` | `PASS` — 11 assertions; SVG/PNG dimensions, synchronized asset manifest, and layered wordmark markers. |
| Quick Start | `powershell -File tests/quick-start-smoke-tests.ps1` | `PASS` — 8 assertions. |
| Python syntax | `python -B -c "...ast.parse..."` | `PASS` — 12 Python files parsed without writing bytecode. |
| Python `compileall` | `python -m compileall -q skills tests` | `NOT TESTED` as a bytecode-write proof — the sandbox denied writes to existing protected `__pycache__` directories; the read-only AST check above passed. |

## Evidence class

Package tests demonstrate the exercised contract scenarios. Collection
discovery demonstrates cross-reference and metadata consistency. Neither one
proves a fresh host installation or independent acceptance.
