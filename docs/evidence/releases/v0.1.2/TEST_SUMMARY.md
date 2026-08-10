# v0.1.2 test summary

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
| language-learning | `powershell -File skills/language-learning/tests/language-learning-contract-tests.ps1` | `PASS` — 33 assertions. |
| recap | `powershell -File skills/recap/tests/recap-output-contract-tests.ps1` | `PASS` — 8 assertions. |
| learn-anything hooks | `python -m unittest discover -s tests -p "test*.py"` | `PASS` — 4 tests; 80 collection assertions and 7 learn-anything hook assertions. |
| manuscript-ops | `python skills/manuscript-ops/scripts/{assess_project,check_dependencies,validate_state}.py --help` | `PASS` — all three read-only CLI help checks returned successfully. |
| collection discovery | `powershell -File tests/collection-discovery-tests.ps1` | `PASS` — 1064 assertions, including Skill-guide, workflow, release-evidence, and bilingual semantic-pair parity. |
| header asset | `powershell -File tests/header-asset-tests.ps1` | `PASS` — 11 assertions; SVG/PNG dimensions, synchronized asset manifest, and layered wordmark markers. |
| Quick Start | `powershell -File tests/quick-start-smoke-tests.ps1` | `PASS` — 8 assertions. |
| Python syntax | `python -B -c "...ast.parse..."` | `PASS` — Python files parsed without writing bytecode. |
| Tagged fresh install | `npx skills add LightDevCoder/skills#v0.1.2 ...` plus `npx skills list` | `PASS` — CLI `1.5.22`; whole collection listed exactly 7 packages, per-Skill destination listed exactly `review-loop`, and no source checkout was present in any fresh destination. See [installation evidence](INSTALLATION_VERIFICATION.md). |
| Generic `latest` fresh install | `npx skills add LightDevCoder/skills ...` plus `npx skills list` | `PASS` — CLI `1.5.22`; whole collection listed exactly 7 packages, per-Skill destination listed exactly `review-loop`, and no source checkout was present in any fresh destination. See [installation evidence](INSTALLATION_VERIFICATION.md). |
| Release-commit CI | GitHub Actions `collection-quality` | `PASS` — run `31362999381` on `8de5ec1a453b0e93f71dcda160e17ea7b42c3997`. |

## Evidence class

Package tests demonstrate the exercised contract scenarios. Collection
discovery demonstrates cross-reference and metadata consistency. Fresh tagged
installation evidence is recorded separately; neither local package tests nor
CLI discovery proves independent acceptance or model-mediated runtime behavior.
