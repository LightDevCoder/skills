# v0.2.7 namespace producer evidence

- Acceptance source: `.scratch/light-skill-namespace/spec-revision-3.md`, Revision 3, SHA-256 `f64a5f266015961b362812b24148557aca57371ba6a6dc4b8bacb680e51b2ed4`.
- User decision: 2026-10-06, “我看了一下确实，应该发0.2.7”. Previous Revision 2 and its blocked acceptance remain historical.
- Fixed point: `97adf5f319b8800b6635057434dcb4aeda2ddecd`; published v0.2.6 retained.
- Scope: exactly twelve canonical name migrations; 24 retained identities, 36 packages; no aliases/global migration.

## Structural and source observations

`input.json` freezes all baseline identities and invocation/UI policy from the actual remote-main Git tree. `identity-policy-audit.json` compares all 36 policies and categories and twelve UI labels/default prompts against this baseline. All assertions pass; these are structural observations, not actual Host selection.

`baseline-preservation.json` compares all 224 tracked files in the travel package and published release directories against the baseline Git tree. Every byte is retained. No travel functionality is newly implemented by this migration.

## Behavioral checks

`python3 -m pytest -q skills/productivity/ask-light/tests/test_namespace_migration.py tests/test_manuscript_dependencies.py tests/test_functional_closure.py tests/test_release_integrity.py tests/test_external_boundary_guard.py`: 128 passed in 27.19 s. Includes old-only/mixed source fixtures, approval/ready-ticket routes, canonical optional dependencies, finite historical readers, exact frozen token amendment restoration and executable command-boundary negative cases.

The merged unchanged travel template passes `node --test tests/*.test.mjs` (80 assertions-bearing tests) in disposable `/private/tmp/light-namespace-travel-v027-20261006/site`, using the prior installed dependency directory. The generator `node --test skills/productivity/light-travelpage/scripts/tests/create.test.mjs` passes four tests. Logs remain beside that site. These are automated behaviors, not new browser/host/provider claims.

## Pending evidence

Full collection rerun passes 534 pytest tests (43.32 s) and 158 unittest tests (22.690 s). Compilation succeeds with `PYTHONPYCACHEPREFIX=/private/tmp/namespace-v027-pycache`; public documentation checks and `git diff --check` pass. The earlier merge-wide runs failed only on copied draft relative links (533 pytest and 157 unittest checks passed); those links and stale copied-version wording were repaired, then all checks rerun. Logs are `.scratch/light-skill-namespace/evidence/v027-{full-repaired,unittest-repaired,docs-repair}.log`. Exact candidate A8 CLI matrix and independent Standards/Spec/Evaluator review are pending. A2 actual Host selector and A9 actual invocation/dependency reads remain required. Prior initialization failures are retained under namespace-v0.2.6; the current Host diagnosis is separate. Remote CI/tag/pinned-source installation/Release/receipt are not completed. No release receipt exists for v0.2.7.
