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
| collection discovery | `powershell -File tests/collection-discovery-tests.ps1` | `PASS` — 683 assertions, including Skill-guide, workflow, release-evidence, and bilingual semantic-pair parity. |
| header asset | `powershell -File tests/header-asset-tests.ps1` | `PASS` — 11 assertions; SVG/PNG dimensions, synchronized asset manifest, and layered wordmark markers. |
| Quick Start | `powershell -File tests/quick-start-smoke-tests.ps1` | `PASS` — 8 assertions. |
| Python syntax | `python -B -c "...ast.parse..."` | `PASS` — 12 Python files parsed without writing bytecode. |
| Python `compileall` | `python -m compileall -q skills tests` | `NOT PASSED locally` — the sandbox denied writes to existing protected `__pycache__` directories; the same command passed in GitHub Actions on merged release commit `c50f1ef`. |
| Tagged fresh install | `npx skills add LightDevCoder/skills#v0.1.1 ...` plus `npx skills list` | `PASS` — CLI `1.5.20`; whole collection listed 5 packages, per-Skill destination listed `review-loop`, and both source checkouts were absent. See [installation evidence](INSTALLATION_VERIFICATION.md). |
| Release-commit CI | GitHub Actions `collection-quality` | `PASS` — run `30189210521` on `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`. |

## Evidence class

Package tests demonstrate the exercised contract scenarios. Collection
discovery demonstrates cross-reference and metadata consistency. Fresh tagged
installation evidence is recorded separately; neither local package tests nor
CLI discovery proves independent acceptance or model-mediated runtime behavior.
